# coding=utf-8

import huobi_main_client
import huobi_main_monitor
import logging
import time

class Huobi_Main_Operator():

    def buy_BTC(self, amount=''): # amount here is the amount of BTC

        huobi_main_client_1 = huobi_main_client.Huobi_Main_Client()
        huobi_main_monitor_1 = huobi_main_monitor.Huobi_Main_Monitor()

        # Amount to buy
        logging.warning('Amount to buy: %s' % amount)

        # Check buy price and avgPrice
        marketAvailable, avgPrice, buyPrices = huobi_main_monitor_1.getAverageAsksGivenSize(float(amount)*2) # reserve enough market
        print(marketAvailable, avgPrice, buyPrices)

        logging.warning('Average Bought Price (estimated): %s' % avgPrice)

        buyPrice = '%.2f' % ((buyPrices[-1][0]) * 1.01) # raise buy limit price by 1% to ensure trade success
        logging.warning('Set Buy Price: %s ' % buyPrice)

        # Check balance
        balance_CNY = huobi_main_client_1.getAccountInfo()['available_cny_display']
        if float(amount) * float(buyPrice) * 1.002 <= float(balance_CNY):
            balanceOkay = True
        else:
            balanceOkay = False
        logging.warning('Current CNY balance: %s' % balance_CNY)
        logging.warning('Estimated CNY for buying %s BTC: %.2f' % (amount, float(amount) * float(buyPrice) * 1.002))
        logging.warning('Checking CNY balance: %s' % 'PASSED!' if balanceOkay else 'FAILED!')

        # Buy BTC
        if balanceOkay:
            if marketAvailable:
                # Make order
                price = buyPrice
                order_status = huobi_main_client_1.buy(coinType=1, price=price, amount=amount)
                print(order_status)
                order_id = order_status['id']

                # Check order status, if success report
                count = 0
                while count<=2:
                    if huobi_main_client_1.is_btc_order_success(order_id):
                        logging.warning('Order Successfully Filled!')
                        print(huobi_main_client_1.getOrderInfo(1, order_id))
                        break
                    time.sleep(5)
                    count += 1
                if count>2: # order not placed within 10 seconds
                    logging.warning('Order Failed! The following is detailed info.')
                    logging.warning(huobi_main_client_1.getOrderInfo(1, order_id))
                    logging.warning('Cancelling order...')
                    huobi_main_client_1.cancelOrder(1, order_id)
                    time.sleep(1)
                    if huobi_main_client_1.is_btc_order_cancelled(order_id):
                        logging.warning('Order cancelled successfully!')
                    else:
                        logging.warning('Please check if the order is cancelled. Manually handle exceptions.')
                        # raise 'Exception: order not canceled successfully!'
                    print(huobi_main_client_1.getOrderInfo(1, order_id))
                return huobi_main_client_1.getOrderInfo(1, order_id)
            else:
                logging.warning('No enough market for buying BTC of amount %s' % amount)
        else:
            logging.warning('No enough available CNY balance!')
            huobi_main_client_1.printAccountInfo()

if __name__ == "__main__":
    pass
    # Huobi_Main_Operator().buy_BTC('0.001')
    # client = huobi_main_client.Huobi_Main_Client()
    # print("获取账号详情")
    # print(client.getAccountInfo())
    # client.printAccountInfo()
    # print("获取所有正在进行的委托")
    # print(client.getOrders(1)) # 1 BTC, 2 LTC
    # print(client.get_LTC_orders())
    # print("限价买入")
    # order_id = client.buy(1, "1", "0.001")
    # print(order_id)
    # print(client.get_BTC_orders())
    # print("获取订单详情")
    # print(client.getOrderInfo(1, order_id['id']))
    # print("限价卖出")
    # print(client.sell(1, "1000000", "0.001"))
    # client.getOrders(1)
    # # print("市价买入")
    # # print(client.buyMarket(1, "1.00"))
    # # print("市价卖出")
    # # print(client.sellMarket(1, "1.00"))
    #
    # print("查询个人最新10条成交订单")
    # print(client.getNewDealOrders(1))
    # print("根据trade_id查询order_id")
    # print(client.getOrderIdByTradeId(1, 274424))
    # print("取消订单接口")
    # print(client.cancelOrder(1, 4455362932))
    # print(client.get_BTC_orders())