import requests
import json
import time
from candle import *
from market import *

def get_markets_all() : 
    url = "https://api.upbit.com/v1/market/all"
    querystring = {"isDetails":"false"}
    response = requests.request("GET", url, params=querystring)
    return response.json()

def get_market_groups(market_group_name) :
    json_markets = get_markets_all()
    selected_markets = []
    for json_market in json_markets:
        if market_group_name in json_market.get("market") :
            selected_markets.append(json_market)
    return selected_markets

def get_candles(market_name) :
    url = "https://api.upbit.com/v1/candles/minutes/1"
    #for list in json_res:
    querystring = {"market": market_name, "count": "1"}
    response = requests.request("GET", url, params=querystring)
    return response.json()

def main():
    try:
        market_group = get_market_groups("KRW")
        for market in market_group:
            candle = Candle(get_candles(market.get("market")))
            if candle.is_nice(1.2):
                candle.show()
                nice_market = Market(candle.get_market_name())
                nice_market.init()
            time.sleep(0.1)
    except Exception as e:    
        print("raise error ", e)

if __name__ == "__main__":
    # execute only if run as a script
    main()
