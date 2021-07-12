
import json
import time
import requests
from .base_trader import *

import os
import sys

from .candle import *
from .calcualtor import *

def get_day_candle_list(market_name, count) :
    str_list = []
    str_list.append("https://api.upbit.com/v1/candles/days")
    url =  ''.join(str_list)
    querystring = {"market": market_name, "count": count}
    response = requests.request("GET", url, params=querystring)
    time.sleep(0.1)
    return response.json()


class DayTrader(BaseTrader):
    def __init__(self, market_name, count, src_logger):
        super().__init__(market_name, src_logger)
        json_candles = get_day_candle_list(market_name, count)
        self.create_candle_list_from_json(json_candles)
        self.trader_name = 'DayTrader'

    def get_rsi_check_point_day(self):
        point = 0
        self.logger.info('self.rsi(0, 14) ==> ' + str(self.rsi(0, 14)))
        if self.rsi(0, 14) <= 35 or self.rsi(0, 14) >= 75 :
            self.logger.info('rsi check fail' )
            point = point-1
        elif self.rsi(0, 14) >= 43:
            point = point+1

        if self.rsi(0, 14) > self.rsi(1, 14):
            self.logger.info('rsi(0, 14) rsi(1, 14) ==> ' + str(self.rsi(0, 14)) + ' ' + str(self.rsi(1, 14)))
            point = point+1     
        return point

    def check_pattern(self):
        mos = self.get_momentum_list()
        self.logger.info('mos[0] ==> ' + str(mos[0]))
    
        point = 0
        if self.candles[0].trade_price > self.ma(10) : 
            point += 1

        point = point + self.get_rsi_check_point_day()

        if mos[0] > 15:
            point = point * 1.2
        elif mos[0] > 7:
            point = point 
        elif mos[0] <= 7 and mos[0] >= -1.2:
            point = point * 0.7 
        else:
            point = 0
            
        return point


