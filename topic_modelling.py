import pandas as pd
import re
from nltk.corpus import stopwords
from nltk import word_tokenize, pos_tag
from nltk.stem.porter import *
from gensim import matutils, models
import pickle

def get_url_regex(): # https://stackoverflow.com/questions/11331982/how-to-remove-any-url-within-a-string-in-python/11332580
    regex = r'('
    # Scheme (HTTP, HTTPS, FTP and SFTP):
    regex += r'(?:(https?|s?ftp):\/\/)?'
    # www:
    regex += r'(?:www\.)?'
    regex += r'('
    # Host and domain (including ccSLD):
    regex += r'(?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\.)+)'
    # TLD:
    regex += r'([A-Z]{2,6})'
    # IP Address:
    regex += r'|(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    regex += r')'
    # Port:
    regex += r'(?::(\d{1,5}))?'
    # Query path:
    regex += r'(?:(\/\S+)*)'
    regex += r')'

    return regex

def remove_urls(text):
    regex = get_url_regex()
    find_urls = re.compile(regex, re.IGNORECASE)

    found_urls = [f[0] for f in find_urls.findall(text)]
    
    for url in found_urls:
        text = text.replace(url, '')

    return text
    
def is_noun_or_adj(pos):
    return pos[:2] == 'NN' or pos[:2] == 'JJ'

def process_text(text):

    # Remove urls
    text = remove_urls(text)

    # Tokenization
    tokenized = word_tokenize(text)

    # Stop words
    stop_words = stopwords.words('english')
    stop_words.extend(['https', 'http', 'www'])

    # Removing stop words and keeping adj and nouns
    nouns_adj = [word for (word, pos) in pos_tag(tokenized) if is_noun_or_adj(pos) and word not in stop_words]

    # Stemming
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(token) for token in nouns_adj]

    return ' '.join(stemmed_tokens)

# MAIN
if __name__ == "__main__":

    res = process_text('This is a test for my topic modelling programme and i am very excited about it redd.it and google.es ')
    print(res)