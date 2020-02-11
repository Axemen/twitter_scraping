from datetime import datetime as dt

from bs4 import BeautifulSoup as bs
from splinter import Browser


def scraper_user(username, n_tweets=100):
    # browser = Browser('chrome', headless=False)

    with Browser() as browser:

        base_url = "https://twitter.com/"
        browser.visit(base_url)
        browser.visit(base_url + username)
        soup = bs(browser.html, 'html.parser')
        tweets = soup.find_all('div', class_='tweet')
        records = []

        for tweet in tweets:
            record = {
                'text': tweet.find(class_='tweet-text').text,
                'num_comments': tweet.find(class_='js-actionReply').text.strip().split('\n')[-1],
                'num_favorites': tweet.find(class_='js-actionFavorite').text.strip().split('\n')[-1],
                'num_retweets': tweet.find(class_='js-actionRetweet').text.strip().split('\n')[-1],
                'date': dt.utcfromtimestamp(int(tweet.find(class_='_timestamp')['data-time']))
            }
            
            try:
                record['img'] = tweet.find('img')['src']
            except:
                record['img'] = None

        records.append(record)

if __name__ == "__main__":
    scraper_user('BarackObama')