import requests
import json
import time
from mail import *
import datetime

from markets.my_market import *
    
def main():
    try:
        my_markets = get_my_markets()

        while True:
            for market in my_markets:
                if market.market_name == "KRW-KRW":
                    continue

                if market.is_go_down1():
                    print('haha - go to sell', market.market_name)
                    now = datetime.datetime.now()
                    str1 = 'haha - go to sell' + market.market_name
                    send_mail(str1, market.market_name)
                    print(now)
            time.sleep(40)
    except Exception as e:    
        print("raise error ", e)
if __name__ == "__main__":
    # execute only if run as a script
    main()
