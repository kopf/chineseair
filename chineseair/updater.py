#!/usr/bin/env python
# -*- coding: utf8 -*-

import json
import os
import time

import twitter


FEEDS = ['beijingair', 'CGShanghaiAir', 'CGChengduAir', 'Guangzhou_Air']

with open('auth.json') as f:
    AUTH = json.loads(f.read())
API = twitter.Api(**AUTH)

def update_webpage():
    print 'Updating webpage...'
    datapoint = '''[new Date({year}, {month}, {date}, {hour}, 0, 0), {beijing}, {shanghai}, {chengdu}, {guangzhou}]'''
    template = '''
        data.addRows([
            {datapoints}
        ]);
        return data;
    '''
    print 'Loading data...'
    with open('data.json', 'r') as f:
        data = json.loads(f.read())
    datapoints = []
    print 'Constructing JS...'
    for timestr, values in data.iteritems():
        t = time.strptime(timestr[:15], '%m-%d-%Y %H:%M')
        datapoints.append(datapoint.format(year=t.tm_year, month=t.tm_mon - 1,
                                           date=t.tm_mday, hour=t.tm_hour,
                                           beijing=values.get('beijingair', 'undefined'),
                                           shanghai=values.get('CGShanghaiAir', 'undefined'),
                                           chengdu=values.get('CGChengduAir', 'undefined'),
                                           guangzhou=values.get('Guangzhou_Air', 'undefined')))
    datapoints = ',\n'.join(sorted(datapoints))
    js = '''
            function populateData(data) {
                %s
            }
    ''' % template.format(datapoints=datapoints)
    print 'Writing to data.js...'
    with open('../javascripts/data.js', 'w') as f:
        f.write(js)
    print 'Done!'


def update_feeds():
    filename = 'data.json'
    if not os.path.exists(filename):
        total_data = {}
    else:
        with open(filename, 'r') as f:
            total_data = json.loads(f.read())

    finished = {}
    for feed in FEEDS:
        finished[feed] = False
    page = 1

    while not all([state for _, state in finished.iteritems()]):
        for feed in FEEDS:
            print 'Getting page {0} of tweets for {1}'.format(page, feed)
            finished[feed], total_data = get_new_tweets(feed, page, total_data)
        page += 1

    print 'Saving %s' % filename
    with open(filename, 'w') as f:
        f.write(json.dumps(total_data, indent=4))


def get_new_tweets(feed, page, total_data):
    tweets = API.GetUserTimeline(feed, count=200, page=page)
    if not tweets:
        return True, total_data
    finished = False
    for tweet in tweets:
        try:
            time, value = process_tweet(tweet)
        except ValueError:
            continue

        if time in total_data:
            if feed in total_data[time]:
                finished = True
                break
            else:
                total_data[time][feed] = value
        else:
            total_data[time] = {feed: value}
    return finished, total_data


def process_tweet(tweet):
    processed = tweet.text.split('; ')
    if '24hr avg' in tweet.text:
        raise ValueError('Tweet is an average value')
    if 'No Reading' in tweet.text or 'No Data' in tweet.text or len(processed) < 5:
        raise ValueError('Tweet contained no value')
    return processed[0], processed[3]


if __name__ == '__main__':
    update_feeds()
    update_webpage()
