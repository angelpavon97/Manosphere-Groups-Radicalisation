from IncelsSQL import IncelsSQL
from random import randint
import matplotlib.pyplot as plt

def reduce_dictionary(dictionary, min = 200, max = 400):
    return {k:dictionary[k] for k in dictionary if dictionary[k] > min and dictionary[k] <= max}

def plot_dictionary(dictionary, min, max):
    d = reduce_dictionary(dictionary, min, max)

    plt.bar(range(len(d)), list(d.values()), align='center', color = 'orange')
    plt.xticks(range(len(d)), list(d.keys()), rotation='vertical')
    plt.show()

connection = IncelsSQL()

# comments = connection.get_comments()
# urls = connection.get_urls_statistics()

# print('Number of comments: ', len(comments))
# print(comments[randint(0,len(comments))])

# print('Number of urls: ', len(urls))
# print(urls[randint(0,len(urls))])

# urls = connection.get_url_root()
# print(urls)
# plot_dictionary(urls)

urls = connection.get_urls_from_comments()
print('Number of urls: ', len(urls))
print(urls[randint(0,len(urls))])

# unique_urls = connection.get_domains_from_comments(urls)
unique_urls = connection.get_domains_path_from_comments(urls)
# print(unique_urls)

plot_dictionary(unique_urls, 1000, 1000000)
plot_dictionary(unique_urls, 400, 1000)
plot_dictionary(unique_urls, 200, 400)
plot_dictionary(unique_urls, 100, 200)

connection.close_connection()
