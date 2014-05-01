from datetime import datetime
import json
import os

from BeautifulSoup import BeautifulSoup
import logbook
import requests

from google import FusionTable


TABLE_ID = '14BwrqWVcFIEZSVSa15TlkqTsLYqLO6BXJkWzhu60'
AUTH = json.loads(open('auth.json', 'r').read())
FEEDS = {
    'Beijing': 'http://www.stateair.net/web/rss/1/1.xml',
    'Chengdu': 'http://www.stateair.net/web/rss/1/2.xml',
    'Guangzhou': 'http://www.stateair.net/web/rss/1/3.xml',
    'Shanghai': 'http://www.stateair.net/web/rss/1/4.xml',
    'Shenyang': 'http://www.stateair.net/web/rss/1/5.xml'
}
log = logbook.Logger(__name__)


def get_fusiontable():
    return FusionTable(TABLE_ID, 'ventolin@gmail.com',
                       AUTH['pass'], AUTH['api_key'])

def parse_feeds():
    retval = {}
    for city, url in FEEDS.iteritems():
        log.info('Parsing {0}'.format(url))
        xml = requests.get(url).text
        soup = BeautifulSoup(xml)
        for reading in soup.findAll('item'):
            value = reading.aqi.text
            if value == '-999':
                continue
            time = datetime.strptime(reading.readingdatetime.text,
                                     '%m/%d/%Y %I:%M:%S %p')
            time = time.strftime('%Y-%m-%d %H:%M:%S')
            retval.setdefault(time, {})
            retval[time][city] = value
    return retval

if __name__ == '__main__':
    table = get_fusiontable()
    for time, values in parse_feeds().iteritems():
        table.upsert(time, values)
    log.info('Finished.')
