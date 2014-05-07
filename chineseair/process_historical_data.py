#!/usr/bin/env python
import sys

from updater import get_fusiontable


def parse(line):
    """Parse a CSV line from stateair.net's historical records"""
    line = line.split(',')
    return {'city': line[0], 'time': line[2] + ':00', 'value': line[7]}

def process(filenames):
    """Process an entire CSV file from stateair.net"""
    table = get_fusiontable()
    datapoints = {}
    for filename in filenames:
        data = open(filename, 'r').read()
        for line in data.split('\n'):
            if 'Valid' in line:
                datapoint = parse(line)
                datapoints.setdefault(datapoint['time'], {})
                datapoints[datapoint['time']][datapoint['city']] = datapoint['value']
    for time, values in datapoints.iteritems():
        table.upsert(time, values)


if __name__ == '__main__':
    process([f for f in sys.argv if f.endswith('.csv')])
