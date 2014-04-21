import json
import os

import requests

BASE_URL = "https://www.googleapis.com/fusiontables/v1/query?sql={0}"
TABLE_ID = '14BwrqWVcFIEZSVSa15TlkqTsLYqLO6BXJkWzhu60'
with open('auth.json', 'r') as f:
    AUTH = json.loads(f.read())

def get_auth_token():
    resp = requests.post('https://www.google.com/accounts/ClientLogin',
                         headers={'Content-type': 'application/x-www-form-urlencoded'},
                         params={'accountType': 'GOOGLE', 'Email': 'ventolin@gmail.com',
                                 'Passwd': AUTH['google_pass'], 'service': 'fusiontables',
                                 'source': 'ventolin.org'})
    for segment in resp.text.split('\n'):
        if 'Auth=' in segment:
            return segment

def perform_sql(sql, auth_token):
    resp = requests.post(
        BASE_URL.format(sql),
        headers={'Authorization': 'GoogleLogin {0}'.format(auth_token.replace('Auth=', 'auth='))}
    return resp
