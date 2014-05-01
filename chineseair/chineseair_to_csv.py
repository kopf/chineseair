#!/usr/bin/env python
"""A hacked-together script to transform the old data.js file into a .csv"""

import re
import sys

def load_data():
    retval = []
    for line in open(sys.argv[-1], 'r').readlines():
        if 'new Date' in line:
            retval.append(line.strip())
    return retval
        
if __name__ == '__main__':
    data = load_data()
    print 'Time,Beijing,Shanghai,Chengdu,Guangzhou'
    for line in data:
        (_, _, year, month, date, hour, _, _, _, beijing, shanghai, chengdu, guangzhou, _) = re.split('\(|, |\)|\[|\]', line)
        if beijing == 'undefined': beijing = ''
        if shanghai == 'undefined': shanghai = ''
        if chengdu == 'undefined': chengdu = ''
        if guangzhou == 'undefined': guangzhou = ''
        print '{year}-{month}-{date} {hour}:00:00,{beijing},{shanghai},{chengdu},{guangzhou}'.format(
            year=year, month=str(int(month) + 1).zfill(2), date=date, hour=hour.zfill(2), beijing=beijing, shanghai=shanghai,
            chengdu=chengdu, guangzhou=guangzhou)

