
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
    def __init__(self, market_name, src_logger):
        self.market_name = market_name
        self.candles = []
        self.child = None
        self.trader_name = ''
        self.cross_margin = 0.5
        self.max_bollinger_bands_width = 10
        self.logger = src_logger
        self.min_ma = 0
        self.max_ma = 0

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


    def momentum(self, index):
        return ((self.candles[index].trade_price -  self.candles[index + 9].trade_price) / self.candles[index + 9].trade_price) * 100

    def momentum2(self, index):
        return (self.candles[index].trade_price / self.candles[index + 9].trade_price) * 100

    def get_momentum_list(self):
        mo_list = []
        for i in range(0, len(self.candles) - 10):
            mo_list.append(self.momentum(i))
        return mo_list

    def momentum_ma(self, index):
        mos = self.get_momentum_list()
        sum = 0
        for i in range(0, index): 
            sum = sum + mos[i]
        return sum / index

    def check_momentum_range(self, min_mo, max_mo):
        mos = self.get_momentum_list()
        return mos[0] <= max_mo and mos[0] >= min_mo

    def rsi(self, index, rsi_range):
        diff_list = []
        for i in range(index, rsi_range + index):
            diff_list.append((self.candles[i].trade_price - self.candles[i + 1].trade_price))
        
        #구한 데이터를 기준으로 음의 값을 0으로하는 상승분 데이터와, 양의 값을 0으로 하는 하락분데이터로 나눔
        upper_sum = 0
        down_sum = 0
        for diff_data in diff_list:
            if diff_data > 0:
                upper_sum += diff_data
            else:
                down_sum += abs(diff_data)

        AU = upper_sum / rsi_range
        AD = down_sum / rsi_range

        RS = AU / AD
        RSI = AU/(AU+AD)
        return RSI * 100

    def get_bollinger_bands_width(self):
        stdev = self.get_bollinger_bands_standard_deviation()
        high_band = self.ma(20) + (stdev * 2)
        low_band = self.ma(20) - (stdev * 2)
        return self.get_margin(high_band, low_band)

    def get_rsi_check_point(self):
        point = 0
        if self.rsi(0, 14) <= 35 or self.rsi(0, 14) >= 75 :
            self.logger.info('rsi check fail ' + str(self.rsi(0, 14)) )
            point = point-1
        elif self.rsi(0, 14) >= 43 :
            self.logger.info('rsi check success ' + str(self.rsi(0, 14)) )
            point = point+1

        if self.rsi(0, 14) > self.rsi(1, 14):
            self.logger.info('rsi(0, 14) rsi(1, 14) ==> ' + str(self.rsi(0, 14)) + ' ' + str(self.rsi(1, 14)))
            point = point+1     
        return point


    def check_base_pattern(self, max_bol_width):
        self.logger.info(' self.candles[0].trade_price : ' + str(self.candles[0].trade_price) + 'self.ma(10) : ' + str(self.ma(10)))
        self.logger.info('self.get_margin(self.ma(5), self.ma(10)) ==> ' + str(self.get_margin(self.ma(5), self.ma(10))))
        self.logger.info('self.get_bollinger_bands_width() ==> ' + str(self.get_bollinger_bands_width()))
        point = 0

        mos = self.get_momentum_list()
        self.logger.info('mos[0] ==> ' + str(mos[0]))
        point = point + self.get_rsi_check_point()
        
        if self.get_bollinger_bands_width() <= max_bol_width:
            point = point + 1
        else :
            point = point - 1 

        if self.ma(self.min_ma) >= self.ma(self.max_ma):
            point = point + 1

        if self.candles[0].trade_price >= self.ma(10):
            point = point + 1

        if mos[0] > 15:
            point = point * 1.2
        elif mos[0] > 7:
            point = point 
        elif mos[0] <= 7 and mos[0] >= -1.2:
            point = point * 0.7 
        else:
            point = 0
    
        return point

        



        



        


        






    