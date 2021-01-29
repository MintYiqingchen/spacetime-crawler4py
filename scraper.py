import re
from urllib.parse import urlparse
import pickle
from bs4 import BeautifulSoup
from utils.word_freq import WordFreq
from utils import UrlInfo

# TODO: How many subdomains did you find in the ics.uci.edu domain?
def scraper(url, resp):
    if resp.raw_response is None:
        return list(), UrlInfo(url, True), None
    html = resp.raw_response.text
    soup = BeautifulSoup(html, 'html.parser')
    links = extract_next_links(url, soup)

    pure_content = soup.text
    token_list = extract_word_freq(pure_content)

    return links, UrlInfo(url, True, len(token_list)), token_list


def extract_next_links(url, soup):
    atags = soup.find_all(href=is_valid)
    return [a.get('href') for a in atags]    

def extract_word_freq(pure_content):
    parsed_content = WordFreq(pure_content)
    # tokenize
    token_lst = parsed_content.tokenize()
    return token_lst

def is_valid(url):
    if url is None:
        return False
    # * *.ics.uci.edu/*
    # *.cs.uci.edu/*
    # *.informatics.uci.edu/*
    # *.stat.uci.edu/*
    # today.uci.edu/department/information_computer_sciences/*
    if re.match(r"(.*\.(ics|cs|informatics|stat).uci.edu|today.uci.edu/department/information_computer_sciences)(\/.*)?", url):
        return True
    else: 
        return False

    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise