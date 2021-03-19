import requests
import json
import time
from candle import *
from market import *
from pattern import *

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

def is_nice_pattern(market_name):
    if is_pattern_30minute_nice(market_name) and is_pattern_5minute_nice(market_name) and is_pattern_240minute_nice(market_name) and is_pattern_day_nice(market_name) :
        print("go bid", market_name)
        return True
    return False

def main():
    try:
        bid_count = 0
        bid_count_max = 2
        market_group = get_market_groups("KRW")
        while bid_count < bid_count_max:
            for market in market_group:
                market_name = market.get("market")
                if is_nice_pattern(market_name):
                    nice_market = Market(market_name, get_bid_price(market_name))
                    if nice_market.is_already_have() == False:
                        nice_market.bid(200000)
                        bid_count = bid_count + 1
                        print("bid count", bid_count)
                        if bid_count >= bid_count_max:
                            break                    
                time.sleep(0.2)
            time.sleep(60)
    except Exception as e:    
        print("raise error ", e)
if __name__ == "__main__":
    # execute only if run as a script
    main()
