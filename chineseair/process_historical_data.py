import sys

from updater import get_fusiontable


def parse(line):
    """Parse a CSV line from stateair.net's historical records"""
    line = line.split(',')
    return {'city': line[0], 'time': line[2] + ':00', 'value': line[7]}

def process(filename, upserts):
    """Process an entire CSV file from stateair.net"""
    table = get_fusiontable()
    data = open(filename, 'r').read()
    datapoints = []
    for line in data.split('\n'):
        if 'Valid' in line:
            datapoints.append(parse(line))
    if upserts:
        for datapoint in datapoints:
            table.upsert(
                datapoint['time'], {datapoint['city']: datapoint['value']})
    else:
        table.bulk_insert(datapoints)


if __name__ == '__main__':
    print 'Perform all Upserts or Inserts? (U for upserts, I for inserts) '
    upserts = None
    while upserts not in ['U', 'I']:
        upserts = raw_input()
    process(sys.argv[-1], upserts=upserts=='U')
