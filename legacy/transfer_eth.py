import huobi_eth_client
import poloniex_client
import email_client


class Transfer_ETH():

    def transfer_eth_from_huobi_to_poloniex(self, amount=''):
        # INVALID: the method of withdraw eth needs trade pw which is not yet supported by the server

        print('Start Transferring ETH from Huobi to Poloniex...')

        # get deposit address from poloniex and make sure it is the same as the recorded one
        print('Getting Poloniex deposit address:')
        poloniexDepositAddress = poloniex_client.Poloniex_Client().client.returnDepositAddresses()['ETH']
        print('Deposit address returned from Poloniex:  %s' % poloniexDepositAddress)
        print('Deposit address in local record:         %s' % POLONIEX_ETH_DEPOSIT_ADDRESS)
        isAddressSame = poloniexDepositAddress == POLONIEX_ETH_DEPOSIT_ADDRESS
        if isAddressSame:
            print('Deposit address verification result: PASS!')
        else:
            print('Deposit address verification result: FAILED! Please check Poloniex deposit address manually and update in local record!')
            raise BaseException('Deposit address not the same as record')

        # transfer amount from Huobi to Poloniex
        print('Transferring ETH from Huobi to Poloniex:')

        # get address id in eth reserved withdraw address
        addresses = huobi_eth_client.Huobi_ETH_Client().get_eth_withdraw_addresses()
        # print(addresses)
        address_id = ''
        for address in addresses:
            if ('0x' + address['address']) == POLONIEX_ETH_DEPOSIT_ADDRESS:
                address_id = address['id']
                break
        if not address_id:
            raise BaseException('Address id not found!')

        # transfer using withdraw address id
        withdraw_id = huobi_eth_client.Huobi_ETH_Client().withdraw_eth_create(address_id, amount='0.01')
        status = huobi_eth_client.Huobi_ETH_Client().withdraw_eth_place(withdraw_id)
        if status['status']=='ok':
            print('Transfer status: OK! Status: %s' % status)
        else:
            print('Transfer status: ERROR! Status: %s' % status)
            raise BaseException('Transfer error! Status: %s' % status)

        # return status
        withdraw_id = status['data']
        print('Transfer SUCCESS! Amount: %s BTC, Withdraw_ID: %s' % (amount, withdraw_id))
        return withdraw_id

    def transfer_eth_from_poloniex_to_huobi(self, amount=''):
        print('Start Transferring ETH from Poloniex to Huobi...')

        # get deposit address from huobi and make sure it is the same as the recorded one
        print('Getting Huobi deposit address:')
        print('Deposit address in local record: %s' % HUOBI_ETH_DEPOSIT_ADDRESS)
        print('Since the address cannot be verified, please go to the website to verify the address!')

        # send email about the transfer address
        try:
            print('Sending caution email:')
            email_client.Email_client().notify_me_by_email(title='Caution about ETH deposit address in Huobi.', content='BTC is being transferred from Poloniex to Huobi.\n Amount: %s \nBTC deposit address of Huobi cannot be verified. Please check manually.' % amount)
            print('Email sent successfully!')
        except:
            print('Email sent FAILED.')

        # transfer amount from Poloniex to Huobi
        print('Transferring ETH from Poloniex to Huobi:')
        status = poloniex_client.Poloniex_Client().client.withdraw(currency='ETH', amount=amount, address=HUOBI_ETH_DEPOSIT_ADDRESS)
        print('Returned response: \"%s\"' % status['response'])
        print('Expected response: \"%s\"' % 'Withdrew %.8f ETH.' % float(amount))
        if status['response'] == 'Withdrew %.8f ETH.' % float(amount):
            print('Transfer status: OK! Status: %s' % status)
        else:
            print('Transfer status: ERROR! Status: %s' % status)
            raise BaseException('Transfer error! Status: %s' % status)

        # return status
        print('Transfer SUCCESS! Amount: %s ETH' % amount)
        return True

if __name__ == '__main__':
    # print(Transfer_ETH().transfer_eth_from_huobi_to_poloniex(amount='0.01'))
    # withdraw_id = Transfer_BTC().transfer_btc_from_huobi_to_poloniex('0.01')
    # print(huobi_main_client.Huobi_Main_Client().cancel_withdraw(withdraw_id))
    # print(Transfer_BTC().transfer_btc_from_poloniex_to_huobi('0.01'))
    # print(Transfer_ETH().transfer_eth_from_poloniex_to_huobi('0.006'))
    pass
