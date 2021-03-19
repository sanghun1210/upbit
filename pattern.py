
import json
import time
import requests
from candle import *


def get_day_candle_list(market_name) :
    str_list = []
    str_list.append("https://api.upbit.com/v1/candles/days")
    url =  ''.join(str_list)
    querystring = {"market": market_name, "count": "5"}
    response = requests.request("GET", url, params=querystring)
    return Candle(response.json())

def get_candle_list(market_name, minute_unit) :
    str_list = []
    str_list.append("https://api.upbit.com/v1/candles/minutes/")
    str_list.append(str(minute_unit))
    url =  ''.join(str_list)
    querystring = {"market": market_name, "count": "10"}
    response = requests.request("GET", url, params=querystring)
    return Candle(response.json())

def is_pattern_30minute_nice(market_name):
    # 10개봉 중에 최고점을 찾는다.
    # 가장 최근봉은 최고점보다 낮아야 한다.
    # 가장 최근봉은 이전봉보다 low_price가 높아야 한다.
    # 가장 최근봉은 최고점 봉보다 1~2%정도 낮아야 한다.
    candles = get_candle_list(market_name, 30)
    time.sleep(0.1)
    max_candle = candles.get_max_trade_candle()
    current_candle = candles.get_current_candle()
    max_trade_price = max_candle.get("trade_price")
    current_trade_price = current_candle.get("trade_price")
    if(max_trade_price <= current_trade_price) :
        return False

    if(candles.is_trade_price_goup() == False):
        return False

    margin = max_trade_price - current_trade_price
    if margin > 0 :
        ror = (margin / max_trade_price) * 100
        if ror <= 5 and ror > 0.8 : 
            print("wow 30 : ", market_name)
            return True
    return False    

def is_pattern_5minute_nice(market_name):
    candles = get_candle_list(market_name, 5)
    time.sleep(0.1)
    return candles.is_trade_price_goup() and candles.is_pumped(2.2) == False
    
def is_pattern_240minute_nice(market_name):
    candles = get_candle_list(market_name, 240)
    time.sleep(0.1)
    return candles.is_trade_price_goup()
    
def get_bid_price(market_name):
    candles = get_candle_list(market_name, 5)
    time.sleep(0.1)
    return candles.get_bid_price()


def is_pattern_day_nice(market_name):
    candles = get_day_candle_list(market_name)
    time.sleep(0.1)
    if candles.is_pumped(12):
        print("alredy pumped day")
        return False
    return True

    
    

    