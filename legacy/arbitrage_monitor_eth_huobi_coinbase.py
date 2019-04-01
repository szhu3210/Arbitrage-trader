from coinbase.wallet.client import Client
import huobi_main_monitor
import time
import email_client

class Arbitrage_BTC():

    def calculate_premium(self):

        # get coinbase price
        coinbase_monitor = Client(api_key='admin', api_secret='admin')
        coinbase_price = float(coinbase_monitor.get_buy_price()['amount'])
        print('BTC price in Coinbase:   %.2f USD' % coinbase_price)

        # get huobi price
        huobi_monitor = huobi_main_monitor.Huobi_Main_Monitor()
        huobi_price = float(huobi_monitor.get_btccny_bid_price())
        print('BTC price in Huobi:      %.2f CNY' % huobi_price)

        # get exchange rate
        exchange_rate = float(coinbase_monitor.get_exchange_rates()['rates']['CNY'])
        print('Exchange rate is now:    %.2f CNY/USD' % exchange_rate)

        # cal premium (huobi -> coinbase)
        premium = huobi_price / exchange_rate - coinbase_price
        premium_rate = premium / coinbase_price
        print('Premium: %.2f USD\nPremium Rate: %.1f %%' % (premium, premium_rate*100))

        return premium_rate

def main():
    while 1:
        rate = Arbitrage_BTC().calculate_premium()
        if abs(rate)>0.05:
            try:
                email_client.Email_client().notify_me_by_email(title='BTC premium is profittable!', content='Premium rate is now: %.1f %%' % (rate*100))
                print('Email sent successfully!')
                time.sleep(15*60)
            except:
                print('Email not sent! Try again in 1 minute...')
                time.sleep(60)
                continue
        time.sleep(60)

if __name__ == '__main__':
    main()