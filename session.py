import requests
import json
import time

def get_markets_all() : 
    url = "https://api.upbit.com/v1/market/all"
    querystring = {"isDetails":"false"}
    response = requests.request("GET", url, params=querystring)
    return response.json()

def get_markets(market_group_name) :
    json_markets = get_markets_all()
    selected_markets = []
    for json_market in json_markets:
        if market_group_name in json_market.get("market") :
            selected_markets.append(json_market)
    return selected_markets


def get_candle(coin_name) :
    url = "https://api.upbit.com/v1/candles/minutes/1"
    #for list in json_res:
    querystring = {"market": coin_name, "count": "1"}
    response = requests.request("GET", url, params=querystring)
    return response.json()


def main():
    try:
        market_list = get_markets("KRW")
        for market in market_list:
            candle = get_candle(market.get("market"))
            print(candle)
            time.sleep(0.1)
    except Exception as e:    # 모든 예외의 에러 메시지를 출력할 때는 Exception을 사용
        print("raise error ", e)

    

if __name__ == "__main__":
    # execute only if run as a script
    main()
