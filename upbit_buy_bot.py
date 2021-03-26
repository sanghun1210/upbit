import requests
import json
import time
from mail import *
import datetime


from markets.upbit_market import *
    
def main():
    try:
        loop_count = 1
        while True:
            upbit_market = UpbitMarket()
            print('1')
            best_market_names = upbit_market.find_best_markets()
            if int(len(best_market_names)) > 0 :
                send_mail(' '.join(best_market_names), "go bid coin")
                now = datetime.datetime.now()
                print('time : ', now,' ', ', '.join(best_market_names))
            loop_count = loop_count + 1
            time.sleep(50)
    except Exception as e:    
        print("raise error ", e)
if __name__ == "__main__":
    # execute only if run as a script
    main()
