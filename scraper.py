import re
from urllib.parse import urlparse
import pickle
from bs4 import BeautifulSoup
from utils.word_freq import WordFreq, filter_stop
from utils import UrlInfo

import logging
def scraper(url, resp):
    if resp.status >= 600:
        logging.getLogger('CRAWLER').error(f'{resp.error}: {url}')
        return list(), UrlInfo(url, True), None
    if resp.raw_response is None:
        return list(), UrlInfo(url, True), None

    html = resp.raw_response.text
    soup = BeautifulSoup(html, 'html.parser')
    # remove style and script
    for tag in soup.find_all(['style', 'script']):
        tag.decompose()

    links = extract_next_links(url, soup)

    if soup.body:
        pure_content = soup.text
        token_list = extract_word_freq(pure_content)
    else:
        return links, UrlInfo(url, True), None
        
    return links, UrlInfo(url, True, len(token_list)), token_list


def extract_next_links(url, soup):
    atags = soup.find_all(href=is_valid, rel=lambda x: (x is None or x != 'nofollow'))
    return [a.get('href') for a in atags]    

def extract_word_freq(pure_content):
    parsed_content = WordFreq(pure_content)
    # tokenize
    token_lst = parsed_content.tokenize()
    return filter_stop(token_lst)

def is_valid(url):
    if url is None:
        return False
    # * *.ics.uci.edu/*
    # *.cs.uci.edu/*
    # *.informatics.uci.edu/*
    # *.stat.uci.edu/*
    # today.uci.edu/department/information_computer_sciences/*
    # if not re.match(r"(.*\.(ics|cs|informatics|stat).uci.edu|today.uci.edu/department/information_computer_sciences)(\/.*)?", url):
    #     return False

    try:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or parsed.netloc.find('://') != -1:
            return False
        if not re.match(r'.*\.(ics|cs|informatics|stat).uci.edu$|today.uci.edu$', parsed.netloc):
            return False
        if parsed.netloc == 'today.uci.edu' and not re.match(r'\/*department/information_computer_sciences(\/.*)?', parsed.path):
            return False
        # special rules for trash pages:
        if parsed.path.find('wp-json') != -1: # example: https://ngs.ics.uci.edu/wp-json/wp/v2/posts/1234
            return False
        # example: https://wics.ics.uci.edu/events/category/wics-meeting-2/2016-09-30/
        if parsed.query.find('ical') != -1 or (parsed.netloc == 'wics.ics.uci.edu' and parsed.path.find('event') != -1):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|xml|json"
            + r"|thmx|mso|arff|rtf|jar|csv|embed|ppsx"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise