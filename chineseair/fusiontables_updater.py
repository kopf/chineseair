import json
import os

import requests

TABLE_ID = '14BwrqWVcFIEZSVSa15TlkqTsLYqLO6BXJkWzhu60'
with open('auth.json', 'r') as f:
    AUTH = json.loads(f.read())

