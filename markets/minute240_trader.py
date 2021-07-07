
import json
import time
import requests
from .base_trader import *

import os
import sys
from .candle import *
from .calcualtor import *

def get_candle_list(market_name, minute_unit, count) :
    str_list = []
    str_list.append("https://api.upbit.com/v1/candles/minutes/")
    str_list.append(str(minute_unit))
    url =  ''.join(str_list)
    querystring = {"market": market_name, "count": count}
    response = requests.request("GET", url, params=querystring)
    time.sleep(0.1)
    return response.json()


class Minute240Trader(BaseTrader):
    def __init__(self, market_name, count):
        super().__init__(market_name)
        json_candles = get_candle_list(market_name, 240, count)
        self.create_candle_list_from_json(json_candles)
        self.trader_name = 'Minute240Trader'
        self.cross_margin = 0.8

    def check_pattern(self):
        mos = self.get_momentum_list()
        return mos[0] >= -7 and mos[0] <= 7 

    #MACD선은 기본 매개변수의 경우 5일 이동평균선과 비슷하게 움직이며, 시그널선은 10일 이동평균선과 비슷하게 움직인다. 지표값의 양음을 결정하는 0선은 60일 이동평균선과 비슷한 움직임을 보인다.
    #0선 위에서의 MACD상승은 신뢰성이 높지만 0선 밑에서의 MACD상승은 신뢰성이 낮다. 0선 위에서의 MACD하락은 주가가 오르는 경우가 많다. 
    #일봉MACD에서의 속임수를 피하기 위해 주봉의 MACD를, 주봉MACD에서의 속임수를 피하기 위해 월봉MACD를 참조하면 신뢰성이 높아진다. 

    #MACD선은 기본 매개변수의 경우 5일 이동평균선
    #시그널선은 10일 이동평균선
    #0선은 60일 이동평균선
    def check_pattern2(self):
        macd = self.ma(5)
        signal = self.ma(10)
        zero_line = self.ma(60)

        if signal > zero_line :
            if macd > signal and signal >= zero_line: 
                return True
        return False

    def check_pattern3(self):
        ewm12 = self.get_exponential_moving_average4(12)
        ewm26 = self.get_exponential_moving_average4(26)
        macd = ewm12-ewm26
        print(macd[0].tolist())








        

        


    




