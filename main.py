from IncelsSQL import IncelsSQL
from random import randint
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import numpy as np
import time

def reduce_dictionary(dictionary, min = 200, max = 400):
    return {k:dictionary[k] for k in dictionary if dictionary[k] > min and dictionary[k] <= max}

def plot_dictionary(dictionary, min, max, color='orange'):
    d = reduce_dictionary(dictionary, min, max)

    plt.bar(range(len(d)), list(d.values()), align='center', color = color)
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
    stopwords.update(['https', 'http', 'www', 'html', 'get_simple', 'com', 'click', 'archive', 'amp', 'auto', 'sub', 'url', 'org'])

    wordcloud = WordCloud(width=800, height=400, stopwords=stopwords, background_color='white').generate(text)
    wordcloud.to_file('Images/word_clouds/' + folder + '/' + file_name)

    # plt.imshow(wordcloud, interpolation='bilinear')
    # plt.axis("off")
    # plt.show()

    return

def save_unique_urls_comments(connection, paths=False):
    
    urls = connection.get_urls_from_comments()
    unique_urls = connection.get_domains_path(urls)

    if paths == False:
        unique_urls = connection.get_domains(urls)
        connection.save_urls(unique_urls, t_name='unique_urls_from_comments')
    else:
        unique_urls = connection.get_domains_path(urls)
        connection.save_urls(unique_urls, t_name='unique_paths_from_comments')

    plot_dictionary(unique_urls, 1000, 1000000)
    plot_dictionary(unique_urls, 400, 1000)
    plot_dictionary(unique_urls, 200, 400)
    plot_dictionary(unique_urls, 100, 200)

def save_unique_urls_links(connection, paths=False):
    
    urls = connection.get_urls_from_links()

    if paths == False:
        unique_urls = connection.get_domains(urls)
        connection.save_urls(unique_urls, t_name='unique_urls_from_links')
    else:
        unique_urls = connection.get_domains_path(urls)
        connection.save_urls(unique_urls, t_name='unique_paths_from_links')
        
    plot_dictionary(unique_urls, 100, 1000000, color = 'blue')
    plot_dictionary(unique_urls, 10, 1000000, color = 'blue')

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

def get_word_clouds_links_comments(connection, paths=False):

    if paths == False:
        unique_urls = connection.get_unique_urls_from_links(n_occurrences=10, return_id=True)
    else:
        unique_urls = connection.get_unique_paths_from_links(n_occurrences=5, return_id=True)

    unique_urls = {k: v for k, v in sorted(unique_urls.items(), key=lambda item: item[0], reverse=True)}

    for u_id, url in unique_urls.items():
        text = connection.get_full_text_from_url(u_id, paths)

        if(len(text) > 0):
            if paths==False:
                plot_word_cloud(text, url, folder='links_comments')
            else:
                plot_word_cloud(text, url, folder='links_comments_p')

