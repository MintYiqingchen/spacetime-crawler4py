import os
import shelve
import sys
import re
from utils.word_freq import filter_stop
from collections import Counter
from urllib.parse import urlparse

if __name__ == '__main__':
    filename = sys.argv[1]
    counter = Counter()
    subdomainCounter = Counter()
    longestPair = (None, -1)
    with shelve.open(filename) as save:
        print("----------------UNIQUE URLS---------------")
        print(len(save))
        for url, wordTuple in save.values():
            a = len(wordTuple)
            if a > longestPair[1]:
                longestPair = (url, a)
            counter.update(wordTuple)

            parsed = urlparse(url)
            if re.match(r".+\.ics.uci.edu", parsed.netloc):
                subdomainCounter[parsed.scheme + '://' + parsed.netloc] += 1
    
    print("----------------LONGEST---------------")
    print(longestPair[0], ' ', longestPair[1])
    print("----------------MOST COMMON---------------")
    for w, c in counter.most_common(50):
        print(w, ' ', c)
    print("----------------SUBDOMAIN---------------")
    keys = sorted(subdomainCounter.keys())
    for k in keys:
        print(k, ' ', subdomainCounter[k])