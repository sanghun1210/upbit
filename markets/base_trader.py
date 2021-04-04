
import json
import time
import requests

import os
import sys
from . import *

from .candle import *
from .calcualtor import *

class BaseTrader():
    def __init__(self, market_name):
        self.market_name = market_name
        self.candles = []

    def create_candle_list_from_json(self, json_candles):
        length = len(json_candles)
        for i in range(0, int(length)):
            temp_cadle = Candle(i, json_candles[i])
            self.candles.append(temp_cadle)

    def ma(self, index):
        my_cal = Calculator(self.candles)
        return my_cal.ma(index)

    def is_go_up(self):
        return (self.candles[0].trade_price > self.candles[1].trade_price) and (self.ma(5) > self.ma(10) > self.ma(20))

    def is_go_up_with_volume(self):
        my_cal = Calculator(self.candles)
        if my_cal.is_growup(4):
            return self.candles[1].candle_acc_trade_volume > self.candles[2].candle_acc_trade_volume > self.candles[3].candle_acc_trade_volume 
        return False

    def is_double_floor(self, margin):
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

        if index_diff  <= 1:
            return False
            
        margin = max_candle.trade_price - min_candle.trade_price
        if (margin / max_candle.trade_price * 100) > margin:
            return False
        
        return self.candles[0].trade_price >= self.candles[1].trade_price

    def is_growup(self, count):
        my_cal = Calculator(self.candles)
        return my_cal.is_growup(count)

    def is_growup_uniform(self, count):
        my_cal = Calculator(self.candles)
        return my_cal.is_growup_uniform(count)

    def is_goup(self, count):
        my_cal = Calculator(self.candles)
        return my_cal.is_goup(count)

    def is_pumped(self, index, rate):
        return self.candles[index].is_yangbong() and self.candles[index].get_yangbong_rate() >= rate

    def is_go_down(self, count):
        my_cal = Calculator(self.candles)
        return my_cal.is_godown(count)

    def is_umbong_candle_long_than(self, index, rate):
        if self.candles[index].is_yangbong() == False:
            if self.candles[index].get_umbong_rate() >= rate:
                return True
        return False
            
    def is_exist_long_umbong(self, count, rate):
        for i in range(0, count):
            if self.is_umbong_candle_long_than(i, rate):
                return True
        return False

        

        

    


