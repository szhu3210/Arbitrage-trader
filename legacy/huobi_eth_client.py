#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import base64
import hmac
import hashlib
import json

from urllib import parse
from urllib import request
from datetime import datetime

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

DEFAULT_POST_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Accept-Language': LANG
}

class Dict(dict):

    def __init__(self, **kw):
        super().__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

def _toDict(d):
    return Dict(**d)

class ApiError(BaseException):
    pass

class ApiNetworkError(BaseException):
    pass

class ApiClient(object):

    def __init__(self, appKey, appSecret, host=API_HOST):
        '''
        Init api client object, by passing appKey and appSecret.
        '''
        self._accessKeyId = appKey
        self._accessKeySecret = appSecret.encode('utf-8') # change to bytes
        self._host = host


    def get(self, path, **params):
        '''
        Send a http get request and return json object.
        '''
        qs = self._sign('GET', path, self._utc(), params)
        return self._call('GET', '%s?%s' % (path, qs))

    def post(self, path, obj=None):
        '''
        Send a http post request and return json object.
        '''
        qs = self._sign('POST', path, self._utc())
        data = None
        if obj is not None:
            data = json.dumps(obj).encode('utf-8')
        return self._call('POST', '%s?%s' % (path, qs), data)

    def _call(self, method, uri, data=None):
        url = '%s://%s%s' % (SCHEME, self._host, uri)
        # print(method + ' ' + url)
        req = request.Request(url, data=data, headers=DEFAULT_GET_HEADERS if method=='GET' else DEFAULT_POST_HEADERS, method=method)
        with request.urlopen(req, timeout=TIMEOUT) as resp:
            if resp.getcode()!=200:
                raise ApiNetworkError('Bad response code: %s %s' % (resp.getcode(), resp.reason))
            return self._parse(resp.read())

    def _parse(self, text):
        # print('Response:\n%s' % text)
        result = json.loads(text, object_hook=_toDict)
        if result.status=='ok':
            return result.data
        raise ApiError('%s: %s' % (result['err-code'], result['err-msg']))

    def _sign(self, method, path, ts, params=None):
        self._method = method
        # create signature:
        if params is None:
            params = {}
        params['SignatureMethod'] = 'HmacSHA256'
        params['SignatureVersion'] = '2'
        params['AccessKeyId'] = self._accessKeyId
        params['Timestamp'] = ts
        # sort by key:
        keys = sorted(params.keys())
        # build query string like: a=1&b=%20&c=:
        qs = '&'.join(['%s=%s' % (key, self._encode(params[key])) for key in keys])
        # build payload:
        payload = '%s\n%s\n%s\n%s' % (method, self._host, path, qs)
        # print('payload:\n%s' % payload)
        dig = hmac.new(self._accessKeySecret, msg=payload.encode('utf-8'), digestmod=hashlib.sha256).digest()
        sig = self._encode(base64.b64encode(dig).decode())
        # print('sign: ' + sig)
        qs = qs + '&Signature=' + sig
        return qs

    def _utc(self):
        return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')

    def _encode(self, s):
        return parse.quote(s, safe='')

