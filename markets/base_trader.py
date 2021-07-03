
import json
import time
import requests

import os
import sys
from . import *

from .candle import *
from .calcualtor import *
from enum import Enum
import math
import pandas as pd

class BaseTrader():
    def __init__(self, market_name):
        self.market_name = market_name
        self.candles = []
        self.child = None
        self.trader_name = ''
        self.cross_margin = 0.5

    def create_candle_list_from_json(self, json_candles):
        length = len(json_candles)
        for i in range(0, int(length)):
            temp_cadle = Candle(i, json_candles[i])
            self.candles.append(temp_cadle)

    def get_margin(self, a, b):
        ma = 0
        if a > b:
            ma = ((a - b) / a) * 100
        else : 
            ma = ((b - a) / b) * 100
        return ma

    def ma(self, index):
        my_cal = Calculator(self.candles)
        return my_cal.ma(index)

    def ma_volume(self, index):
        sum = 0
        for i in range(0, index): 
            sum = sum + self.candles[i].candle_acc_trade_volume
        return sum / index

    def is_ma_volume_up(self):
        return self.candles[0].candle_acc_trade_volume > self.ma_volume(4) and self.candles[0].is_yangbong()

    def is_pre_volumne_min(self, range_count):
        vol_list = []
        for i in range(1, range_count):
            vol_list.append(self.candles[i].candle_acc_trade_volume)

        min_vol = min(vol_list)
        return min_vol == self.candles[1].candle_acc_trade_volume

    def get_max_trade_price(self, range_count):
        trade_price_list = []
        for i in range(0, range_count):
            trade_price_list.append(self.candles[i].trade_price)
        return max(trade_price_list)

    def is_ma_growup(self):
        # 기본 바꾸면 안됨.
        return self.ma(5) > self.ma(50) 
    
    def is_ma_growup_lite(self):
        # 기본 바꾸면 안됨.
        return self.ma(4) > self.ma(8) 

    def is_goup_with_volume(self) :
        return self.candles[0].trade_price > self.candles[1].trade_price and self.candles[0].candle_acc_trade_volume > self.candles[1].candle_acc_trade_volume

    def is_pre_goup_with_volume(self) :
        return self.candles[1].trade_price > self.candles[2].trade_price and self.candles[1].candle_acc_trade_volume > self.candles[2].candle_acc_trade_volume
        
    def is_anomaly_candle(self) :
        return self.candles[0].is_yangbong() and self.candles[0].candle_acc_trade_volume > (self.candles[1].candle_acc_trade_volume * 5)

    def is_growup(self, count): 
        my_cal = Calculator(self.candles)
        return my_cal.is_growup(count)

    def is_go_down(self, count):
        my_cal = Calculator(self.candles)
        return my_cal.is_godown(count)

    def is_umbong_candle_long_than(self, index, rate):
        if self.candles[index].is_yangbong() == False:
            if self.candles[index].get_umbong_rate() >= rate:
                return True
        return False

    def is_go_down(self):
        return self.candles[0].trade_price < self.candles[1].trade_price < self.candles[2].trade_price

    def get_ma(self, count):
        return self.ma(count)

    def is_ma50_over_than_ma15(self):
        return self.ma(50) > self.ma(15)

    def is_ma120_over_than_ma15(self):
        return self.ma(120) > self.ma(15)
        
    def get_ma_margin(self):
        if self.ma(50) > self.ma(15):
            return round(float(((self.ma(50) - self.ma(15)) / self.ma(50)) * 100), 2)
        else:
            return round(float(((self.ma(15) - self.ma(50)) / self.ma(15)) * 100), 2)

    def get_ma_margin120(self):
        if self.ma(120) > self.ma(15):
            return round(float(((self.ma(120) - self.ma(15)) / self.ma(120)) * 100), 2)
        else:
            return round(float(((self.ma(15) - self.ma(120)) / self.ma(15)) * 100), 2)

    def get_ma_print(self):
        if self.ma(50) > self.ma(15):
            per = str(round(float(((self.ma(50) - self.ma(15)) / self.ma(50)) * 100), 2))
            return str('+' + per + '(%)')
        else:
            per = str(round(float(((self.ma(15) - self.ma(50)) / self.ma(15)) * 100), 2))
            return str('-' + per + '(%)')

    def deviation(self, a, b):
        if a >= b:
            return a - b
        else :
            return b - a

    def get_bollinger_bands_standard_deviation(self):
        average20 = self.ma(20)
        mysum = 0
        for i in range(0, 20):
            mysum += (self.deviation(average20, self.candles[i].trade_price) ** 2)
        avr_dev = mysum / 20
        return math.sqrt(float(avr_dev))


    def get_exponential_moving_average(self, start, len):
        target_trade_price_list = []
        for item in self.candles[::-1]:
            target_trade_price_list.append(item.trade_price)

        df = pd.DataFrame(target_trade_price_list)
        return df.ewm(span=len).mean()[0].tolist()

    def get_exponential_moving_average2(self, start, len):
        target_trade_price_list = []
        for i in range(start, len):
            target_trade_price_list.append(self.candles[i].trade_price)

        a = 2 / (len + 1)
        x = target_trade_price_list[0]
        temp = target_trade_price_list[0]
        i = 0
        for target_price in target_trade_price_list:
            if i == 0:
                continue
            else:
                temp = a * target_price + (1 - a) * temp
                x += temp
            i = i + 1
        return x / (len + 1)

    def get_exponential_moving_average3(self, start, len):
        target_trade_price_list = []
        for i in range(start, 100):
            target_trade_price_list.append(self.candles[i].trade_price)
        df = pd.DataFrame(target_trade_price_list)
        return df.ewm(span=len, min_periods=len-1).mean()


        






    