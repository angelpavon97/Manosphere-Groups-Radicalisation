from IncelsSQL import IncelsSQL
from random import randint
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import numpy as np

def reduce_dictionary(dictionary, min = 200, max = 400):
    return {k:dictionary[k] for k in dictionary if dictionary[k] > min and dictionary[k] <= max}

def plot_dictionary(dictionary, min, max):
    d = reduce_dictionary(dictionary, min, max)

    plt.bar(range(len(d)), list(d.values()), align='center', color = 'green')
    plt.xticks(range(len(d)), list(d.keys()), rotation='vertical')
    plt.show()

def process_comment(c):
    c = c.lower()
        
    if 'redd' in c:
        c = c.replace('redd.it', 'reddit.com')
        c = c.replace('np.reddit', 'reddit')

    if 'youtu' in c:
        c = c.replace('youtu.be', 'youtube.com')

    return c

def get_comments_with_url(url, comments):
    return [c for c in comments if url in process_comment(c)]

def plot_word_cloud(text, file_name='word_cloud', folder='comments'):
    file_name = file_name.replace('/', '_').replace('.', '_') + '.png'

    stopwords = set(STOPWORDS)
    stopwords.update(['https', 'http', 'www'])

    wordcloud = WordCloud(width=800, height=400, stopwords=stopwords, background_color='white').generate(text)
    wordcloud.to_file('img/word_clouds/' + folder + '/' + file_name)

    # plt.imshow(wordcloud, interpolation='bilinear')
    # plt.axis("off")
    # plt.show()

    return

def save_unique_urls_comments(connection):
    
    urls = connection.get_urls_from_comments()
    unique_urls = connection.get_domains_path(urls)

    # plot_dictionary(unique_urls, 1000, 1000000)
    # plot_dictionary(unique_urls, 400, 1000)
    # plot_dictionary(unique_urls, 200, 400)
    # plot_dictionary(unique_urls, 100, 200)

    connection.save_urls(unique_urls, t_name='unique_urls_from_comments')

def save_unique_urls_links(connection):
    
    urls = connection.get_urls_from_links()
    unique_urls = connection.get_domains(urls)

    # plot_dictionary(unique_urls, 50, 1000000)

    connection.save_urls(unique_urls, t_name='unique_urls_from_links')

def get_word_clouds_comments(connection):
    urls = connection.get_unique_urls_from_comments(n_occurrences=100)
    comments = connection.get_body_comments()

    for u in urls:
        comments_with_url = get_comments_with_url(u, comments)

        if len(comments_with_url) == 0:
            print('url defectuosa: ', u)
        else:
            plot_word_cloud(' '.join(comments_with_url), u)

def get_word_clouds_links(connection):

    urls = connection.get_unique_urls_from_links(n_occurrences=50)
    text_links = connection.get_text_links()

    for u in urls:
        comments_with_url = get_comments_with_url(u, text_links)

        if len(comments_with_url) == 0:
            print('url defectuosa: ', u)
        else:
            plot_word_cloud(' '.join(comments_with_url), u, folder='links')

def get_word_clouds_links_comments(connection):

    unique_urls = connection.get_unique_urls_from_links(n_occurrences=20, return_id=True)
    unique_urls = {k: v for k, v in sorted(unique_urls.items(), key=lambda item: item[0], reverse=True)}
    print(unique_urls)

    for u_id, url in unique_urls.items():
        ids = connection.get_links_ids_with_url(u_id)
        comments = []

        print(u_id, url)
        for count, i in enumerate(ids):
            print('\t', count+1, '/', len(ids))
            comments = comments + connection.get_comments_from_link(i)

        print('\turl id: ', u_id, ' url: ', url, ' Number of comments: ', len(comments))

        if(len(comments) > 0):
            plot_word_cloud(' '.join(comments), url, folder='links_comments')

# MAIN
if __name__ == "__main__":
    connection = IncelsSQL()

    print('Saving unique urls from comments...')
    save_unique_urls_comments(connection)
    print('Saving unique urls from links...')
    save_unique_urls_links(connection)
    print('Saving word clouds from comments...')
    get_word_clouds_comments(connection)
    print('Saving word clouds from links...')
    get_word_clouds_links(connection)

    print('Saving relation between links and unique urls...')
    connection.save_links_ids_with_url()
    print('Saving word clouds from links comments...')
    get_word_clouds_links_comments(connection)

    print('Saving number of comments...')
    connection.save_number_comments()
    print('Showing most commented urls...')
    plot_dictionary(connection.get_most_commented_urls(), 500, 1000)
    
    connection.close_connection()