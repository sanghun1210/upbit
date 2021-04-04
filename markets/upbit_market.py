import os
import jwt
import uuid
import hashlib
import json
import time
from urllib.parse import urlencode

import requests

from .base_market import *
from .week_trader import *
from .day_trader import *
from .minute240_trader import *
from .minute60_trader import *
from .minute30_trader import *
from .minute15_trader import *
from .minute10_trader import *
from .minute5_trader import *

class UpbitMarket(BaseMarket):
    def __init__(self):
        super().__init__()
        self.market_group = None

    def get_markets_all(self) : 
        url = "https://api.upbit.com/v1/market/all"
        querystring = {"isDetails":"false"}
        response = requests.request("GET", url, params=querystring)
        return response.json()

    def get_market_groups(self, market_group_name) :
        json_markets = self.get_markets_all()
        selected_markets = []
        for json_market in json_markets:
            if market_group_name in json_market.get("market") :
                selected_markets.append(json_market)
        return selected_markets

    def is_nice_pattern(self, market_name):
        # day_trader = DayTrader(market_name, 16)
        # if day_trader.is_good_chart() == False:
        #     return False

        # time.sleep(0.1)
        minute240_trader = Minute240Trader(market_name, 16)
        if minute240_trader.is_good_chart() == False:
            return False

        time.sleep(0.1)
        minute60_trader = Minute60Trader(market_name, 16)
        if minute60_trader.is_good_chart():
            time.sleep(0.1)
            minute10_trader = Minute10Trader(market_name, 14)
            if minute10_trader.is_good_chart():
                return True

        return False

    def is_stra_pattern(self, market_name):
        time.sleep(0.1)
        minute240_trader = Minute240Trader(market_name, 10)
        if minute240_trader.is_stra_pattern() == False:
            return False

        time.sleep(0.1)
        minute60_trader = Minute60Trader(market_name, 10)
        return minute60_trader.is_growup(3)

    def is_go_up_pattern(self, market_name):
        day_trader = DayTrader(market_name, 20)
        time.sleep(0.1)
        minute240_trader = Minute240Trader(market_name, 20)
        time.sleep(0.1)
        minute15_trader = Minute15Trader(market_name, 20)
        time.sleep(0.1)
        minute30_trader = Minute30Trader(market_name, 20)
        if day_trader.is_go_up() and minute240_trader.is_go_up() and minute15_trader.is_growup(4):
            return True

        if minute240_trader.is_go_up() and minute30_trader.is_go_up_with_volume():
            return True

        return False

    def is_go_up_pattern_with_hoje(self, market_name):
        hojes = self.get_hoje_list()
        time.sleep(0.1)
        minute240_trader = Minute240Trader(market_name, 20)
        time.sleep(0.1)
        minute30_trader = Minute30Trader(market_name, 20)

        for hoje in hojes:
            if hoje == market_name:
                return minute240_trader.is_growup(4) and minute30_trader.is_growup(3)
        return False

    def is_go_up_pattern_by_ma(self, market_name):
        minute240_trader = Minute240Trader(market_name, 20)
        time.sleep(0.1)
        minute60_trader = Minute60Trader(market_name, 20)
        time.sleep(0.1)
        minute5_trader = Minute5Trader(market_name, 20)
        time.sleep(0.1)

        return minute240_trader.is_go_up() and minute60_trader.is_go_up() and minute5_trader.is_go_up()

    def is_go_up_pattern_by_volume(self, market_name):
        minute240_trader = Minute240Trader(market_name, 20)
        time.sleep(0.1)
        minute60_trader = Minute60Trader(market_name, 20)
        time.sleep(0.1)
        return minute240_trader.is_go_up() and minute60_trader.is_go_up_with_volume()

    def find_best_markets(self):
        market_name_list = []
        
        if self.market_group == None:
            self.market_group = self.get_market_groups("KRW")
        for market in self.market_group:
            is_goup = False
            market_name = market.get("market")
            print('checking...', market_name)
            mail_to = ""
            if self.is_go_up_pattern_by_ma(market_name):
                print('is_go_up_pattern_by_ma')
                mail_to = mail_to + (market_name + ' (is_go_up_pattern_by_ma)')
                is_goup = True
            if self.is_go_up_pattern_by_volume(market_name):
                print('is_go_up_pattern_by_volume')
                mail_to = mail_to + (market_name + ' (is_go_up_pattern_by_volume)')
                is_goup = True
            if is_goup :
                market_name_list.append(mail_to)
        return market_name_list
                
    def is_already_have(self, market_name):
        query = {
            'market': market_name,
        }
        query_string = urlencode(query).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': self.access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, self.secret_key)
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        res = requests.get(self.server_url + "/v1/orders/chance", params=query, headers=headers)
        #print(res.json())

        ask_account = res.json()["ask_account"]
        coin_balance = ask_account["balance"]
        
        is_already_have_this = (coin_balance != '0.0')
        #print("is_already_have_this coin : ", is_already_have_this, market_name)
        return is_already_have_this
        
    def bid(self, market_name, money):            
        query = {
            'market': market_name,
            'side': 'bid',
            'volume': '',
            'price': str(money),
            'ord_type': 'price',
        }
        print(query)
        query_string = urlencode(query).encode()
        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': self.access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, self.secret_key)
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        res = requests.post(self.server_url + "/v1/orders", params=query, headers=headers)


