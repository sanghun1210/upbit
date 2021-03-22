import requests
import json
import time
from candle import *
from market import *

from traders.week_trader import *
from traders.day_trader import *
from traders.minute240_trader import *
from traders.minute30_trader import *

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
    week_trader = WeekTrader(market_name, 5)
    if week_trader.is_good_chart() == False:
        return False

    day_trader = DayTrader(market_name, 16)
    if day_trader.is_good_chart() == False:
        return False

    minute240_trader = Minute240Trader(market_name, 20)
    if minute240_trader.is_good_chart() == False:
        return False

    minute30_trader = Minute30Trader(market_name, 10)
    if minute30_trader.is_good_chart() == False:
        return False

    return True
    
def main():
    try:
        bid_count = 0
        bid_count_max = 10
        loop_count = 0
        market_group = get_market_groups("KRW")
        while bid_count < bid_count_max:
            for market in market_group:
                market_name = market.get("market")
                if market_name == "KRW-XLM" or market_name == "KRW-KMD" or market_name == "KRW-SNT":
                    continue

                if is_nice_pattern(market_name):
                    nice_market = Market(market_name)
                    if nice_market.is_already_have() == False:
                        #nice_market.bid(200000)
                        bid_count = bid_count + 1
                        print("bid count", bid_count , market_name)
                        if bid_count >= bid_count_max:
                            break                    
                time.sleep(0.2)
            loop_count = loop_count + 1
            print("loop_count : ", loop_count)
            time.sleep(33)
    except Exception as e:    
        print("raise error ", e)
if __name__ == "__main__":
    # execute only if run as a script
    main()
