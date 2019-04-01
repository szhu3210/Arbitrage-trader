#!/usr/bin/env python3

import time
import email_client
import premium_calculator

def main():
    while 1:
        print('Check ETH premium... (' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ')')
        premium_ETH = premium_calculator.getPremiums()['ethbtc']
        print('Current premium: ' + str(premium_ETH))
        if abs(premium_ETH) > 0.03:
            print('Sending email...')
            try:
                email_client.Email_client().notify_me_by_email("Notification of ETH premium: " + str(premium_ETH),
                                                               'You have some money to take!')
                print("Email sent successfully!")
            except:
                print("Email not sent!")
        else:
            print('Low premium -> No need to send email.')
        time.sleep(300)


if __name__ == "__main__":
    # execute only if run as a script
    main()
