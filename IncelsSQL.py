import mysql.connector
from config import config # Dictionary with mysql config
import tldextract
import re
from urllib.parse import urlparse, unquote
import os
from pathlib import PurePosixPath

class IncelsSQL:
    def __init__(self):
        self.cnx = mysql.connector.connect(**config)

    def __get_url_regex(self): # https://stackoverflow.com/questions/9760588/how-do-you-extract-a-url-from-a-string-using-python
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

    def __process_domain(self, domain, path):

        if len(path) >= 2:
                domain += '/' + path[1]

        if len(path) >= 3:
            domain += '/' + path[2]

        if len(path) >= 4:
            domain += '/' + path[3]

        domain = domain.lower()
        
        if 'redd' in domain:
            domain = domain.replace('redd.it', 'reddit.com')
            domain = domain.replace('np.reddit', 'reddit')

        if domain[-1] == ')':
            domain = domain[:-1]
        if domain[-2] == ')':
            domain = domain[:-2]
        
        return domain

    def close_connection(self):
        self.cnx.close()

    def get_comments(self):
        cursor = self.cnx.cursor()

        query = ("SELECT body FROM comments")

        cursor.execute(query)

        comments = []

        for body in cursor:
            comments.append(body[0].decode('UTF-8'))

        return comments

    def get_urls_statistics(self):
        cursor = self.cnx.cursor()

        query = ("SELECT url FROM url_statistics")

        cursor.execute(query)

        urls = []

        for url in cursor:
            urls.append(url[0])

        return urls

    def get_url_root(self): # Dont use this table
        cursor = self.cnx.cursor()

        query = ("SELECT url FROM url_statistics")

        cursor.execute(query)

        urls = {}

        for url in cursor:
            url = url[0]
            ext = tldextract.extract(url)
            
            if ext.subdomain != '' and ext.subdomain != 'www':
                domain = ext.subdomain + '.' + ext.domain
            else:
                domain = ext.domain

            if domain in urls:
                urls[domain] += 1
            else:
                urls[domain] = 1

        return dict(sorted(urls.items(), key=lambda item: item[1], reverse=True))


    def get_urls_from_comments(self):
        cursor = self.cnx.cursor()
        query = ("SELECT body FROM comments")
        cursor.execute(query)

        urls = []

        regex = self.__get_url_regex()
        find_urls = re.compile(regex, re.IGNORECASE)

        for body in cursor:
            comment = body[0].decode('UTF-8')

            found_urls = find_urls.findall(comment)

            for url in found_urls:
                urls.append(url[0])

        return urls

    def get_domains_from_comments(self, urls):

        unique_urls = {}

        for url in urls:
            ext = tldextract.extract(url)

            if ext.subdomain != '' and ext.subdomain != 'www':
                domain = ext.subdomain + '.' + ext.domain
            else:
                domain = ext.domain

            if domain in unique_urls:
                unique_urls[domain] += 1
            else:
                unique_urls[domain] = 1

        return dict(sorted(unique_urls.items(), key=lambda item: item[1], reverse=True))
    

    def get_domains_path_from_comments(self, urls):

        unique_urls = {}

        for url in urls:
            ext = tldextract.extract(url)

            if ext.subdomain != '' and ext.subdomain != 'www':
                domain = ext.subdomain + '.' + ext.domain + '.' + ext.suffix
            else:
                domain = ext.domain + '.' + ext.suffix

            path = PurePosixPath(unquote(urlparse(url).path)).parts

            domain = self.__process_domain(domain, path)

            if domain in unique_urls:
                unique_urls[domain] += 1
            else:
                unique_urls[domain] = 1

        return dict(sorted(unique_urls.items(), key=lambda item: item[1], reverse=True))
         