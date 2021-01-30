# -*- coding: utf-8 -*-

import string
import nltk
from nltk.corpus import stopwords


class WordFreq:
    STOPWORDS = set(stopwords.words('english'))
    def __init__(self, file):
        self.file = file

    def __isEnglish(self, s):
        try:
            s.encode(encoding='utf-8').decode('ascii')
        except UnicodeDecodeError:
            return False
        else:
            return True

    # it runs in linear time relative to the number of characters in the input file: O(n)

    def tokenize(self):
        lst = []
        for line in self.file.splitlines():
        #for line in self.file:
            for word in line.rstrip().lower().split(" "):
                word = word.strip(string.punctuation)
                new_word = ''
                for c in word:
                    if self.__isEnglish(c):
                        new_word = new_word + c
                if new_word != "":
                    lst.append(new_word)
        return lst

def filter_stop(token_list):
    return [w for w in token_list if not w in WordFreq.STOPWORDS]



