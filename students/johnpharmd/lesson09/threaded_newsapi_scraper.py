#!/usr/bin/env python3

import threading
import queue
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


def count_word(word, titles):
    word = word.lower()
    count = 0
    for title in titles:
        if word in title.lower():
            count += 1
    return count


def threading_scrape(thread_count=2):
    """Scrapes newsAPI via multiple threads"""
    # see https://uwpce-pythoncert.github.io/PythonCertDevel/modules/ThreadingMultiprocessing.html
    results = queue.Queue()
    sources = get_sources()
    thread_pool = 0

    def worker():
        art_count = 0
        word_count = 0
        for source in sources:
            titles = get_articles(source)
            art_count += len(titles)
            word_count += count_word('trump', titles)

        results.put((word_count, art_count))

    for i in range(thread_count):
        if thread_pool < MAX_THREAD_POOL:
            thread = threading.Thread(target=worker)
            thread.start()
            thread_pool += 1
            print("Thread %s started" % thread.name)

    return sum((results.get() for i in range(thread_count)))


if __name__ == "__main__":

    # scraping parameter
    thread_count = 4

    start = time.time()

    try:
        word_count, art_count = threading_scrape(thread_count)
    except Exception as e:
        print(f'Error occurred: {e}')

    print(WORD, f'found {word_count} times in {art_count} articles')
    print('Process took {:.0f} seconds'.format(time.time() - start))
