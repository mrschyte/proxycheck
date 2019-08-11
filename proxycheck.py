import argparse
import hashlib
import logging
import requests
import socket
import statistics
import sys
import threading
import timeit

from queue import Queue

class ProxyModifiesResponse(Exception):
    pass

class ProxyNotResponding(Exception):
    pass

class Worker(threading.Thread):
    proxy_types = ['http', 'socks5']

    def __init__(self, queue, testurl, urlhash, timeout, repeats):
        threading.Thread.__init__(self)
        self.queue = queue
        self.testurl = testurl
        self.urlhash = urlhash
        self.timeout = timeout
        self.repeats = repeats

    def make_proxy(self, proxy_type, host, port):
        proxy = {'http': '%s://%s:%d' %(proxy_type, host, port)}
        proxy['https'] = proxy['http']
        return proxy

    def identify(self, host, port):
        for proxy_type in self.proxy_types:
            proxy = self.make_proxy(proxy_type, host, port)
            try:
                self.check(proxy)
                return proxy_type
            except ProxyNotResponding:
                pass
        raise ProxyNotResponding()

    def check(self, proxy):
        try:
            response = requests.get(self.testurl, proxies=proxy, timeout=self.timeout)
            response.raise_for_status()
            return hashlib.md5(response.content).digest() == self.urlhash
        except Exception as ex:
            raise ProxyNotResponding()

    def evalproxy(self, host, port):
        proxy_type = self.identify(host, port)
        proxy = self.make_proxy(proxy_type, host, port)

        if self.check(proxy):
            samples = timeit.repeat(lambda: self.check(proxy), number=1, repeat=self.repeats)

            return (proxy_type,
                    100.0 * statistics.mean(samples),
                    100.0 * statistics.stdev(samples))
        else:
            raise ProxyModifiesResponse()

    def run(self):
        while True:
            host, port = self.queue.get()

            try:
                host = str(socket.gethostbyname(host))
                port = int(port)

                result = self.evalproxy(host, port)
                logging.info('< %15s:%-5d,%8s > has a latency of %8.2f ms (±%8.2f ms)' \
                             %(host, port, result[0], result[1], result[2]))
                if not sys.stdout.isatty():
                    print('%s,%d,%s,%f,%f' %(host, port, result[0], result[1], result[2]))
                    sys.stdout.flush()
            except ProxyModifiesResponse:
                logging.warning('< %15s:%-5d > is modifying response' %(host, port))
            except ProxyNotResponding:
                logging.info('< %15s:%-5d > is not responding' %(host, port))
            except socket.gaierror:
                logging.warning('unable to resolve host < %s >' %(host))
            self.queue.task_done()

def slurp(path):
    with open(path, 'r') as fp:
        return (line.rstrip() for line in fp.readlines())

def main(arguments):
    queue = Queue()

    for idx, line in enumerate(slurp(arguments.proxy_list)):
        try:
            host, port = line.split(':')
            queue.put((host, int(port)))
        except ValueError as ex:
            logging.warning('error parsing line %d (%s), ignoring.' %(idx, line))

    for k in range(arguments.threads):
        thread = Worker(queue, arguments.testurl, arguments.urlhash,
                        arguments.timeout, arguments.repeats)
        thread.setDaemon(True)
        thread.start()

    queue.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test HTTP proxies for their utility and latency')
    parser.add_argument('-l', '--loglevel', default='INFO', choices=['WARNING', 'INFO', 'DEBUG'],
                        help='logging level to use')
    parser.add_argument('-t', '--threads', default=10, type=int,
                        help='number of threads to use')
    parser.add_argument('-u', '--testurl', default='https://www.akamai.com/robots.txt', type=str,
                        help='test url for latency measurement')
    parser.add_argument('-s', '--timeout', default=5, type=int,
                        help='number of seconds to wait before timeout')
    parser.add_argument('-r', '--repeats', default=3, type=int,
                        help='number of times to repeat measurement')
    parser.add_argument('proxy_list', type=str,
                        help='proxies to test in IP:PORT format')
    arguments = parser.parse_args()

    logging.basicConfig(level=arguments.loglevel)

    arguments.urlhash = hashlib.md5(
        requests.get(arguments.testurl).content
    ).digest()

    logging.info('Testing using url: %s' %(arguments.testurl))
    if sys.stdout.isatty():
        logging.info('stdout is a terminal, suppressing CSV output')
    else:
        print('host,port,type,mean,stdev')
        sys.stdout.flush()
    main(arguments)
