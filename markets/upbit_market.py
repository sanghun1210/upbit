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


    def is_nice_trader(self, trader):
        stdev = trader.get_bollinger_bands_standard_deviation()
        high_band = trader.ma(20) + (stdev * 2)
        return trader.candles[0].trade_price < high_band and trader.ma(5) > trader.ma(50) and trader.is_max_trade_price(15)        
            
    def init_traders(self, market_name):
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
        # self.minute15_trader = Minute15Trader(market_name, 120)
        # time.sleep(0.1)
        self.minute30_trader = Minute30Trader(market_name, 120)
        time.sleep(0.1)
        self.minute60_trader = Minute60Trader(market_name, 120)
        time.sleep(0.1)
        self.minute240_trader = Minute240Trader(market_name, 150)
        time.sleep(0.1)
        self.day_trader = DayTrader(market_name, 150)


    def good_pattern_2021_6month(self):
        stdev = self.minute60_trader.get_bollinger_bands_standard_deviation()
        high_band = self.minute60_trader.ma(20) + (stdev * 2)
        low_band = self.minute60_trader.ma(20) - (stdev * 2)
        if self.get_margin(high_band, low_band) <= 8:
            if self.minute60_trader.candles[0].trade_price >= high_band:
                return True
        return False


    def find_best_markets(self, market_group_name):
        market_name_list = []
        
        self.market_group = self.get_market_groups(market_group_name)
        
        for market in self.market_group:
            market_name = market.get("market")
            is_buy = False
            is_write_db = False

            try:
                print('checking...', market_name)
                self.init_traders(market_name)
                mail_to = market_name + ':'    
                mail_to = mail_to + ' => ' + str(self.minute60_trader.candles[0].trade_price)

                point = 0

                if self.day_trader.check_pattern(): point += 1
                if self.minute240_trader.check_momentum_range(-7, 7): point += 1
                if self.minute240_trader.rsi(0, 14) > 50 and self.minute240_trader.rsi(1, 14): point += 1
                if self.minute60_trader.check_pattern(): point += 1
                # if self.minute30_trader.check_pattern():
                #     print(' +30min ')
                #     point += 1    

                if point >= 4:
                    is_buy = True

                        # if self.minute30_trader.check_pattern():
                        #     print(' +30min ')
                        #     mail_to = mail_to + ' 30min!' 
                        #     is_buy = True

                # if self.is_main_trader_growup(self.minute5_trader, 12):
                #     if self.is_sub_trader_growup(self.minute15_trader) and self.is_third_trader_growup(self.minute30_trader, 5):
                #         print(' +5min ')
                #         if self.minute15_trader.is_ma50_over_than_ma15():
                #             mail_to = mail_to + ' 15min : ' + '+' + str(self.minute5_trader.get_ma_margin())
                #         else:
                #             mail_to = mail_to + ' 15min : ' + '-' + str(self.minute5_trader.get_ma_margin())
                #         is_buy = True
                
                # if self.is_main_trader_growup(self.minute5_trader, 0.5, 55):
                #     if self.is_sub_trader_growup(self.minute15_trader) and self.is_third_trader_growup(self.minute30_trader, 5):
                #         print(' +15min ')
                #         if self.minute5_trader.is_ma50_over_than_ma15():
                #             mail_to = mail_to + ' 5min : ' + '+' + str(self.minute15_trader.get_ma_margin())
                #         else:
                #             mail_to = mail_to + ' 5min : ' + '-' + str(self.minute15_trader.get_ma_margin())
                #         is_buy = True
                 
                # if self.is_main_trader_growup(self.minute15_trader, 1, 35):
                #     if self.is_sub_trader_growup(self.minute30_trader) and self.is_third_trader_growup(self.minute60_trader, 7):
                #         print(' +15min ')
                #         if self.minute15_trader.is_ma50_over_than_ma15():
                #             mail_to = mail_to + ' 15min : ' + '+' + str(self.minute15_trader.get_ma_margin())
                #         else:
                #             mail_to = mail_to + ' 15min : ' + '-' + str(self.minute15_trader.get_ma_margin())
                #         is_buy = True

                # if self.is_main_trader_growup(self.minute30_trader, 1.2, 23):
                #     if self.day_trader.candles[1].is_yangbong():
                #         print(' +30min ')
                #         if self.minute30_trader.is_ma50_over_than_ma15():
                #             mail_to = mail_to + ' 30min : ' + '+' + str(self.minute30_trader.get_ma_margin())
                #         else:
                #             mail_to = mail_to + ' 30min : ' + '-' + str(self.minute30_trader.get_ma_margin())
                #         is_buy = True

                # if self.is_main_trader_growup(self.minute60_trader, 1.3, 15):
                #     if self.day_trader.candles[1].is_yangbong():
                #         print(' +60min ')
                #         if self.minute60_trader.is_ma50_over_than_ma15():
                #             mail_to = mail_to + ' 60min : ' + '+' + str(self.minute60_trader.get_ma_margin())
                #         else:
                #             mail_to = mail_to + ' 60min : ' + '-' + str(self.minute60_trader.get_ma_margin())
                #         is_buy = True

                # if self.is_main_trader_growup(self.minute240_trader, 2, 8):
                #     if self.minute240_trader.is_ma50_over_than_ma15() :
                #         mail_to = mail_to + ' 240min : ' + '+' + str(self.minute240_trader.get_ma_margin())
                #     else:
                #         mail_to = mail_to + ' 240min : ' + '-' + str(self.minute240_trader.get_ma_margin())
                #     is_buy = True


                # if is_buy :
                #     if self.minute30_trader.is_ma120_over_than_ma15():
                #         mail_to = mail_to + ' 30min(120-Line) : ' + '+' + str(self.minute60_trader.get_ma_margin120())
                #     else:
                #         mail_to = mail_to + ' 30min(120-Line) : ' + '-' + str(self.minute60_trader.get_ma_margin120())

                #     if self.minute60_trader.is_ma120_over_than_ma15():
                #         mail_to = mail_to + ' 60min(120-Line) : ' + '+' + str(self.minute60_trader.get_ma_margin120())
                #     else:
                #         mail_to = mail_to + ' 60min(120-Line) : ' + '-' + str(self.minute60_trader.get_ma_margin120())

                #     if self.minute240_trader.is_ma120_over_than_ma15():
                #         mail_to = mail_to + ' 240min(120-Line) : ' + '+' + str(self.minute240_trader.get_ma_margin120())
                #     else:
                #         mail_to = mail_to + ' 240min(120-Line) : ' + '-' + str(self.minute240_trader.get_ma_margin120())
                     

                # if self.minute60_trader.is_ma_growup() and self.minute60_trader.get_ma_margin120() < 0.7 :
                #     print(' +60min ')
                #     if self.minute60_trader.is_ma120_over_than_ma15():
                #         mail_to = mail_to + ' 60min_margin_best : ' + '+' + str(self.minute60_trader.get_ma_margin120())
                #     else:
                #         mail_to = mail_to + ' 60min_margin_best : ' + '-' + str(self.minute60_trader.get_ma_margin120())
                #     is_buy = True

                # if self.minute240_trader.is_ma_growup() and self.minute240_trader.get_ma_margin120() < 1:
                #     if self.minute240_trader.is_ma120_over_than_ma15() :
                #         mail_to = mail_to + ' 240min_margin_best : ' + '+' + str(self.minute240_trader.get_ma_margin120())
                #     else:
                #         mail_to = mail_to + ' 240min_margin_best : ' + '-' + str(self.minute240_trader.get_ma_margin120())
                #     is_buy = True


                # if self.is_nice_trader(self.minute60_trader):
                #     print('go to buy')
                #     is_buy = True
                
                if is_write_db:
                    print('write_database')
                    self.write_log(market_name, str(self.minute15_trader.candles[0].trade_price))

                if is_buy :
                    #log 기록
                    print(mail_to)
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


