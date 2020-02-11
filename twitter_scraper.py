from datetime import datetime as dt
from functools import partial
from time import sleep

import pandas as pd
from bs4 import BeautifulSoup as bs
from joblib import Parallel, delayed
from pandas import Series
from splinter import Browser


def show_tweets(browser, n):
    """ Scrolls down on the browser until n tweets are shown """
    num_tweets = bs(browser.html, 'html.parser')\
        .find_all('section')[0]['aria-labelledby']
    while int(num_tweets.split('-')[-1]) < n:
        browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        num_tweets = bs(browser.html, 'html.parser')\
            .find_all('section')[0]['aria-labelledby']


def get_text_from_article(article):
    """ Extracts the tweets text from an article tag """
    return article.find_all('span')[4].text


def get_num_retweets(article):
    return article.find_all(
        'div', {"data-testid": "retweet"})[0].text


def get_num_likes(article):
    return article.find_all(
        'div', {"data-testid": "like"})[0].text


def get_num_replies(article):
    return article.find_all(
        'div', {"data-testid": "reply"})[0].text


def scrape_user(n, username):
    """ Scrape twitter for the designated user """

    with Browser('chrome') as browser:

        all_articles = []

        browser.visit(f'https://www.twitter.com/{username}')
        sleep(2)

        num_tweets = bs(browser.html, 'html.parser')\
            .find_all('section')[0]['aria-labelledby']

        while int(num_tweets.split('-')[-1]) < n:

            # Get da broth
            soup = bs(browser.html, 'html.parser')

            # find the noodles
            articles = soup.find_all('article')

            # pour into the bowl
            all_articles.append(articles)

            # get more water
            browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            num_tweets = bs(browser.html, 'html.parser')\
                .find_all('section')[0]['aria-labelledby']

    flattened_articles = [i for l in all_articles for i in l]
    articles = Series(flattened_articles).drop_duplicates()
    parse_articles(articles).to_csv(f'{username}_tweets.csv', index=False)


def parse_articles(articles):
    """ extracts the text and metadata from the articles """
    df = pd.DataFrame(columns=['time', 'num_replies',
                               'num_likes', 'num_retweets', 'tweet_text'])

    for article in articles:
        try:
            df = df.append({
                'time': article.find('time')['datetime'],
                'num_replies': get_num_replies(article),
                'num_likes': get_num_likes(article),
                'num_retweets': get_num_retweets(article),
                'tweet_text': get_text_from_article(article)
            }, ignore_index=True)
        except Exception as e:
            print(e)

    return df


def main(usernames):
    
    f = delayed(partial(scrape_user, 100))
    executor = Parallel(n_jobs=5,
                        batch_size=2,
                        backend='multiprocessing',
                        prefer='processes')
    tasks = (f(i) for i in usernames)
    executor(tasks)

if __name__ == "__main__":
    usernames = ['BarackObama', 'realDonaldTrump', 'HillaryClinton', 'MichelleObama']
    main(usernames)
