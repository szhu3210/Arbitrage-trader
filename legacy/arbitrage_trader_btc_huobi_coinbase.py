from coinbase.wallet.client import Client
import coinbase_client
import huobi_main_monitor
import time
import email_client

coinbaseClient = Client(coinbase_client.Coinbase_Client().api_key, coinbase_client.Coinbase_Client.api_secret)

