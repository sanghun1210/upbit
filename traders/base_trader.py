
import json
import time
import requests

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from candle import *
from calcualtor import *

class BaseTrader():
    def __init__(self, market_name):
        self.market_name = market_name
        self.candles = []

    def create_candle_list_from_json(self, json_candles):
        length = len(json_candles)
        for i in range(0, int(length) - 1):
            temp_cadle = Candle(i, json_candles[i])
            self.candles.append(temp_cadle)

    def is_double_floor(self):
        my_cal = Calculator(self.candles)
        max_candle = my_cal.get_max_trade_price_candle()
        min_candle = my_cal.get_min_trade_price_candle()

        if max_candle.index == 0:
            return False

        index_diff = 0
        if max_candle.index > min_candle.index:
            index_diff = max_candle.index - min_candle.index
        else:
            index_diff = min_candle.index - max_candle.index

        if index_diff  <= 2:
            return False
            
        margin = max_candle.trade_price - min_candle.trade_price
        if (margin / max_candle.trade_price * 100) > 15:
            return False
        
        return self.candles[0].trade_price >= self.candles[1].trade_price

    def is_growup(self, count):
        my_cal = Calculator(self.candles)
        return my_cal.is_growup(count)

    def is_growup_uniform(self, count):
        if self.market_name == "KRW-GRS":
            print("chekc")
        
        my_cal = Calculator(self.candles)
        return my_cal.is_growup_uniform(count)

    def is_goup(self, count):
        my_cal = Calculator(self.candles)
        return my_cal.is_goup(count)
        

    


