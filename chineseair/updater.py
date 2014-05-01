import json
import os

import requests

from google import FusionTable


TABLE_ID = '14BwrqWVcFIEZSVSa15TlkqTsLYqLO6BXJkWzhu60'
AUTH = json.loads(open('auth.json', 'r').read())


def get_fusiontable():
    return FusionTable(TABLE_ID, 'ventolin@gmail.com',
                       AUTH['pass'], AUTH['api_key'])
