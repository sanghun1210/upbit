import requests
import json
import time
from mail import *

from markets.my_market import *
    
def main():
    try:
        upbit_market = MyMarket()
        best_market_names = upbit_market.get_markets()
        #send_mail(' '.join(best_market_names), "go bid coin")
    except Exception as e:    
        print("raise error ", e)
if __name__ == "__main__":
    # execute only if run as a script
    main()
