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
        week_trader = WeekTrader(market_name, 6)
        if week_trader.is_good_chart() == False:
            return False

        day_trader = DayTrader(market_name, 16)
        if day_trader.is_good_chart() == False:
            return False

        minute240_trader = Minute240Trader(market_name, 16)
        if minute240_trader.is_good_chart() == False:
            return False

        minute60_trader = Minute60Trader(market_name, 16)
        minute30_trader = Minute30Trader(market_name, 14)
        if minute60_trader.is_good_chart() :
            minute10_trader = Minute10Trader(market_name, 14)
            if minute10_trader.is_good_chart():
                return True

            minute15_trader = Minute15Trader(market_name, 14)
            if minute15_trader.is_good_chart():
                return True
                
        elif minute30_trader.is_good_chart():
            minute10_trader = Minute10Trader(market_name, 14)
            if minute10_trader.is_good_chart() == False:
                return True
        return False

    def find_best_markets(self):
        market_name_list = []
        if self.market_group == None:
            self.market_group = self.get_market_groups("KRW")
        for market in self.market_group:
            market_name = market.get("market")
            if self.is_nice_pattern(market_name):
                if self.is_already_have(market_name) == False:
                    #print("go to bid")
                    market_name_list.append(market_name)
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


