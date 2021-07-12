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
from .minute1_trader import *
from .market_log import MarketLog

import logging

class UpbitMarket(BaseMarket):
    def __init__(self, logdb_connection, src_logger):
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
        self.logger = src_logger
        self.goup_market = True

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

    def is_main_trader_growup(self, trader, margin, max_range):
        return trader.is_ma_growup() and (self.get_margin(trader.get_max_trade_price(max_range), trader.candles[0].trade_price) <= 1)

    def is_sub_trader_growup(self, trader):
        if trader.is_ma_growup():
             return True
        if trader.ma(15) > trader.ma(50):
            return True
        return False

    def is_third_trader_growup(self, trader, margin):
        if trader.ma(15) > trader.ma(50):
            return True
        elif trader.ma(50) - trader.ma(15) >= margin:
            return True
        return False

    def get_margin(self, a, b):
        ma = 0
        if a > b:
            ma = ((a - b) / a) * 100
        else : 
            ma = ((b - a) / b) * 100
        return ma
            
    def init_traders(self, market_name, src_logger):
        # self.week_trader = WeekTrader(market_name, 5)
        # time.sleep(0.1)
        # self.minute1_trader = Minute1Trader(market_name, 120)
        # time.sleep(0.1)
        # self.minute3_trader = Minute3Trader(market_name, 120)
        # time.sleep(0.1)
        # self.minute5_trader = Minute5Trader(market_name, 120)
        # time.sleep(0.1)
        # self.minute10_trader = Minute10Trader(market_name, 120)
        # time.sleep(0.1)
        self.minute15_trader = Minute15Trader(market_name, 120, src_logger)
        time.sleep(0.1)
        self.minute30_trader = Minute30Trader(market_name, 120, src_logger)
        time.sleep(0.1)
        self.minute60_trader = Minute60Trader(market_name, 120, src_logger)
        time.sleep(0.1)
        self.minute240_trader = Minute240Trader(market_name, 150, src_logger)
        time.sleep(0.1)
        self.day_trader = DayTrader(market_name, 150, src_logger)

    def find_best_markets(self, market_group_name):
        market_name_list = []
        
        self.market_group = self.get_market_groups(market_group_name)
        
        for market in self.market_group:
            market_name = market.get("market")
            is_buy = False
            is_write_db = False

            try:
                print('checking...', market_name)
                self.init_traders(market_name, self.logger)
                mail_to = market_name + ':'    
                mail_to = mail_to 

                self.logger.info(market_name)

                if market_name == 'KRW-BTC':
                    if self.minute60_trader.ma(5) > self.minute60_trader.ma(10):
                        is_buy = True
                        self.goup_market = True
                        print('go to buy')
                        mail_to = 'go to buy'
                    else:
                        is_buy = True
                        print('go to sell')
                        self.goup_market = False
                        mail_to = 'go to sell uuuuu'

                point = 0

                point_day = self.day_trader.check_pattern() * 1.4
                self.logger.info('day_trader result : ' + str(point_day))
                point240 = self.minute240_trader.check_base_pattern(15)  
                self.logger.info('minute240_trader result : ' + str(point240))
                # point60 = self.minute60_trader.check_base_pattern(12) * 0.8
                # self.logger.info('minute60_trader result : ' + str(point60))
                point30 = self.minute30_trader.check_base_pattern(7) * 0.5
                self.logger.info('minute30_trader result : ' + str(point30))
                # point15 = self.minute15_trader.check_base_pattern(6) * 0.3
                # self.logger.info('minute15_trader result : ' + str(point15))
                # point = point_day + point240 + point60 + point30 + point15
                point = point_day + point240 +  point30
                self.logger.info('total_poing result : ' + str(point))

                self.logger.info('=======================================================================================================')
                print(point)

                if point >= 8.2 :
                    #log 기록
                    market_name_list.append(mail_to + ' point :  ' + str(point) + ' current price : ' + str(self.minute240_trader.candles[0].trade_price))
                    is_write_db = True

                if is_write_db:
                    print('write_database')
                    self.write_log(market_name, str(self.minute15_trader.candles[0].trade_price))

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


