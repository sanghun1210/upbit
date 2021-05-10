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
from .minute3_trader import *
from .market_log import MarketLog

class UpbitMarket(BaseMarket):
    def __init__(self, logdb_connection):
        super().__init__()
        self.market_group = None
        self.week_trader = None
        self.day_trader = None
        self.minute240_trader = None
        self.minute60_trader = None
        self.minute30_trader = None
        self.minute15_trader = None
        self.minute10_trader = None
        self.minute5_trader = None
        self.minute3_trader = None
        self.logdb = logdb_connection

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

    ######################################################################

    def is_trader_growup(self, trader):
        if trader.is_ma50_over_than_ma15() == False :
            return trader.is_ma_growup_lite()
        else :
            return trader.is_ma_growup()
            

    def init_traders(self, market_name):
        # self.week_trader = WeekTrader(market_name, 5)
        # time.sleep(0.1)
        

        self.minute5_trader = Minute5Trader(market_name, 50)
        time.sleep(0.1)
        # self.minute10_trader = Minute10Trader(market_name, 50)
        # time.sleep(0.1)
        self.minute15_trader = Minute15Trader(market_name, 50)
        time.sleep(0.1)
        self.minute30_trader = Minute30Trader(market_name, 50)
        time.sleep(0.1)
        self.minute60_trader = Minute60Trader(market_name, 50)
        time.sleep(0.1)
        self.minute240_trader = Minute240Trader(market_name, 50)
        time.sleep(0.1)
        self.day_trader = DayTrader(market_name, 50)
        # 
        # self.minute3_trader = Minute3Trader(market_name, 50)
        # time.sleep(0.1)

        self.day_trader.set_child_trader(self.minute240_trader)
        self.minute240_trader.set_child_trader(self.minute60_trader)
        self.minute60_trader.set_child_trader(self.minute30_trader)
        self.minute30_trader.set_child_trader(self.minute15_trader)
        self.minute15_trader.set_child_trader(self.minute5_trader)

    def find_best_markets(self, market_group_name):
        market_name_list = []
        
        self.market_group = self.get_market_groups(market_group_name)
        is_buy = False
            
        for market in self.market_group:
            market_name = market.get("market")

            try:
                print('')
                print('checking...', market_name)
                self.init_traders(market_name)
                mail_to = market_name + ':'    
                mail_to = mail_to + ' => ' + str(self.minute15_trader.candles[0].trade_price)
                mail_list = ['', '', '']
                
                if self.day_trader.is_growup_chart1(mail_list):
                    print(mail_list[0])
                    mail_to = mail_to + mail_list[0]
                    is_buy = True
                elif self.minute240_trader.is_growup_chart1(mail_list):
                    print(mail_list[0])
                    mail_to = mail_to + mail_list[0]
                    is_buy = True                
                else:
                    continue

                if is_buy :
                    #log 기록
                    print('write_database')
                    print(mail_to)
                    self.write_log(market_name, str(self.minute15_trader.candles[0].trade_price))
                    market_name_list.append(mail_to)

            except Exception as e:
                print("raise error ", e)

        
            
        return market_name_list

    def write_log(self, market_name, price):
        market_log = MarketLog(self.logdb)
        market_log.insert_one(market_name, price)
        #print(market_log.select_all())
                
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


