
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
    def __init__(self, market_name, count, src_logger):
        super().__init__(market_name, src_logger)
        json_candles = get_candle_list(market_name, 60, count)
        self.create_candle_list_from_json(json_candles)
        self.trader_name = 'Minute60Trader'
        self.cross_margin = 0.7
        self.max_bollinger_bands_width = 7
        self.min_ma = 10
        self.max_ma = 50



