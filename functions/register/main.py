# -*- coding: utf-8 -*-

# Method for  registering this module

from __future__ import print_function, unicode_literals

import requests
import json
import os


def handle(event, ctx):
    if not 'api_url' in event:
        raise Exception("'api_url' not in payload")

    with open('module.json') as data_file:
        data = json.load(data_file)

    url = event['api_url']+'/tx/module'

    response = requests.post(url, data=data, headers={'content-type': 'application/json'})
    return json.loads(response.text)
