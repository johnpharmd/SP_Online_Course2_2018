#!/usr/bin/env python3

import threading
import queue
# import functools
import time
import requests

MAX_THREAD_POOL = 250

WORD = 'trump'

NEWS_API_KEY = '0b7b85e7886047c6a516f5b5516276a1'

base_url = 'https://newsapi.org/v1/'


def get_sources():
    """
    Get all the English language sources of news

    'https://newsapi.org/v1/sources?language=en'
    """
    url = base_url + 'sources'
    params = {'language': 'en'}
    resp = requests.get(url, params=params)
    data = resp.json()
    sources = [src['id'].strip() for src in data['sources']]
    print('all the sources')
    print(sources)
    return sources


def get_articles(source):
    """
    https://newsapi.org/v1/articles?source=associated-press&sortBy=top&apiKey=0b7b85e7886047c6a516f5b5516276a1
    """
    url = base_url + 'articles'
    params = {'source': source,
              'apiKey': NEWS_API_KEY,
              # 'sortBy': 'latest',  # some sources don't support latest}
              'sortBy': 'top',
              # 'sortBy': 'popular',
              }
    print('requesting:', source)
    resp = requests.get(url, params=params)
    if resp.status_code != 200:  # aiohttp has 'status'
        print('something went wrong with {}'.format(source))
        print(resp)
        print(resp.text)
        return []
    data = resp.json()
    # the url to the article itself is in data['articles'][i]['url']
    titles = [str(art['title']) + str(art['description']) for art in
              data['articles']]
    return titles


def scrape_f(f, N):
    # dx = (b - a) / N
    return sum(map(f, (i for i in range(N))))


# def timer(func):
#     """Print the runtime of the decorated function"""
#     # from https://realpython.com/primer-on-python-decorators/
#     @functools.wraps(func)
#     def wrapper_timer(*args, **kwargs):
#         start_time = time.perf_counter()    # 1
#         value = func(*args, **kwargs)
#         end_time = time.perf_counter()      # 2
#         run_time = end_time - start_time    # 3
#         print(f'Finished {func.__name__!r} in {run_time:.4f} secs')
#         return value
#     return wrapper_timer


# @timer
def threading_api(func, N, thread_count=2):
    """Scrapes newsAPI via multiple threads"""
    # break work into N chunks
    # see https://uwpce-pythoncert.github.io/PythonCertDevel/modules/ThreadingMultiprocessing.html
    N_chunk = int(float(N) / thread_count)
    results = queue.Queue()

    def worker(*args):
        results.put(scrape_f(*args))

    if thread_count < MAX_THREAD_POOL:
        for i in range(thread_count):
            thread = threading.Thread(target=worker, args=(func, N_chunk))
            thread.start()
            print("Thread %s started" % thread.name)

    return sum((results.get() for i in range(thread_count)))


def count_word(word, titles):
    word = word.lower()
    count = 0
    for title in titles:
        if word in title.lower():
            count += 1
    return count


if __name__ == "__main__":

    # scraping parameters
    N = 10**7
    thread_count = 2

    start = time.time()
    # sources = threading_api(get_sources(), N, thread_count)
    # titles = threading_api(get_articles(source), N, thread_count)
    art_count = 0
    word_count = 0
    for source in sources:
        titles = get_articles(source)
        art_count += len(titles)
        word_count += count_word('trump', titles)
    print(WORD, f'found {word_count} times in {art_count} articles,' +
                ' using {N} chunks')

    print('Process took {:.0f} seconds'.format(time.time() - start))
