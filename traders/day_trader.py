
import json
import time
import requests
from .base_trader import *

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from candle import *
from calcualtor import *

def get_day_candle_list(market_name, count) :
    str_list = []
    str_list.append("https://api.upbit.com/v1/candles/days")
    url =  ''.join(str_list)
    querystring = {"market": market_name, "count": count}
    response = requests.request("GET", url, params=querystring)
    return response.json()


class DayTrader(BaseTrader):
    def __init__(self, market_name, count):
        super().__init__(market_name)
        json_candles = get_day_candle_list(market_name, count)
        self.create_candle_list_from_json(json_candles)

    def is_good_chart(self):
        if self.is_double_floor():
            return True

        if self.is_growup(4) and self.candles[0].trade_price >= self.candles[1].trade_price:
            return True

        return False



    


