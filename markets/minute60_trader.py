
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


class Minute60Trader(BaseTrader):
    def __init__(self, market_name, count):
        super().__init__(market_name)
        json_candles = get_candle_list(market_name, 60, count)
        self.create_candle_list_from_json(json_candles)
        self.trader_name = 'Minute60Trader'
        self.cross_margin = 0.7

    def check_pattern(self):
        mos = self.get_momentum_list()
        if mos[0] >= -7 and mos[0] <= 7 and mos[0] > self.momentum_ma(5):
            stdev = self.get_bollinger_bands_standard_deviation()
            high_band = self.ma(20) + (stdev * 2)
            low_band = self.ma(20) - (stdev * 2)
            if self.get_margin(high_band, low_band) <= 8:
                if self.ma(5) > self.ma(10) and self.get_margin(self.ma(5), self.ma(60)) <= 1.2:
                    return True
        return False

    


