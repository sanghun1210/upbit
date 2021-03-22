
import json
import time
import requests
from .base_trader import *

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from candle import *
from calcualtor import *

def get_candle_list(market_name, minute_unit, count) :
    str_list = []
    str_list.append("https://api.upbit.com/v1/candles/minutes/")
    str_list.append(str(minute_unit))
    url =  ''.join(str_list)
    querystring = {"market": market_name, "count": count}
    response = requests.request("GET", url, params=querystring)
    return response.json()


class Minute240Trader(BaseTrader):
    def __init__(self, market_name, count):
        super().__init__(market_name)
        json_candles = get_candle_list(market_name, 240, count)
        self.create_candle_list_from_json(json_candles)

    def is_good_chart(self):
        if self.is_double_floor() and self.is_goup(2):
            return True

        my_cal = Calculator(self.candles)
        max_candle = my_cal.get_max_trade_price_candle()
        if max_candle.index != 0 and self.is_growup(3) and self.is_goup(2):
            return True 
        
        return False



    


