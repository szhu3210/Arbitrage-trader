import huobi_main_client
import poloniex_client
import email_client


class Transfer_BTC():

    def transfer_btc_from_huobi_to_poloniex(self, amount=''):

        print('Start Transferring BTC from Huobi to Poloniex...')

        # get deposit address from poloniex and make sure it is the same as the recorded one
        print('Getting Poloniex deposit address:')
        poloniexDepositAddress = poloniex_client.Poloniex_Client().client.returnDepositAddresses()['BTC']
        print('Deposit address returned from Poloniex:  %s' % poloniexDepositAddress)
        print('Deposit address in local record:         %s' % POLONIEX_BTC_DEPOSIT_ADDRESS)
        isAddressSame = poloniexDepositAddress == POLONIEX_BTC_DEPOSIT_ADDRESS
        if isAddressSame:
            print('Deposit address verification result: PASS!')
        else:
            print('Deposit address verification result: FAILED! Please check Poloniex deposit address manually and update in local record!')
            raise BaseException('Deposit address not the same as record')

        # transfer amount from Huobi to Poloniex
        print('Transferring BTC from Huobi to Poloniex:')
        status = huobi_main_client.Huobi_Main_Client().withdraw_btc_to_btc_address(poloniexDepositAddress, amount)
        if status['code']==200 and status['message']=='OK':
            print('Transfer status: OK! Status: %s' % status)
        else:
            print('Transfer status: ERROR! Status: %s' % status)
            raise BaseException('Transfer error! Status: %s' % status)

        # return status
        withdraw_id = status['withdraw_coin_id']
        print('Transfer SUCCESS! Amount: %s BTC, Withdraw_ID: %s' % (amount, withdraw_id))
        return withdraw_id

    def transfer_btc_from_poloniex_to_huobi(self, amount=''):

        print('Start Transferring BTC from Poloniex to Huobi...')

        # get deposit address from huobi and make sure it is the same as the recorded one
        print('Getting Huobi deposit address:')
        print('Deposit address in local record: %s' % HUOBI_BTC_DEPOSIT_ADDRESS)
        print('Since the address cannot be verified, please go to the website to verify the address!')

        # send email about the transfer address
        try:
            print('Sending caution email:')
            email_client.Email_client().notify_me_by_email(title='Caution about BTC deposit address in Huobi.', content='BTC is being transferred from Poloniex to Huobi.\n Amount: %s \nBTC deposit address of Huobi cannot be verified. Please check manually.' % amount)
            print('Email sent successfully!')
        except:
            print('Email sent FAILED.')

        # transfer amount from Poloniex to Huobi
        print('Transferring BTC from Poloniex to Huobi:')
        status = poloniex_client.Poloniex_Client().client.withdraw(currency='BTC', amount=amount, address=HUOBI_BTC_DEPOSIT_ADDRESS)
        print('Returned response: \"%s\"' % status['response'])
        print('Expected response: \"%s\"' % 'Withdrew %.8f BTC.' % float(amount))
        if status['response'] == 'Withdrew %.8f BTC.' % float(amount):
            print('Transfer status: OK! Status: %s' % status)
        else:
            print('Transfer status: ERROR! Status: %s' % status)
            raise BaseException('Transfer error! Status: %s' % status)

        # return status
        print('Transfer SUCCESS! Amount: %s BTC' % amount)
        return True

if __name__ == '__main__':
    # withdraw_id = Transfer_BTC().transfer_btc_from_huobi_to_poloniex('0.01')
    # print(huobi_main_client.Huobi_Main_Client().cancel_withdraw(withdraw_id))
    # print(Transfer_BTC().transfer_btc_from_poloniex_to_huobi('0.3901'))
    pass