def get_feedback_posts_between_communities(connection):

    communities = {'t5_2sjgc': 'MGTOW',
                   't5_2zlzd': 'badwomensanatomy',
                   't5_3jxsz': 'IncelsWithoutHate',
                   't5_3kvtt': 'IncelTears',
                   't5_3m7dc': 'IncelsInActions',
                   't5_3pci5': 'Braincels',
                   't5_hnz41': 'Trufemcels'}

    for c_id, c_name in communities.items():

        links_text = connection.get_text_links(community=c_id) # Obtain links where subreddit_id = c_id

        communities_count = {'t5_2sjgc': 0,
                             't5_2zlzd': 0,
                             't5_3jxsz': 0,
                             't5_3kvtt': 0,
                             't5_3m7dc': 0,
                             't5_3pci5': 0,
                             't5_hnz41': 0,
                             'red_pill': 0,
                             'incels_me': 0,
                             'mgtow_com': 0}

        for text in links_text: # For each link search

            # Process text
            text = text.lower()
            if 'redd' in text:
                text = text.replace('redd.it', 'reddit.com')
                text = text.replace('np.reddit', 'reddit')

            # Count
            if 'reddit.com/r/mgtow' in text:
                communities_count['t5_2sjgc']+=1
            elif 'reddit.com/r/badwomensanatomy' in text:
                communities_count['t5_2zlzd']+=1
            elif 'reddit.com/r/incelswithouthate' in text:
                communities_count['t5_3jxsz']+=1
            elif 'reddit.com/r/inceltears' in text:
                communities_count['t5_3kvtt']+=1
            elif 'reddit.com/r/incelsinaction' in text:
                communities_count['t5_3m7dc']+=1
            elif 'reddit.com/r/braincels' in text:
                communities_count['t5_3pci5']+=1
            elif 'reddit.com/r/trufemcels' in text:
                communities_count['t5_hnz41']+=1
            elif 'reddit.com/r/theredpill' in text:
                communities_count['red_pill']+=1
            elif 'incels.me' in text:
                communities_count['incels_me']+=1
            elif 'mgtow.com' in text:
                communities_count['mgtow_com']+=1
            

        print(c_name + ' feedback:')
        print('\t' + 'MGTOW: ' + str(communities_count['t5_2sjgc']))
        print('\t' + 'badwomensanatomy: ' + str(communities_count['t5_2zlzd']))
        print('\t' + 'IncelsWithoutHate: ' + str(communities_count['t5_3jxsz']))
        print('\t' + 'IncelTears: ' + str(communities_count['t5_3kvtt']))
        print('\t' + 'IncelsInActions: ' + str(communities_count['t5_3m7dc']))
        print('\t' + 'Braincels: ' + str(communities_count['t5_3pci5']))
        print('\t' + 'Trufemcels: ' + str(communities_count['t5_hnz41']))
        print('\t' + 'TheRedPill: ' + str(communities_count['red_pill']))
        print('\t' + 'Incels.me: ' + str(communities_count['incels_me']))
        print('\t' + 'MGTOW.com: ' + str(communities_count['mgtow_com']))

def get_feedback_comments_between_communities(connection):

    communities = {'t5_2sjgc': 'MGTOW',
                   't5_2zlzd': 'badwomensanatomy',
                   't5_3jxsz': 'IncelsWithoutHate',
                   't5_3kvtt': 'IncelTears',
                   't5_3m7dc': 'IncelsInActions',
                   't5_3pci5': 'Braincels',
                   't5_hnz41': 'Trufemcels'}

    for c_id, c_name in communities.items():

        links = connection.get_ids_and_text_links(community=c_id) # Obtain links where subreddit_id = c_id

        communities_count = {'t5_2sjgc': 0,
                             't5_2zlzd': 0,
                             't5_3jxsz': 0,
                             't5_3kvtt': 0,
                             't5_3m7dc': 0,
                             't5_3pci5': 0,
                             't5_hnz41': 0,
                             'red_pill': 0,
                             'incels_me': 0,
                             'mgtow_com': 0}

        for t in links: # For each link search
            link_id, text = t

            # Process text
            text = text.lower()
            if 'redd' in text:
                text = text.replace('redd.it', 'reddit.com')
                text = text.replace('np.reddit', 'reddit')

            # Count
            if 'reddit.com/r/mgtow' in text:
                communities_count['t5_2sjgc']+= connection.get_n_comments_from_link(link_id)
            elif 'reddit.com/r/badwomensanatomy' in text:
                communities_count['t5_2zlzd']+= connection.get_n_comments_from_link(link_id)
            elif 'reddit.com/r/incelswithouthate' in text:
                communities_count['t5_3jxsz']+= connection.get_n_comments_from_link(link_id)
            elif 'reddit.com/r/inceltears' in text:
                communities_count['t5_3kvtt']+= connection.get_n_comments_from_link(link_id)
            elif 'reddit.com/r/incelsinaction' in text:
                communities_count['t5_3m7dc']+= connection.get_n_comments_from_link(link_id)
            elif 'reddit.com/r/braincels' in text:
                communities_count['t5_3pci5']+= connection.get_n_comments_from_link(link_id)
            elif 'reddit.com/r/trufemcels' in text:
                communities_count['t5_hnz41']+= connection.get_n_comments_from_link(link_id)
            elif 'reddit.com/r/theredpill' in text:
                communities_count['red_pill']+= connection.get_n_comments_from_link(link_id)
            elif 'incels.me' in text:
                communities_count['incels_me']+= connection.get_n_comments_from_link(link_id)
            elif 'mgtow.com' in text:
                communities_count['mgtow_com']+= connection.get_n_comments_from_link(link_id)
            

        print(c_name + ' feedback:')
        print('\t' + 'MGTOW: ' + str(communities_count['t5_2sjgc']))
        print('\t' + 'badwomensanatomy: ' + str(communities_count['t5_2zlzd']))
        print('\t' + 'IncelsWithoutHate: ' + str(communities_count['t5_3jxsz']))
        print('\t' + 'IncelTears: ' + str(communities_count['t5_3kvtt']))
        print('\t' + 'IncelsInActions: ' + str(communities_count['t5_3m7dc']))
        print('\t' + 'Braincels: ' + str(communities_count['t5_3pci5']))
        print('\t' + 'Trufemcels: ' + str(communities_count['t5_hnz41']))
        print('\t' + 'TheRedPill: ' + str(communities_count['red_pill']))
        print('\t' + 'Incels.me: ' + str(communities_count['incels_me']))
        print('\t' + 'MGTOW.com: ' + str(communities_count['mgtow_com']))

