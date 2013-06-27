#!/usr/bin/env python
# -*- coding: utf8 -*-

import json
import os
import time

import requests


FEEDS = ['beijingair', 'CGShanghaiAir', 'CGChengduAir', 'Guangzhou_Air']


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
        if ' to ' not in timestr:
            t = time.strptime(timestr, '%m-%d-%Y %H:%M')
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
        all_data = {}
    else:
        with open(filename, 'r') as f:
            all_data = json.loads(f.read())

    for feed in FEEDS:
        print 'Forcing an update of twitter feed {0} on greptweet.com...'.format(feed)
        requests.get('http://greptweet.com/f/{0}'.format(feed))
        print 'Processing data...'
        all_data = update_data(feed, all_data)

    print 'Saving %s' % filename
    with open(filename, 'w') as f:
        f.write(json.dumps(all_data, indent=4))


def update_data(feed, all_data):
    tweets = requests.get(
        'http://greptweet.com/u/{feed}/{feed}.txt'.format(feed=feed.lower()))
    for line in tweets.text.split('\n'):
        try:
            time, value = process_tweet(line)
        except ValueError:
            continue

        all_data.setdefault(time, {}).setdefault(feed, value)
    return all_data


def process_tweet(text):
    segments = text.split('; ')
    if '24hr avg' in text:
        raise ValueError('Tweet is an average value')
    if 'No Reading' in text or 'No Data' in text or len(segments) < 5:
        raise ValueError('Tweet contained no value')
    
    time = segments[0].split('|')[-1]
    value = segments[3]
    
    return time, value


if __name__ == '__main__':
    update_feeds()
    update_webpage()
