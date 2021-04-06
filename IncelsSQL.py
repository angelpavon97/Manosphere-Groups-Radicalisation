import mysql.connector
from config import config # Dictionary with mysql config
import tldextract
import re
from urllib.parse import urlparse, unquote
import os
from pathlib import PurePosixPath
import numpy as np

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

    def __process_domain(self, domain, path = None):

        if path != None:
            if len(path) >= 2:
                    domain += '/' + path[1]
            if len(path) >= 3:
                domain += '/' + path[2]
            if len(path) >= 4:
                domain += '/' + path[3]

        domain = self.__process_text(domain)
        
        if domain[-1] == ')':
            domain = domain[:-1]
        if domain[-2] == ')':
            domain = domain[:-2]
        
        return domain

    def __process_text(self, text):

        text = text.lower()
        
        if 'redd' in text:
            text = text.replace('redd.it', 'reddit.com')
            text = text.replace('np.reddit', 'reddit')

        if 'youtu' in text:
            text = text.replace('youtu.be', 'youtube.com')

        return text

    def close_connection(self):
        self.cnx.close()

    def get_comments(self):
        cursor = self.cnx.cursor()

        query = ("SELECT * FROM comments")

        cursor.execute(query)

        comments = []

        for comment in cursor:
            c_id, c_auto_id, c_auto_link_id, c_link_id, c_body, c_parent_id, c_author, c_date = comment[:8]
            print('----->',comment[:8])
            #comments.append(body[0].decode('UTF-8'))

        return comments

    def get_body_comments(self):
        cursor = self.cnx.cursor()

        query = ("SELECT body FROM comments")

        cursor.execute(query)

        comments = []

        for body in cursor:
            comments.append(body[0].decode('UTF-8'))

        return comments

    def get_text_links(self):
        cursor = self.cnx.cursor()

        query = ("SELECT self_text FROM links")

        cursor.execute(query)

        t_list = []

        for text in cursor:
            if text[0] != None:
                t_list.append(text[0].decode('UTF-8'))

        return t_list

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


    def get_urls_from_links(self):
        cursor = self.cnx.cursor()
        query = ("SELECT self_text FROM links")
        cursor.execute(query)

        urls = []

        regex = self.__get_url_regex()
        find_urls = re.compile(regex, re.IGNORECASE)

        for l in cursor:
            if l[0] != None:
                text = l[0].decode('UTF-8')

                found_urls = find_urls.findall(text)

                for url in found_urls:
                    urls.append(url[0])

        return urls

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

    def get_domains(self, urls):

        unique_urls = {}

        for url in urls:
            ext = tldextract.extract(url)

            if ext.subdomain != '' and ext.subdomain != 'www':
                domain = ext.subdomain + '.' + ext.domain + '.' + ext.suffix
            else:
                domain = ext.domain + '.' + ext.suffix

            domain = self.__process_domain(domain)

            if domain in unique_urls:
                unique_urls[domain] += 1
            else:
                unique_urls[domain] = 1

        return dict(sorted(unique_urls.items(), key=lambda item: item[1], reverse=True))
    

    def get_domains_path(self, urls):

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

    def exists_table(self, t_name):

        cursor = self.cnx.cursor()
        cursor.execute("SHOW TABLES")

        return t_name in [t[0] for t in cursor]

    def save_urls(self, unique_urls, t_name = 'unique_urls'):

        cursor = self.cnx.cursor()

        if self.exists_table(t_name):
            query = "DROP TABLE IF EXISTS " + t_name
            cursor.execute(query) 

        # Create table
        query = ("CREATE TABLE " + t_name + " (id INT AUTO_INCREMENT PRIMARY KEY, url VARCHAR(700), n_occurrences INT DEFAULT 0, n_comments INT DEFAULT 0)")
        cursor.execute(query)

        for url, count in unique_urls.items():

            if count >= 5:
                query = "INSERT INTO " + t_name + " (url, n_occurrences) VALUES (%s, %s)"
                values = (url, count)
                cursor.execute(query, values)

                self.cnx.commit()

        print('All urls saved')

    def get_unique_urls_from_links(self, n_occurrences = 0, return_id = False):
        cursor = self.cnx.cursor()

        if return_id == False:
            query = ("SELECT url FROM unique_urls_from_links WHERE n_occurrences > " + str(n_occurrences))
            cursor.execute(query)
            return [url[0] for url in cursor]
        else:
            query = ("SELECT id, url FROM unique_urls_from_links  WHERE n_occurrences > " + str(n_occurrences))
            cursor.execute(query)
            return {u[0]:u[1] for u in cursor}

    def get_unique_urls_from_comments(self, n_occurrences = 0):
        cursor = self.cnx.cursor()

        query = ("SELECT url FROM unique_urls_from_comments WHERE n_occurrences > " + str(n_occurrences))
        cursor.execute(query)

        return [url[0] for url in cursor]

    # Creates a many-to-many table that links unique_urls_from_links with links 
    def save_links_ids_with_url(self, t_name = 'urls_links_ids'):

        cursor = self.cnx.cursor()

        if self.exists_table(t_name):
            query = "DROP TABLE IF EXISTS " + t_name
            cursor.execute(query)

        query = ("SELECT id, url FROM unique_urls_from_links")
        cursor.execute(query)
        unique_urls = {u[0]:u[1] for u in cursor}

        query = ("SELECT id, self_text FROM links")
        cursor.execute(query)
        links = {l[0]:l[1] for l in cursor}

        query = "CREATE TABLE " + t_name + " (url_from_links_id INT, link_id VARCHAR(20))"
        cursor.execute(query)

        for url_id, unique_url in unique_urls.items():
            for link_id, link_body in links.items():

                if link_body != None and unique_url in self.__process_text(str(link_body)):
                    query = ("INSERT INTO " + t_name + " (url_from_links_id, link_id) VALUES (%s, %s)")
                    values = (url_id, link_id)
                    cursor.execute(query, values)

                    self.cnx.commit()
                    
        print('Table ' + t_name + ' created successfully.')

    def get_links_ids_with_url(self, u_id):

        cursor = self.cnx.cursor()

        query = ("SELECT link_id FROM urls_links_ids WHERE url_from_links_id = %s")
        values = (u_id,)
        cursor.execute(query, values)

        link_ids = [l_id[0] for l_id in cursor]
        
        return link_ids

    def get_comments_from_link(self, id):

        cursor = self.cnx.cursor()

        query = ("SELECT body FROM comments WHERE link_id = %s") # high computational time (5-10 secs)
        values = (id,)
        cursor.execute(query, values)

        comments = [c[0].decode('UTF-8') for c in cursor]
     
        return comments

    def get_n_comments_from_link(self, id):
        cursor = self.cnx.cursor()

        query = ("SELECT COUNT(*) FROM comments WHERE link_id = %s")
        values = (id,)
        cursor.execute(query, values)
     
        return sum([c[0] for c in cursor])

    def update_n_comments(self, u_id, n_comments):
        cursor = self.cnx.cursor()

        query = ("UPDATE unique_urls_from_links SET n_comments = %s WHERE id = %s")
        values = (n_comments, u_id)

        cursor.execute(query, values)
        self.cnx.commit()

    def save_number_comments(self): # Save the n_comments in unique_urls_from_links

        cursor = self.cnx.cursor()

        unique_urls = self.get_unique_urls_from_links(n_occurrences=0, return_id=True)
        unique_urls = {k: v for k, v in sorted(unique_urls.items(), key=lambda item: item[0], reverse=True)}

        for u_id, url in unique_urls.items():
            ids = self.get_links_ids_with_url(u_id)

            n_comments = 0

            for count, i in enumerate(ids):
                print('\t', count+1, '/', len(ids))
                n_comments += self.get_n_comments_from_link(i)

            print('\turl id: ', u_id, ' url: ', url, ' Number of comments: ', n_comments)
            self.update_n_comments(u_id, n_comments)


    def get_most_commented_urls(self):
        cursor = self.cnx.cursor()

        query = ("SELECT url, n_comments FROM unique_urls_from_links")
        cursor.execute(query)
        most_commented_urls = {c[0]:c[1] for c in cursor}
        return dict(sorted(most_commented_urls.items(), key=lambda item: item[1], reverse=True))