# MAIN
if __name__ == "__main__":

    # Start connection
    print('Start connection...')
    connection = IncelsSQL()
    time.sleep(10) # 10 seconds before removing a table for creating it again

    # # CREATING AND UPDATING TABLES
    print('Saving unique urls from comments...')
    save_unique_urls_comments(connection)
    print('Saving unique paths from links...')
    save_unique_urls_links(connection, paths=True)
    print('Saving unique domains from links...')
    save_unique_urls_links(connection, paths=True)

    print('Saving relation between links and unique paths...')
    connection.save_links_ids_with_url(t_name='paths_links_ids', paths=True)
    print('Saving relation between links and unique domains...')
    connection.save_links_ids_with_url(t_name='urls_links_ids', paths=False)

    print('Saving number of users and number of comments...')
    connection.save_n_comments_and_n_users(paths=True)
    connection.save_n_comments_and_n_users(paths=False)

    # # STATS
    links_url, links_no_url, comments_url, comments_no_url = connection.get_comments_from_links_stats()
    print('Links with url:', str(links_url), 'Comments from links with url:', str(comments_url))
    print('Links without url:', str(links_no_url), 'Comments from links without url:', str(comments_no_url))
    print('Avarege comments for links with url:', str(comments_url/links_url))
    print('Avarege comments for links without url:', str(comments_no_url/links_no_url))

    # # PLOTING

    print('Showing most commented paths...')
    plot_dictionary(connection.get_most_commented_paths(), 1000, 1000000, color='green')
    plot_dictionary(connection.get_most_commented_paths(), 500, 1000, color='green')
    print('Showing most commented domains...')
    plot_dictionary(connection.get_most_commented_urls(), 1000, 1000000, color='green')
    plot_dictionary(connection.get_most_commented_urls(), 500, 1000, color='green')
    print('Showing number of users...')
    plot_dictionary(connection.get_n_users(paths=True), 100, 10000, color='red')
    plot_dictionary(connection.get_n_users(paths=True), 10, 100, color='red')

    # # FEEDBACK
    print('Showing feedback between communities...')
    get_feedback_posts_between_communities(connection)
    get_feedback_comments_between_communities(connection)

    # # TOPICS

    connection.save_comments_urls(t_name = 'comments_from_url', paths = False)
    connection.save_comments_urls(t_name = 'comments_from_paths', paths = True)   

    # # WORD CLOUDS

    print('Saving word clouds from comments...')
    get_word_clouds_comments(connection)
    print('Saving word clouds from links...')
    get_word_clouds_links(connection)
    print('Saving word clouds from links comments...')
    get_word_clouds_links_comments(connection, paths=True)

    connection.close_connection()