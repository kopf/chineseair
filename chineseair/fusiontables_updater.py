import json
import os

import requests

BASE_URL = "https://www.googleapis.com/fusiontables/v1/query?sql={sql}&key={api_key}"
TABLE_ID = '14BwrqWVcFIEZSVSa15TlkqTsLYqLO6BXJkWzhu60'
with open('auth.json', 'r') as f:
    AUTH = json.loads(f.read())


def get_auth_token():
    resp = requests.post('https://www.google.com/accounts/ClientLogin',
                         headers={'Content-type': 'application/x-www-form-urlencoded'},
                         params={'accountType': 'GOOGLE', 'Email': 'ventolin@gmail.com',
                                 'Passwd': AUTH['pass'], 'service': 'fusiontables',
                                 'source': 'ventolin.org'})
    for segment in resp.text.split('\n'):
        if 'Auth=' in segment:
            return segment.replace('Auth=', 'auth=')


def perform_sql(sql, auth_token):
    resp = requests.post(
        BASE_URL.format(sql=sql, api_key=AUTH['api_key']),
        headers={'Authorization': 'GoogleLogin {0}'.format(auth_token)})
    return resp


def get_row_by_time(time):
    """Selects rows, filtering by time. 
    Helper function to ensure single quotes (NOT double quotes) are used inside
    sql query
    """
    sql = "SELECT * FROM {0} WHERE Time='{1}'".format(TABLE_ID, time)
    return perform_sql(sql)
