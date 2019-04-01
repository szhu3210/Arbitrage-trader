from poloniex import Poloniex

class Poloniex_Monitor():
    def get_tick_price(self):
        return Poloniex().returnTicker()

if __name__=='__main__':
    print(Poloniex_Monitor().get_tick_price())