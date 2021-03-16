import requests
import json

def get_markets() : 
    url = "https://api.upbit.com/v1/market/all"
    querystring = {"isDetails":"false"}
    response = requests.request("GET", url, params=querystring)
    return response.json()


def get_candle(market_name) :
    url = "https://api.upbit.com/v1/candles/minutes/1"
    #for list in json_res:
    querystring = {"market": market_name, "count": "1"}
    response = requests.request("GET", url, params=querystring)
    return response.json()


def main():
    market_list = get_markets()
    for market in market_list:
        candle = get_candle(market.get("market"))
        print(candle)
    

if __name__ == "__main__":
    # execute only if run as a script
    main()
