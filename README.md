# proxycheck
Test HTTP(S) proxies for their utility and latency

## Quickstart
~~~~
% python proxycheck.py
usage: proxycheck.py [-h] [-l {WARNING,INFO,DEBUG}] [-t THREADS] [-u TESTURL]                                                        
                     [-s TIMEOUT] [-r REPEATS]
                     proxy_list
proxycheck.py: error: the following arguments are required: proxy_list

% python proxycheck.py proxylist
INFO:root:Testing using url: https://www.akamai.com/robots.txt
INFO:root:stdout is a terminal, suppressing CSV output
INFO:root:<  207.154.244.19:3128  > is not responding
INFO:root:<   188.244.5.229:3128  > is not responding
INFO:root:< 195.201.129.209:3128  > is not responding
INFO:root:< 195.201.129.209:3128  > is not responding
INFO:root:<   60.248.220.22:1080  > is not responding
INFO:root:<    91.82.85.154:3128  > has a latency of    19.27 ms (±   10.83 ms)
INFO:root:<     167.99.42.6:8080  > has a latency of    20.19 ms (±    0.92 ms)
INFO:root:<    176.9.40.189:3128  > has a latency of    24.89 ms (±    0.47 ms)
INFO:root:< 178.238.228.187:9090  > has a latency of    22.00 ms (±    1.01 ms)
INFO:root:<  80.211.135.118:3128  > is not responding
INFO:root:<    51.254.45.80:3128  > has a latency of    29.92 ms (±    0.42 ms)
INFO:root:<   87.98.174.157:3128  > has a latency of    32.33 ms (±    0.41 ms)
INFO:root:<  212.237.57.154:3128  > is not responding
INFO:root:<  80.211.228.238:8888  > has a latency of    38.90 ms (±    1.24 ms)
INFO:root:<   81.177.23.240:8888  > is not responding
INFO:root:<  212.237.26.124:8888  > has a latency of    37.52 ms (±    0.83 ms)
~~~~

## F.A.Q.
### How to save the output in CSV format?
To save the output in CSV, simply redirect the stdout stream to a file.
For example run: `% python proxycheck.py proxylist > output.csv`
