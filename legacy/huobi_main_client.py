# coding=utf-8
import hashlib
import time
import urllib
import urllib.parse
import urllib.request
import json

HUOBI_SERVICE_API = "https://api.huobi.com/apiv3"

class Huobi_Main_Client():

    def __init__(self):
        # 在此输入您的Key
        pass

    def _send2api(self, pParams, extra):
        pParams['access_key'] = self.ACCESS_KEY
        pParams['created'] = int(time.time())
        pParams['sign'] = self._createSign(pParams)
        if (extra):
            for k in extra:
                v = extra.get(k)
                if (v != None):
                    pParams[k] = v
                    # pParams.update(extra)
        tResult = self._httpRequest(HUOBI_SERVICE_API, pParams)
        return tResult

    def _createSign(self, params):
        params['secret_key'] = self.SECRET_KEY
        params = sorted(params.items(), key=lambda d: d[0], reverse=False)
        message = urllib.parse.urlencode(params)
        message = message.encode(encoding='UTF8')
        m = hashlib.md5()
        m.update(message)
        m.digest()
        sig = m.hexdigest()
        return sig

    def _httpRequest(self, url, params):
        postdata = urllib.parse.urlencode(params)
        postdata = postdata.encode('utf-8')

        fp = urllib.request.urlopen(url, postdata)
        if fp.status != 200:
            return None
        else:
            mybytes = fp.read()
            mystr = mybytes.decode("utf8")
            fp.close()
            return json.loads(mystr)

    def getAccountInfo(self):
        params = {"method": "get_account_info"}
        extra = {}
        res = self._send2api(params, extra)
        return res

    def getOrders(self, coinType):
        params = {"method": "get_orders"}
        params['coin_type'] = coinType
        extra = {}
        res = self._send2api(params, extra)
        return res

    def getOrderInfo(self, coinType, id):
        params = {"method": "order_info"}
        params['coin_type'] = coinType
        params['id'] = id
        extra = {}
        res = self._send2api(params, extra)
        return res

    def buy(self, coinType=None, price='', amount=''):
        params = {"method": 'buy'}
        params['coin_type'] = coinType
        params['price'] = price
        params['amount'] = amount
        extra = {}
        res = self._send2api(params, extra)
        return res

    def sell(self, coinType, price, amount):
        params = {"method": 'sell'}
        params['coin_type'] = coinType
        params['price'] = price
        params['amount'] = amount
        extra = {}
        res = self._send2api(params, extra)
        return res

    def buyMarket(self, coinType, amount):
        params = {"method": 'buy_market'}
        params['coin_type'] = coinType
        params['amount'] = amount
        extra = {}
        res = self._send2api(params, extra)
        return res

    def sellMarket(self, coinType, amount):
        params = {"method": 'sell_market'}
        params['coin_type'] = coinType
        params['amount'] = amount
        extra = {}
        res = self._send2api(params, extra)
        return res

    def getNewDealOrders(self, coinType):
        params = {"method": "get_new_deal_orders"}
        params['coin_type'] = coinType
        extra = {}
        res = self._send2api(params, extra)
        return res

    def getOrderIdByTradeId(self, coinType, tradeid):
        params = {"method": "get_order_id_by_trade_id"}
        params['coin_type'] = coinType
        params['trade_id'] = tradeid
        extra = {}
        res = self._send2api(params, extra)
        return res

    def cancelOrder(self, coinType, id):
        params = {"method": 'cancel_order'}
        params['coin_type'] = coinType
        params['id'] = id
        extra = {}
        res = self._send2api(params, extra)
        return res

    def _br(self):
        print('-'*50)

    def printAccountInfo(self):
        info = self.getAccountInfo()
        self._br()
        print('Account Balances:')
        for name in info:
            print('%30s  %10s' % (name, info[name]))
        self._br()

    def get_BTC_orders(self):
        return self.getOrders(1)

    def get_LTC_orders(self):
        return self.getOrders(2)

    def withdraw_btc_to_btc_address(self, withdraw_address, amount):
        if float(amount)<0.01:
            raise BaseException('Transfer amount should be larger than 0.01 BTC!')
        params = {"method": 'withdraw_coin'}
        params['coin_type'] = 1
        params['withdraw_address'] = withdraw_address
        params['withdraw_amount'] = amount
        extra = {'trade_password': self.TRADE_PW}
        res = self._send2api(params, extra)
        return res

    def get_withdraw_status(self, withdraw_id):
        params = {"method": 'get_withdraw_coin_result'}
        params['withdraw_coin_id'] = withdraw_id
        extra = {}
        res = self._send2api(params, extra)
        return res

    def get_withdraw_status_all(self):
        # INVALID
        params = {"method": 'get_withdraw_coin_requests'}
        params['withdraw_coin_id'] = ''
        extra = {}
        res = self._send2api(params, extra)
        return res

    def cancel_withdraw(self, withdraw_id):
        params = {"method": 'cancel_withdraw_coin'}
        params['withdraw_coin_id'] = withdraw_id
        extra = {}
        res = self._send2api(params, extra)
        return res

    def get_deposit_address(self):
        # INVALID
        params = {"method": 'get_deposit_coin_address'}
        # params['withdraw_coin_id'] = ''
        extra = {}
        res = self._send2api(params, extra)
        return res

    def get_btc_new_deal_orders(self):
        params = {"method": 'get_new_deal_orders', 'coin_type': 1}
        extra = {}
        res = self._send2api(params, extra)
        return res

    def is_btc_order_success(self, order_id):
        return self.getOrderInfo(1, order_id)['status'] == 2

    def is_btc_order_cancelled(self, order_id):
        return self.getOrderInfo(1, order_id)['status'] in [3, 6]

if __name__ == '__main__':
    pass
    # print(Huobi_Main_Client().buy(1, '0.01', '1.0'))
    # print(Huobi_Main_Client().is_btc_order_success('4461311025'))
    # print(Huobi_Main_Client().getOrderInfo(1, '4461311025'))
    # print(Huobi_Main_Client().get_btc_new_deal_orders())
    # Huobi_Main_Client().getOrderInfo()
    # Huobi_Main_Client().withdraw_btc_to_btc_address('', '0.01')
    # print(Huobi_Main_Client().get_withdraw_status_all())
    # print(Huobi_Main_Client().get_withdraw_status('3289309'))
    # print(Huobi_Main_Client().cancel_withdraw('3289312'))
    print(Huobi_Main_Client().getAccountInfo())
    # print(Huobi_Main_Client().get_deposit_address())