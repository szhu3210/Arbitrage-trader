#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import hmac
import hashlib
import urllib
import json
import codecs

from urllib import parse
from urllib import request
from datetime import datetime

import logging
# logging.basicConfig(level=logging.ERROR)

# timeout in 5 seconds:
TIMEOUT = 5

API_HOST = 'api.huobi.com'

BTCCNY = '/staticmarket/ticker_btc_json.js'
BTCCNY_ORDERS = '/staticmarket/depth_btc_100.js'
LTCCNY = '/staticmarket/ticker_ltc_json.js'
CNYUSD = 'http://api.fixer.io/latest?base=USD'

SCHEME = 'http'

# language setting: 'zh-CN', 'en':
LANG = 'zh-CN'

DEFAULT_GET_HEADERS = {
    'Accept': 'application/json',
    'Accept-Language': LANG
}

class ApiNetworkError(BaseException):
    pass

class Huobi_Main_Monitor(object):

    def __init__(self, host=API_HOST):
        self._host = host

    def get(self, path):
        return self._call('GET', path)

    def _call(self, method, uri, data=None):
        url = '%s://%s%s' % (SCHEME, self._host, uri)
        logging.info(method + ' ' + url)
        req = request.Request(url, data=data, headers=DEFAULT_GET_HEADERS, method=method)
        with request.urlopen(req, timeout=TIMEOUT) as resp:
            if resp.getcode()!=200:
                raise ApiNetworkError('Bad response code: %s %s' % (resp.getcode(), resp.reason))
            # return json.loads(resp.read())
            reader = codecs.getreader('utf-8')
            return json.load(reader(resp))

    def _get(self, method, url, data=None):
        logging.info(method + ' ' + url)
        req = request.Request(url, data=data, headers=DEFAULT_GET_HEADERS, method=method)
        with request.urlopen(req, timeout=TIMEOUT) as resp:
            if resp.getcode()!=200:
                raise ApiNetworkError('Bad response code: %s %s' % (resp.getcode(), resp.reason))
            # return json.loads(resp.read())
            reader = codecs.getreader('utf-8')
            return json.load(reader(resp))

    def get_btccny_ask_price(self):
        return self.get(BTCCNY)['ticker']['sell']

    def get_btccny_ask_prices(self):
        return self.get(BTCCNY_ORDERS)['asks']

    def get_btccny_bid_price(self):
        return self.get(BTCCNY)['ticker']['buy']

    def get_ltccny_bid_price(self):
        return self.get(LTCCNY)['ticker']['buy']

    def get_cnyusd_bid_price(self):
        return self._get('GET', CNYUSD)

    def getAverageAsksGivenSize(self, size):
        size = float(size)
        logging.info('Calculating average ask price based on the size of %.5f' % size)
        asks = self.get_btccny_ask_prices()
        print(asks)
        total = 0
        rest = size
        priceRange = []
        for ask in asks:
            price, volume = ask
            if volume >= rest:
                total += price * rest
                priceRange.append([price, rest])
                rest = 0
                break
            total += price * volume
            rest -= volume
            priceRange.append(ask)
        status = (rest<=0)
        return status, '%.2f' % (total/size), priceRange

if __name__=='__main__':
    pass
    # print(Huobi_Main_Monitor().get_btccny_ask_prices())
    # print(Huobi_Main_Monitor().getAverageAsksGivenSize('5'))