class Huobi_ETH_Client():

    def __init__(self):
        self.client = ApiClient(API_KEY, API_SECRET)
        self.account_id = self._getAccountID()

    def getSymbols(self):
        logging.info('Getting symbols for client:')
        return self.client.get('/v1/common/symbols')

    def getUserInfo(self):
        logging.info('Getting user info for client:')
        return self.client.get('/v1/users/user')

    def getAllAccounts(self):
        logging.info('Getting accounts for client:')
        return self.client.get('/v1/account/accounts')

    def getETHBalance(self):
        balanceList = self.client.get('/v1/account/accounts/%s/balance' % self.account_id).list
        for line in balanceList:
            if line.currency=='eth' and line.type=='trade':
                return line.balance
        raise BaseException('ETH balance not found in account! Check ETH account!')

    def getCNYBalance(self):
        balanceList = self.client.get('/v1/account/accounts/%s/balance' % self.account_id).list
        for line in balanceList:
            if line.currency=='cny' and line.type=='trade':
                return line.balance
        raise BaseException('CNY balance not found in account! Check ETH account!')

    def printBalanceRaw(self):
        accs = self.getAllAccounts()
        logging.info('All Accounts: ')
        logging.info(accs)
        logging.info('Getting balance for client:')
        for acc in accs:
            logging.info('Getting sub account: %s' % acc)
            subaccs = self.client.get('/v1/account/accounts/%s/balance' % acc.id)
            print(subaccs)

    def getBalance(self):
        res = []
        accs = self.getAllAccounts()
        logging.info('All Accounts: ')
        logging.info(accs)
        logging.info('Getting balance for client:')
        for acc in accs:
            logging.info('Getting sub account: %s' % acc)
            subaccs = self.client.get('/v1/account/accounts/%s/balance' % acc.id)
            res.append(subaccs)
        return res

    def printBalance(self):
        accs = self.getAllAccounts()
        logging.info('All Accounts: ')
        logging.info(accs)
        logging.info('Getting balance for client:')
        account_id = accs[0].id
        for acc in accs:
            logging.info('Getting sub account: %s' % acc)
            subaccs = self.client.get('/v1/account/accounts/%s/balance' % acc.id)
            self._br()
            print('Account ID: %s' % account_id)
            print('#\tCurrency\tType\t\tBalance')
            for i, currency in enumerate(subaccs.list):
                print('%d\t%s\t\t%s\t\t%s' % (i+1, currency.currency, currency.type, currency.balance))
            self._br()

    def _getAccountID(self):
        return self.getAllAccounts()[0].id

    def _br(self):
        print('\n' + '-'*50 + '\n')

    def getSubmittedOrders(self):
        return self._getOrders('submitted')

    def printSubmittedOrders(self):
        logging.info('Getting submitted orders:')
        order_info = self.getSubmittedOrders()
        self._printOrders(order_info, title='ALL SUBMITTED ORDERS')

    def getCurrentOrders(self):
        return self._getOrders('submitted,partial-filled,partial-canceled')

    def printCurrentOrders(self):
        logging.info('Getting current orders:')
        order_info = self.getCurrentOrders()
        self._printOrders(order_info, title='CURRENT ORDERS')

    def getAllValidOrders(self):
        return self._getOrders('submitted,partial-filled,partial-canceled,filled,canceled')

    def printAllValidOrders(self):
        logging.info('Getting all valid orders:')
        order_info = self.getAllValidOrders()
        self._printOrders(order_info, title='ALL VALID ORDERS')

    def getFilledOrders(self):
        return self._getOrders('filled')

    def getAllOrders(self):
        return self._getOrders()

    def _getOrders(self, types='pre-submitted,submitted,partial-filled,partial-canceled,filled,canceled'):
        return self.client.get('/v1/order/orders', symbol='ethcny', states=types)

    def printAllOrders(self):
        logging.info('Getting all orders:')
        order_info = self.getAllOrders()
        self._printOrders(order_info, title='ALL ORDERS')

    def _printOrders(self, order_info, title=''):
        self._br()
        print('  ' + '~'*10 + ''.join(title) + '~'*10 +'\n')
        print('  #   Order\t    Amount\t          Price\t           Create Time         Type        Field-Amount      Field-Cash      Field-Fees       Finished Time     Source   State       Cancelled at')
        for i, line in enumerate(order_info):
            # print(line)
            print('%3d  %d\t%s\t%15s\t  %s  \t%10s\t%15s\t%15s\t%15s\t   %s\t  %s  \t%s\t%s' % (
                i+1,
                line.id,
                line.amount,
                line.price,
                datetime.fromtimestamp(line['created-at']/1000).strftime('%Y-%m-%d %H:%M:%S'),
                line.type,
                line['field-amount'],
                line['field-cash-amount'],
                line['field-fees'],
                datetime.fromtimestamp(line['finished-at']/1000).strftime('%Y-%m-%d %H:%M:%S'),
                line.source,
                line.state,
                '' if 0==line['canceled-at'] else datetime.fromtimestamp(line['canceled-at']/1000).strftime('%Y-%m-%d %H:%M:%S')
            ))
        self._br()

    def buy_ETH_limit(self):
        pass

    def createOrder(self, amount, price, direction):
        order_id = self.client.post('/v1/order/orders', {
            'account-id': self.account_id,
            'amount': amount,
            'price': price,
            'symbol': 'ethcny',
            'type': direction,
            'source': 'api'
        })
        logging.info('Printing order_id:')
        logging.info(order_id)
        return order_id

    def placeOrder(self, order_id):
        self.client.post('/v1/order/orders/%s/place' % order_id)

    def printOrderDetails(self, order_id):
        order_info = self.client.get('/v1/order/orders/%s' % order_id)
        self._printOrders([order_info], title='ORDER DETAIL of ORDER # %s' % order_id)

    def getOrderStatus(self, order_id):
        return self.client.get('/v1/order/orders/%s' % order_id).state

    def getOrderDetail(self, order_id):
        return self.client.get('/v1/order/orders/%s' % order_id)

    def isOrderSuccess(self, order_id):
        orderStatus = self.getOrderStatus(order_id)
        return orderStatus == 'filled'

    def isOrderCancelled(self, order_id):
        orderStatus = self.getOrderStatus(order_id)
        return orderStatus == 'canceled'

    def cancelOrder(self, order_id):
        return self.client.post('/v1/order/orders/%s/submitcancel' % order_id)

    def cancelAllOrders(self):
        logging.info('Canelling all current orders:')
        self.printCurrentOrders()
        orders = self.getCurrentOrders()
        for order in orders:
            order_id = order.id
            logging.info('Cancelling order # %d' % order_id)
            self.cancelOrder(order_id)
        logging.info('All orders cancelled!')

    def getWithdrawAddress(self):
        return self.client.get('/v1/dw/withdraw-legal/addresses', currency='cny')

    def create_transfer_cny_to_main(self, amount):
        withdraw_id = self.client.post('/v1/dw/withdraw-legal/create', {
            'account-id': self.account_id,
            'amount': amount,
            'currency': 'cny',
        })
        print('Printing CNY_withdraw_id:')
        print(withdraw_id)
        return withdraw_id

    def place_transfer_cny_to_main(self, withdraw_id):
        return self.client.post('/v1/dw/withdraw-legal/%s/place' % withdraw_id)

    def transfer_cny_to_main(self, amount):
        if '.' in amount and len(amount.split('.')[1]) > 2:
            raise BaseException('CNY transfer amount: Decimal part should be no more than 2-digits!')
        if float(self.getCNYBalance()) < float(amount):
            raise BaseException('Not enough CNY balance (in ETH account) to transfer!')
        transfer_id = self.create_transfer_cny_to_main(amount)
        return self.place_transfer_cny_to_main(transfer_id)

    def get_transferable_cny_from_main(self):
        return self.client.get('/v1/dw/deposit-legal/balance', currency='cny')

    def create_transfer_cny_from_main(self, amount):
        withdraw_id = self.client.post('/v1/dw/deposit-legal/create', {
            'account-id': self.account_id,
            'amount': amount,
            'currency': 'cny',
        })
        print('Printing CNY_deposit_id: %s ' % withdraw_id)
        return withdraw_id

    def place_transfer_cny_from_main(self, withdraw_id):
        return self.client.post('/v1/dw/deposit-legal/%s/place' % withdraw_id)

    def cancel_transfer_cny_from_main(self, withdraw_id):
        # INVALID
        return self.client.post('/v1/dw/deposit-legal/%s/submitcancel' % withdraw_id)

    def cancel_transfer_cny_to_main(self, withdraw_id):
        # INVALID
        return self.client.post('/v1/dw/withdraw-legal/%s/cancel' % withdraw_id)

    def get_financial_history(self):
        return self.client.get('/v1/query/finances')

    def print_financial_history(self):
        history = self.get_financial_history()
        for transaction in history:
            print(transaction)

    def transfer_cny_from_main(self, amount):
        if float(self.get_transferable_cny_from_main()) < float(amount):
            raise BaseException('Not enough CNY balance (in main account) to transfer!')
        transfer_id = self.create_transfer_cny_from_main(amount)
        return self.place_transfer_cny_from_main(transfer_id)

    def get_eth_withdraw_addresses(self):
        addresses = self.client.get('/v1/dw/withdraw-virtual/addresses', currency='eth')
        logging.info('Printing addresses:')
        logging.info(addresses)
        return addresses

    def withdraw_eth_create(self, address_id='', amount=''):
        # INVALID
        withdraw_id = self.client.post('/v1/dw/withdraw-virtual/create', {
            'address-id': address_id,
            'amount': amount,
            'trade-password': self.TRADE_PW # needs update here, trade pw is not supported by server and will return error
        })
        logging.info('Printing withdraw_id:')
        logging.info(withdraw_id)
        return withdraw_id

    def withdraw_eth_place(self, withdraw_id):
        status = self.client.post('/v1/dw/withdraw-virtual/%s/place' % withdraw_id)
        print('Withdraw ETH order placed.')
        logging.info('Printing withdraw status:')
        logging.info(status)
        return status

def main():
    huobi_eth = Huobi_ETH_Client()
    # print(type(huobi_eth.getCNYBalance()))
    # print(huobi_eth.cancel_transfer_cny_to_main(withdraw_id='45833'))
    # huobi_eth.print_financial_history()
    # huobi_eth.transfer_cny_from_main(amount='1.0')
    # print(huobi_eth.transfer_cny_to_main(amount='0.02'))
    # print(huobi_eth.get_eth_withdraw_addresses())
    # print(huobi_eth.get_transferable_cny_from_main())
    # print(huobi_eth.transfer_cny_from_main('0.01'))
    # print(huobi_eth.getCNYBalance())
    # huobi_eth.getETHBalance()
    # print(huobi_eth.transfer_cny_to_main('0.03'))
    # transfer_id = huobi_eth.create_transfer_cny_to_main('0.02')
    # print(huobi_eth.place_transfer_cny_to_main(transfer_id))
    # print(huobi_eth.getWithdrawAddress())
    # print(huobi_eth.getSymbols())
    # print(huobi_eth.getUserInfo())
    # print(huobi_eth.getAllAccounts())
    # huobi_eth.printBalance()
    # huobi_eth.printSubmittedOrders()
    # huobi_eth.printAllValidOrders()
    # huobi_eth.printAllOrders()
    # orderid = huobi_eth.createOrder(huobi_eth.account_id(), '0.001', '1600.0', 'sell-limit')
    # huobi_eth.placeOrder(orderid)
    # huobi_eth.cancelAllOrders()

if __name__ == '__main__':
    main()
