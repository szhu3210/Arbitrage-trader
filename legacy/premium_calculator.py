import huobi_eth_client
import huobi_eth_monitor
import huobi_eth_operator
import huobi_main_monitor
from poloniex import Poloniex

def getPrices():
    prices = {}

    # get cny usd
    prices['cnyusd'] = huobi_main_monitor.Huobi_Main_Monitor().get_cnyusd_bid_price()['rates']['CNY']

    # get huobi market prices: sell eth, sell ltc, buy btc.
    prices['btccny-huobi'] = float(huobi_main_monitor.Huobi_Main_Monitor().get_btccny_ask_price())
    prices['ltccny-huobi'] = float(huobi_main_monitor.Huobi_Main_Monitor().get_ltccny_bid_price())
    prices['ethcny-huobi'] = float(huobi_eth_monitor.Huobi_ETH_Monitor().getAverageBidsGivenSize(10)[1])
    prices['ethbtc-huobi'] = prices['ethcny-huobi'] / prices['btccny-huobi']
    prices['ltcbtc-huobi'] = prices['ltccny-huobi'] / prices['btccny-huobi']

    # get Poloniex market prices:
    prices['ethbtc-poloniex'] = float(Poloniex().returnTicker()['BTC_ETH']['lowestAsk'])
    prices['ltcbtc-poloniex'] = float(Poloniex().returnTicker()['BTC_LTC']['lowestAsk'])

    # get Coinbase market prices:

    return prices

def getPremiums():
    prices = getPrices()
    # check premium of btc, eth, ltc between huobi and poloniex and coinbase
    premiums = {}
    premiums['ethbtc'] = (prices['ethbtc-huobi']-prices['ethbtc-poloniex']) / prices['ethbtc-poloniex']
    premiums['ltcbtc'] = (prices['ltcbtc-huobi']-prices['ltcbtc-poloniex']) / prices['ltcbtc-poloniex']

    return premiums

if __name__=='__main__':
    print(getPrices())
    print(getPremiums())