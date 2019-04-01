import premium_calculator
import time
import huobi_eth_client
import huobi_eth_operator
import huobi_main_client
import huobi_main_operator
import poloniex_client
import transfer_btc
import transfer_eth
import email_client

import logging
logging.basicConfig(level=logging.WARNING)

PREMIUM_THRESHOLD = 0.01

class Arbitrage_Trader_ETH_BTC_Huobi_Poloniex():

    def __init__(self):
        pass

    def cal_assets(self, balances=None):

        cny = 0.0
        cny += float(balances['huobi_main']['available_cny_display'])
        print('Asset: CNY, Account: Huobi_Main_Available, Amount: %s' % balances['huobi_main']['available_cny_display'])
        cny += float(balances['huobi_main']['frozen_cny_display'])
        print('Asset: CNY, Account: Huobi_Main_Frozen, Amount: %s' % balances['huobi_main']['frozen_cny_display'])
        print(balances['huobi_eth'][0]['list'])
        temp = [acc['balance'] for acc in balances['huobi_eth'][0]['list'] if acc['currency'] == 'cny']
        cny += sum(map(float, temp))
        print('Asset: CNY, Account: Huobi_ETH_All, Amount: %s' % temp)
        print('Asset: CNY, Total: %.2f' % cny)

        btc = 0.0
        print('Asset: BTC, Account: Huobi_Main_Available, Amount: %s' % balances['huobi_main']['available_btc_display'])
        btc += float(balances['huobi_main']['available_btc_display'])
        print('Asset: BTC, Account: Huobi_Main_Frozen, Amount: %s' % balances['huobi_main']['frozen_btc_display'])
        btc += float(balances['huobi_main']['frozen_btc_display'])
        print('Asset: BTC, Account: Poloniex, Amount: %s' % balances['poloniex']['BTC'])
        btc += float(balances['poloniex']['BTC'] if 'BTC' in balances['poloniex'] else '0.0')
        print('Asset: BTC, Total: %.4f' % btc)

        eth = 0.0
        temp = [acc['balance'] for acc in balances['huobi_eth'][0]['list'] if acc['currency'] == 'eth']
        eth += sum(map(float, temp))
        print('Asset: ETH, Account: Huobi_ETH_All, Amount: %s' % temp)
        eth += float(balances['poloniex']['ETH'] if 'ETH' in balances['poloniex'] else '0.0')
        print('Asset: ETH, Account: Poloniex, Amount: %s' % balances['poloniex']['ETH'])
        print('Asset: ETH, Total: %.4f' % eth)

        assets = {}
        assets['cny'] = cny
        assets['btc'] = btc
        assets['eth'] = eth

        return assets

    def cal_profits(self, balances_old=None, balances_new=None):

        """
        Old balances:
        {'huobi_main': {'total': '18594.71', 'net_asset': '18594.71', 'available_cny_display': '68.99',
                        'available_btc_display': '0.9781', 'available_ltc_display': '0.0000',
                        'frozen_cny_display': '20.00', 'frozen_btc_display': '0.0000', 'frozen_ltc_display': '0.0000',
                        'loan_cny_display': '0.00', 'loan_btc_display': '0.0000', 'loan_ltc_display': '0.0000'},
         'huobi_eth': [{'id': 191213, 'type': 'spot', 'state': 'working',
                        'list': [{'currency': 'cny', 'type': 'trade', 'balance': '0.8771764855'},
                                 {'currency': 'cny', 'type': 'frozen', 'balance': '168.3715730000'},
                                 {'currency': 'eth', 'type': 'trade', 'balance': '4.8359434300'},
                                 {'currency': 'eth', 'type': 'frozen', 'balance': '0.0000000000'}]}],
         'poloniex': ['  BTC  0.02127211', '  ETH 0.10034348']}
        New balances:
        {'huobi_main': {'total': '18716.36', 'net_asset': '18716.36', 'available_cny_display': '69.79',
                        'available_btc_display': '0.9803', 'available_ltc_display': '0.0000',
                        'frozen_cny_display': '20.00', 'frozen_btc_display': '0.0000', 'frozen_ltc_display': '0.0000',
                        'loan_cny_display': '0.00', 'loan_btc_display': '0.0000', 'loan_ltc_display': '0.0000'},
         'huobi_eth': [{'id': 191213, 'type': 'spot', 'state': 'working',
                        'list': [{'currency': 'cny', 'type': 'trade', 'balance': '0.8326764855'},
                                 {'currency': 'cny', 'type': 'frozen', 'balance': '168.3715730000'},
                                 {'currency': 'eth', 'type': 'trade', 'balance': '4.8109434300'},
                                 {'currency': 'eth', 'type': 'frozen', 'balance': '0.0000000000'}]}],
         'poloniex': ['  BTC  0.01894709', '  ETH 0.12528098']}
        """

        # calculate profit results and put in report

        # total asset before and after arbitrage
        assets_old = self.cal_assets(balances_old)
        assets_new = self.cal_assets(balances_new)
        print('Old Assets: \n%s' % assets_old)
        print('New Assets: \n%s' % assets_new)

        # profit of cny and btc and eth
        profits = {}
        for currency in ('cny', 'btc', 'eth'):
            profits[currency] = assets_new[currency] - assets_old[currency]
        return profits

    def get_balances(self):
        balances = {}
        balances['huobi_main'] = huobi_main_client.Huobi_Main_Client().getAccountInfo()
        balances['huobi_eth'] = huobi_eth_client.Huobi_ETH_Client().getBalance()
        balances['poloniex'] = poloniex_client.Poloniex_Client().get_available_balances()
        return balances

    def execute_positive_premium_arbitrage(self, eth_trade_amount=''):
        # return execution status
        print('=' * 50 + ' S T A R T ' + '=' * 50)
        print('Executing positive premium arbitrage:')

        # Phase 0: record balances
        print('\nPhase 0: Record balances:')
        balances_old = self.get_balances()
        print('Current balances (before arbitrage): %s' % balances_old)

        # Phase 1: get balances and calculate amount
        print('\nPhase 1: Get balances and verify trade amount:')
        # test_amount = '0.01' # test amount is 1 ETH
        # eth_trade_amount = test_amount
        print('ETH trade amount: %s' % eth_trade_amount)
        eth_balance_huobi = huobi_eth_client.Huobi_ETH_Client().getETHBalance()
        print('Current ETH balance in Huobi:      %s' % eth_balance_huobi)
        btc_balance_poloniex = poloniex_client.Poloniex_Client().get_balance('BTC')
        print('Current BTC balance in poloniex:   %s' % btc_balance_poloniex)
        eth_affordable_amount = float(btc_balance_poloniex) / float(poloniex_client.Poloniex_Client().client.returnTicker()['BTC_ETH']['lowestAsk'])
        print('Affordable ETH amount in poloniex: %.4f' % eth_affordable_amount)
        eth_max_amount = min(float(eth_balance_huobi), eth_affordable_amount)
        print('Maximum ETH purchase amount: %.4f ' % eth_max_amount)
        if float(eth_trade_amount) < eth_max_amount:
            print('Balance verification: PASS!')
        else:
            print('Not enough balance to trade!')
            raise BaseException('Insufficient trade balance !')

        # Phase 2: Sell ETH in huobi and buy ETH in poloniex
        print('\nPhase 2: Sell ETH in huobi and buy ETH in poloniex')

        print('Selling ETH in huobi: amount = %s' % eth_trade_amount)
        eth_sell_order_detail = huobi_eth_operator.ETH_operator().sellETH(amount=eth_trade_amount)

        cny_transfer_amount = '%.2f' % float(eth_sell_order_detail['field-cash-amount'])
        print('Transferring CNY to huobi main account: amount = %s' % cny_transfer_amount)
        huobi_eth_client.Huobi_ETH_Client().transfer_cny_to_main(amount=cny_transfer_amount)

        print('Buying ETH in poloniex:')
        eth_purchase_order_status = poloniex_client.Poloniex_Client().buy_ETH(amount=eth_trade_amount)
        btc_spent_in_eth_purchase = sum([float(subtrade['total']) for subtrade in eth_purchase_order_status['resultingTrades']])

        btc_trade_amount = str('%.4f' % float(btc_spent_in_eth_purchase))
        print('Buying BTC in huobi: amount = %s' % btc_trade_amount)
        huobi_main_operator.Huobi_Main_Operator().buy_BTC(amount=btc_trade_amount)

        # Phase 3: Transfer BTC and ETH back
        print('\nPhase 3: Transfer BTC and ETC back')
        print('Transferring BTC back to Poloniex: amount = %s' % btc_trade_amount)
        if float(btc_trade_amount) <= 0.1:
            print('The BTC amount for transfer is too small! No need to transfer.\n(Huobi requires at least 0.01 BTC for transfer.)')
        else:
            transfer_btc.Transfer_BTC().transfer_btc_from_huobi_to_poloniex(amount=btc_trade_amount)

        print('Transferring ETH back to Huobi: amount = %s' % eth_trade_amount)
        if float(eth_trade_amount) <= 1.0:
            print('The ETH amount for transfer is too small! No need to transfer.\n')
        else:
            transfer_eth.Transfer_ETH().transfer_eth_from_poloniex_to_huobi(amount=eth_trade_amount)

        # Report arbitrage
        print('Arbitrage successfully proceeded! ETH amount = %s' % eth_trade_amount)

        # Phase 4: Report
        print('\nPhase 4: Report')
        print('Getting balances:')
        balances_new = self.get_balances()
        print('Current balances (after arbitrage): %s' % balances_new)

        profit_report = str(self.cal_profits(balances_old=balances_old, balances_new=balances_new))
        print('Profit Report: \n%s' % profit_report)

        print('Report by email...')
        try:
            email_client.Email_client().notify_me_by_email(title='Arbitrage (ETH, positive premium) successfully proceeded!', content='ETH amount: %s \nOld balances: \n%s \nNew balances: \n%s\n\n Profit Report: \n %s' % (eth_trade_amount, balances_old, balances_new, profit_report))
            print('Email was sent.')
        except:
            print('Email was not sent.')

        print('=' * 50 + ' E N D ' + '=' * 50)

        return 'Execution status: SUCCESS'

    def execute_negative_premium_arbitrage(self):
        # return execution status
        pass

    def run(self):
        while 1:

            # keep watching market opportunities and take action

            # Get premium
            premium = premium_calculator.getPremiums()['ethbtc']

            # Take action
            if premium > PREMIUM_THRESHOLD:
                print('Premium is high than %.2f, execute positive premium arbitrage:' % PREMIUM_THRESHOLD)
                status = self.execute_positive_premium_arbitrage(eth_trade_amount='0.5')
                print('Execution result: %s' % status)
            elif premium < -PREMIUM_THRESHOLD:
                # print('Premium is lower than %.2f, execute negative premium arbitrage:' % -PREMIUM_THRESHOLD)
                # status = self.execute_negative_premium_arbitrage()
                # print('Execution result: %s' % status)
                # The premium is calculated only for positive one so negative one is not suitable.
                pass
            else:
                print('Premium is %.2f, not reach threshold.' % premium)
                pass

            # wait for 1 minute (?)
            time.sleep(60)

if __name__=='__main__':

    # poloniex_client.Poloniex_Client().client.returnOrderTrades(eth_purchase_order_number)[0]['total']
    # balances = Arbitrage_Trader_ETH_BTC_Huobi_Poloniex().get_balances()
    # print(balances)
    # print(Arbitrage_Trader_ETH_BTC_Huobi_Poloniex().cal_assets(balances=balances))
    # print(Arbitrage_Trader_ETH_BTC_Huobi_Poloniex().cal_profits(balances_old=balances, balances_new=balances))
    # Arbitrage_Trader_ETH_BTC_Huobi_Poloniex().execute_positive_premium_arbitrage(eth_trade_amount='0.3') # minimum amount: 0.02 ETH for trading and 0.2 ETH if needs transfer back
    pass