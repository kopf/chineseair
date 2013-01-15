#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import json

import twitter


FEEDS = ['beijingair', 'CGShanghaiAir', 'CGChengduAir', 'Guangzhou_Air']

with open('auth.json') as f:
    AUTH = json.loads(f.read())
API = twitter.Api(**AUTH)

def update_webpage():
    pass

def update_feed(feed):
    filename = '%s.json' % feed
    if not os.path.exists(filename):
        total_data = []
    else:
        with open(filename, 'r') as f:
            total_data = json.loads(f.read)
    finished = False
    page = 1
    while not finished:
        print 'Getting page {0} of tweets for {1}'.format(page, feed)
        finished, total_data = get_new_tweets(feed, page, total_data)
        page += 1

    print 'Saving %s' % filename
    with open(filename, 'w') as f:
        f.write(json.dumps(total_data))

def get_new_tweets(feed, page, total_data):
    tweets = API.GetUserTimeline(feed, count=200, page=page)
    if not tweets:
        return True, total_data
    finished = False
    for tweet in tweets:
        try:
            tweet = process_tweet(tweet)
        except ValueError:
            continue

        if tweet in total_data:
            finished = True
            break
        else:
            total_data.append(tweet)
    return finished, total_data

def process_tweet(tweet):
    if '24hr avg' in tweet.text:
        raise ValueError('Tweet is an average value')
    return tweet.text.split('; ')

if __name__ == '__main__':
    for feed in FEEDS:
        update_feed(feed)
    update_webpage()
