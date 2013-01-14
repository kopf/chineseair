import os
import json

import twitter


def load_auth_data(filename):
    with open(filename) as f:
        data = f.read()
    return json.loads(data)

if __name__ == '__main__':
    auth = load_auth_data('auth.json')
    api = twitter.Api(**auth)
    print api.VerifyCredentials()