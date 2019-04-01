import poloniex

class Poloniex_Client():
    def __init__(self):
        self.client = poloniex.Poloniex(public_key, secret_key)

    def get_balances(self):
        return self.client.returnBalances()


    def get_available_balances(self):
        res = {}
        balances = self.get_balances()
        for c in balances:
            if float(balances[c]) != 0:
                res[c] = balances[c]
        return res

    def print_available_balances(self):
        balances = self.get_balances()
        for c in balances:
            if float(balances[c]) != 0:
                print('%5s  %10s' % (c, balances[c]))

    def get_balance(self, currency='BTC'):
        return self.get_balances()[currency]

    def _buy_ETH(self, amount='', rate='', order_type='fillOrKill'):
        return self.client.buy(currencyPair='BTC_ETH', rate=rate, amount=amount, orderType=order_type)

    def get_eth_asks(self):
        return self.client.returnOrderBook('BTC_ETH', depth=20)

    def cal_buy_price(self, size):
        size = float(size)
        asks = self.get_eth_asks()['asks']
        print(asks)
        total = 0
        rest = size
        priceRange = []
        for ask in asks:
            price_s, volume_s = ask
            price, volume = map(float, ask)
            if volume>rest:
                total += price*rest
                priceRange.append([price_s, rest])
                rest = 0
                break
            total += price*volume
            rest -= volume
            priceRange.append(ask)
        status = (rest <= 0)
        return status, '%.4f' % (total/size), priceRange

    def buy_ETH(self, amount='0'):
        print(self.get_eth_asks())
        balance_BTC = self.get_balance('BTC')
        marketAvailable, avgPrice, priceRange = self.cal_buy_price(float(amount)*2) # reserve enough market space
        price = '%.8f' % (float(priceRange[-1][0]) * 1.01) # buy price, raise 1 % limit to ensure trade success
        if float(balance_BTC) > float(price)*float(amount)*1.01: # check balance of BTC
            if marketAvailable: # check market status (if it is big enough for this order)
                print('Buying ETH: amount = %s, price = %s, total = %.6f' % (amount, price, float(price)*float(amount)))
                order = self._buy_ETH(amount=amount, rate=price)
                deal_amount = str(sum([float(trade['amount']) for trade in order['resultingTrades']]))
                print(order)
                print('Traded amount: %s / %s (%.0f%%)' % (deal_amount, amount, 100*float(deal_amount)/float(amount)))
                if abs(float(deal_amount)-float(amount))/float(amount)<0.01: # more than 99% of orders are dealed
                    print('Order successfully traded!')
                else:
                    print('Order is good but trade failed! Please handle exceptions manually.')
                return order
            else:
                print('Market not enough for buying ETH of amount %s.' % amount)
        else:
            print('Not enough balance available to buy ETH of amount %s.' % amount)
        print('Order failed. Please handle exceptions manually.')

if __name__=='__main__':
    trader = Poloniex_Client()
    # print(trader.cal_buy_price(size='20'))
    # trader.print_available_balances()
    # order_status = trader.buy_ETH(amount='0.0021')
    # print(order_status)
    # print(trader.client.returnOrderTrades('299426069353'))
    print(trader.get_available_balances())
    pass