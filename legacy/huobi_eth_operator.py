#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import huobi_eth_client
import huobi_eth_monitor
import time
import logging
logging.basicConfig(level=logging.WARNING)

class ETH_operator():

    def sellETH(self, amount=''):

        huobi_eth_client_1 = huobi_eth_client.Huobi_ETH_Client()
        huobi_eth_monitor_1 = huobi_eth_monitor.Huobi_ETH_Monitor()

        # Amount to sell
        logging.warning('Amount to sell: %s' % amount)

        # Check balance
        balance_ETH = huobi_eth_client_1.getETHBalance()
        if amount <= balance_ETH:
            balanceOkay = True
        else:
            balanceOkay = False
        logging.warning('Current ETH balance: %s' % balance_ETH)
        logging.warning('Checking ETH balance: %s' % 'PASSED!' if balanceOkay else 'FAILED!')

        # Check sell price and avgPrice
        huobi_eth_monitor_1.printBids()
        marketAvailable, avgPrice, sellPrices = huobi_eth_monitor_1.getAverageBidsGivenSize(float(amount)*2) # reserve enough market
        print(marketAvailable, avgPrice, sellPrices)

        logging.warning('Average Sold Price (estimated): %s' % avgPrice)

        sellPrice = '%.2f' % (sellPrices[-1][0] * 0.99) # lower sellPrice by 1 % to ensure trade success
        logging.warning('Set Sell Price: %s ' % sellPrice)

        # Sell ETH
        if balanceOkay:
            if marketAvailable==True:
                # Create order and place order
                price = sellPrice
                direction = 'sell-limit'
                order_id = huobi_eth_client_1.createOrder(amount, price, direction)
                huobi_eth_client_1.placeOrder(order_id)

                # Check order status, if success report
                count = 0
                while count<=6:
                    if huobi_eth_client_1.isOrderSuccess(order_id):
                        logging.warning('Order Successfully Filled!')
                        huobi_eth_client_1.printOrderDetails(order_id)
                        break
                    time.sleep(5)
                    count += 1
                if count>6: # order not placed within 30 seconds
                    logging.warning('Order Failed! The following is detailed info.')
                    huobi_eth_client_1.printOrderDetails(order_id)
                    logging.warning('Cancelling order...')
                    huobi_eth_client_1.cancelOrder(order_id)
                    time.sleep(1)
                    if huobi_eth_client_1.isOrderCancelled(order_id):
                        logging.warning('Order cancelled successfully!')
                    else:
                        logging.warning('Please check if the order is cancelled. Manually handle exceptions.')
                        # raise 'Exception: order not canceled successfully!'
                    huobi_eth_client_1.printOrderDetails(order_id)
                return huobi_eth_client_1.getOrderDetail(order_id)
            else:
                logging.warning('No enough market for selling ETH of amount %s' % amount)
        else:
            logging.warning('No enough available ETH balance!')
            huobi_eth_client_1.printBalance()