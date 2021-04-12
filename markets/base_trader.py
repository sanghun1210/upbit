
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

    def is_ma_growup(self):
        return self.ma(5) > self.ma(10) > self.ma(20)

    def is_goup_with_volume(self):
        if self.candles[0].trade_price > self.candles[1].trade_price and self.candles[0].candle_acc_trade_volume > self.candles[1].candle_acc_trade_volume:
            return True
        if self.candles[0].trade_price > self.candles[1].trade_price > self.candles[2].trade_price and self.candles[1].candle_acc_trade_volume > self.candles[2].candle_acc_trade_volume:
            return True
        return False

    def is_growup(self, count): 
        my_cal = Calculator(self.candles)
        return my_cal.is_growup(count)

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

    def is_go_down(self):
        return self.candles[0].trade_price < self.candles[1].trade_price < self.candles[2].trade_price

        

        

    


