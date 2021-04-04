
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


class Minute15Trader(BaseTrader):
    def __init__(self, market_name, count):
        super().__init__(market_name)
        json_candles = get_candle_list(market_name, 15, count)
        self.create_candle_list_from_json(json_candles)

    def is_good_chart(self):
        if self.is_double_floor(15):
            return True
        return False

    def is_go_down(self):
        print('ma5, ma10',self.ma(5),  self.ma(10))
        return self.ma(5) < self.ma(10) < self.ma(20)


    

