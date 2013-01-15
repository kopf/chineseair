#!/usr/bin/env python
# -*- coding: utf8 -*-

import json
import os
import time

from BeautifulSoup import BeautifulSoup
import twitter


FEEDS = ['beijingair', 'CGShanghaiAir', 'CGChengduAir', 'Guangzhou_Air']

with open('auth.json') as f:
    AUTH = json.loads(f.read())
API = twitter.Api(**AUTH)

def update_webpage():
    print 'Updating webpage...'
    datapoint = '''[new Date({year}, {month}, {date}, {hour}, 0, 0), {value}]'''
    template = '''
        data.addRows([
            {datapoints}
        ]);
        return data;
    '''
    print 'Loading data...'
    with open('beijingair.json', 'r') as f:
        data = json.loads(f.read())
    datapoints = []
    print 'Constructing HTML...'
    for entry in data:
        for timestr, value in entry.iteritems():
            t = time.strptime(timestr, '%m-%d-%Y %H:%M')
            datapoints.append(datapoint.format(year=t.tm_year, month=t.tm_mon,
                                               date=t.tm_mday, hour=t.tm_hour,
                                               value=value))
    datapoints = ',\n'.join(datapoints)
    html = '''
        <script type="text/javascript" id="chineseair_data_population">
            function populateData(data) {
                %s
            }
        </script>
    ''' % template.format(datapoints=datapoints)
    print 'Inserting HTML...'
    with open('../index.html', 'r') as f:
        soup = BeautifulSoup(f.read())
    element = soup.find('script', {'id': 'chineseair_data_population'})
    element.replaceWith(BeautifulSoup(html))
    with open('../index.html', 'w') as f:
        f.write(str(soup))
    print 'Done!'


def update_feed(feed):
    filename = '%s.json' % feed
    if not os.path.exists(filename):
        total_data = []
    else:
        with open(filename, 'r') as f:
            total_data = json.loads(f.read())
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
    processed = tweet.text.split('; ')
    if '24hr avg' in tweet.text:
        raise ValueError('Tweet is an average value')
    if 'No Reading' in tweet.text or 'No Data' in tweet.text or len(processed) < 5:
        raise ValueError('Tweet contained no value')
    return {processed[0]: processed[3]}


if __name__ == '__main__':
    for feed in FEEDS:
        update_feed(feed)
    update_webpage()
