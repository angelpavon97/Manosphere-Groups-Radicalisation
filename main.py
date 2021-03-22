from IncelsSQL import IncelsSQL
from random import randint
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

def reduce_dictionary(dictionary, min = 200, max = 400):
    return {k:dictionary[k] for k in dictionary if dictionary[k] > min and dictionary[k] <= max}

def plot_dictionary(dictionary, min, max):
    d = reduce_dictionary(dictionary, min, max)

    plt.bar(range(len(d)), list(d.values()), align='center', color = 'orange')
    plt.xticks(range(len(d)), list(d.keys()), rotation='vertical')
    plt.show()

def get_comments_with_url(url, comments):
    return [c for c in comments if url in c.lower()]

def plot_word_cloud(text, file_name='word_cloud', folder='comments'):
    file_name = file_name.replace('/', '_').replace('.', '_') + '.png'
    wordcloud = WordCloud(width=800, height=400, stopwords=STOPWORDS, background_color='white').generate(text)
    wordcloud.to_file('img/word_clouds/' + folder + '/' + file_name)

    # plt.imshow(wordcloud, interpolation='bilinear')
    # plt.axis("off")
    # plt.show()

    return

# plot_word_cloud(' '.join(['dog dog dog', 'cat cat cat cat is is is is is is is ']))
connection = IncelsSQL()

# connection.save_urls(unique_urls, t_name='unique_urls_from_comments')

urls = connection.get_unique_urls_from_comments(n_occurrences=100)
comments = connection.get_body_comments()

for u in urls:
    comments_with_url = get_comments_with_url(u, comments)

    if len(comments_with_url) == 0:
        print('url defectuosa: ', u)
    else:
        plot_word_cloud(' '.join(comments_with_url), u)

# plot_dictionary(unique_urls, 1000, 1000000)
# plot_dictionary(unique_urls, 400, 1000)
# plot_dictionary(unique_urls, 200, 400)
# plot_dictionary(unique_urls, 100, 200)
# plot_dictionary(unique_urls, 50, 1000000)

connection.close_connection()
