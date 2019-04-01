#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import hmac
import hashlib
import urllib
import json

from urllib import parse
from urllib import request
from datetime import datetime

import logging
# logging.basicConfig(level=logging.ERROR)

# timeout in 5 seconds:
TIMEOUT = 5

API_HOST = 'be.huobi.com'

SCHEME = 'https'

# language setting: 'zh-CN', 'en':
LANG = 'zh-CN'

DEFAULT_GET_HEADERS = {
    'Accept': 'application/json',
    'Accept-Language': LANG
}

class ApiNetworkError(BaseException):
    pass

class Huobi_ETH_Monitor(object):

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
            return json.loads(resp.read())

    def getMarket(self):
        logging.info('Getting market data:')
        return self.get('/market/depth?symbol=ethcny&type=step5')

    def getBids(self):
        logging.info('Getting bids:')
        return self.getMarket()['tick']['bids']

    def printBids(self):
        data = self.getBids()
        self._printMarketOrder(data, title='BIDS(BUY)')

    def getAsks(self):
        logging.info('Getting asks:')
        return self.getMarket()['tick']['asks'] 

    def printAsks(self):
        data = self.getAsks()[::-1]
        self._printMarketOrder(data, title='ASKS(SELL)')

    def _printMarketOrder(self, data, title=''):
        logging.info('Printing Market Order of %s' % title)
        self._br()
        print('  ' + '~'*10 + ''.join(title) + '~'*10 +'\n')
        print('    Price       Volume')
        for line in data:
            print('%10.2f\t%10.4f' % (line[0], line[1]))
        self._br()

    def _br(self):
        print('\n' + '-'*50 + '\n')

    def getAverageBidsGivenSize(self, size):
        size = float(size)
        logging.info('Calculating average bid price based on the size of %.5f' % size)
        bids = self.getBids()
        total = 0
        rest = size
        priceRange = []
        for bid in bids:
            price, volume = bid
            if volume>rest:
                total += price * rest
                priceRange.append([price, rest])
                rest = 0
                break
            total += price*volume
            rest -= volume
            priceRange.append(bid)
        status = (rest<=0)
        return status, '%.2f' % (total/size), priceRange

def main():
    a = Huobi_ETH_Monitor()
    print(a.getMarket())
    print(a.getAsks())
    print(a.getBids())
    a.printAsks()
    a.printBids()
    print(a.getAverageBidsGivenSize(10))

if __name__=='__main__':
    # main()
    pass