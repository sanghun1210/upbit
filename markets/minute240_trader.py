
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
        stdev = self.get_bollinger_bands_standard_deviation()
        high_band = self.ma(20) + (stdev * 2)
        low_band = self.ma(20) - (stdev * 2)
        if self.get_margin(high_band, low_band) <= 13:
            if self.get_margin(self.ma(12), self.ma(48)) < 1.5 and self.candles[0].trade_price >= high_band  :
                return True
        return False

    def get_ewm_ma(self, ewm_list, index):
        sum = 0
        for i in range(0, index): 
            sum = sum + ewm_list[i]
        return sum / index



    def check_pattern2(self):
        ewm9 = self.get_exponential_moving_average3(0, 9)
        # ewm1_9 = self.get_exponential_moving_average(1, 10)
        ewm12 = self.get_exponential_moving_average3(0, 12)
        ewm26 = self.get_exponential_moving_average3(0, 26)
        # ewm1_13 = self.get_exponential_moving_average(1, 13)
        # ewm1_27 = self.get_exponential_moving_average(1, 27)

        macd = ewm12 - ewm26
        signal = macd - ewm9


        print(signal[0].tolist())

        # print(self.get_ewm_ma(ewm12_list, 12))
        # print(self.get_ewm_ma(ewm12_list, 26))
        # print(self.get_ewm_ma(ewm12_list, 12) - self.get_ewm_ma(ewm12_list, 26))



        # print(ewm0_12)
        # print(ewm0_26)
        # print(ewm0_12[11] - ewm0_26[25]) # 455
        # print(ewm0_9)             # 303

        # macd0 = ewm0_12[11] - ewm0_26[25]
        # macd1 = ewm1_13[11] - ewm1_27[25]

        # signal0 = ewm0_9[8] 
        # signal1 = ewm1_9[8]

        # print(signal0, macd0)

        # if signal0 >= macd0 and macd0 > signal1 and macd0 > macd1:
        #     return True






        

        


    




