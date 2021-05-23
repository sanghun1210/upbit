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

    ######################################################################

    def is_trader_growup(self, trader):
        return trader.ma(5) > trader.ma(15) 

    def is_sub_trader_growup(self, trader, margin):
        if trader.is_ma_growup():
             return True
        if trader.ma(15) > trader.ma(50):
            return True
        elif trader.ma(50) - trader.ma(15) >= margin:
            return True
        return False

    def is_third_trader_growup(self, trader, margin):
        if trader.ma(15) > trader.ma(50):
            return True
        elif trader.ma(50) - trader.ma(15) >= margin:
            return True
        return False

    def is_ma_growup(self, trader):
        return trader.ma(5) > trader.ma(10) > trader.ma(20)

    def is_ma_growup_long(self, trader):
        return trader.ma(5) > trader.ma(60) > trader.ma(120)

    def get_margin(self, a, b):
        ma = 0
        if a > b:
            ma = ((a - b) / a) * 100
        else : 
            ma = ((b - a) / b) * 100
        return ma

    def is_convergence_section(self, trader, max_margin):
        ma_list = [trader.ma(5), trader.ma(10), trader.ma(20), trader.ma(60), trader.ma(120)]
        max_ma = max(ma_list)
        min_ma = min(ma_list)
        return self.get_margin(max_ma, min_ma) <= max_margin

    def is_convergence_over(self, trader):
        ma_list = [trader.ma(5), trader.ma(10), trader.ma(20), trader.ma(60), trader.ma(120)]
        max_ma = max(ma_list)
        return trader.candles[0].trade_price > trader.ma(120)
            
    def init_traders(self, market_name):
        # self.week_trader = WeekTrader(market_name, 5)
        # time.sleep(0.1)
        # self.minute1_trader = Minute1Trader(market_name, 120)
        # time.sleep(0.1)
        self.minute3_trader = Minute3Trader(market_name, 120)
        time.sleep(0.1)
        self.minute5_trader = Minute5Trader(market_name, 120)
        time.sleep(0.1)
        self.minute10_trader = Minute10Trader(market_name, 120)
        time.sleep(0.1)
        self.minute15_trader = Minute15Trader(market_name, 120)
        time.sleep(0.1)
        self.minute30_trader = Minute30Trader(market_name, 120)
        time.sleep(0.1)
        self.minute60_trader = Minute60Trader(market_name, 120)
        time.sleep(0.1)
        self.minute240_trader = Minute240Trader(market_name, 50)
        time.sleep(0.1)
        self.day_trader = DayTrader(market_name, 120)

    def is_low_point(self, trader):
        if trader.candles[1].is_yangbong() == False and (trader.candles[0].trade_price > trader.candles[1].trade_price) and (trader.candles[0].candle_acc_trade_volume > (trader.candles[1].candle_acc_trade_volume * 1.5)):
            return True

    def find_best_markets(self, market_group_name):
        market_name_list = []
        
        self.market_group = self.get_market_groups(market_group_name)
        
        for market in self.market_group:
            market_name = market.get("market")
            is_buy = False
            is_write_db = False

            try:
                print('')
                print('checking...', market_name)
                self.init_traders(market_name)
                mail_to = market_name + ':'    
                mail_to = mail_to + ' => ' + str(self.minute15_trader.candles[0].trade_price)

                # if self.day_trader.is_pre_candle_yangbong() == False:
                #     continue

                # if self.minute240_trader.is_ma_growup() == False:
                #     continue

                # if self.minute30_trader.is_goup_with_volume():
                #     print(' 30_goup_with_volume ')
                #     mail_to = mail_to + ' 30_goup_with_volume '
                #     is_buy = True
                #     is_write_db = True

                # if self.minute60_trader.is_goup_with_volume():
                #     print(' 60_goup_with_volume ')
                #     mail_to = mail_to + ' 60_goup_with_volume '
                #     is_buy = True
                #     is_write_db = True
                      
                if self.minute10_trader.is_golden_cross(2) and self.minute10_trader.is_ma_growup():
                    if  self.is_sub_trader_growup(self.minute30_trader, 4) and self.is_third_trader_growup(self.minute240_trader, 7):
                        print(' +10min ')
                        mail_to = mail_to + ' +10min cross margin : ' + str(self.minute10_trader.get_ma_margin())
                        is_buy = True
                        is_write_db = True

                if self.minute15_trader.is_golden_cross(2) and self.minute15_trader.is_ma_growup():
                    if self.is_sub_trader_growup(self.minute30_trader, 5) and self.is_third_trader_growup(self.minute240_trader, 7):
                        print(' +15min ')
                        mail_to = mail_to + ' +15min cross margin : ' + str(self.minute15_trader.get_ma_margin())
                        is_buy = True
                        is_write_db = True

                if self.minute30_trader.is_golden_cross(3) and self.minute30_trader.is_ma_growup():
                    if self.is_sub_trader_growup(self.minute60_trader, 5) and self.is_third_trader_growup(self.minute240_trader, 7):
                        print(' +30min ')
                        mail_to = mail_to + ' +30min cross margin : ' + str(self.minute30_trader.get_ma_margin())
                        is_buy = True
                        is_write_db = True

                # if self.is_trader_growup(self.minute240_trader) :
                #     print(' +240min ')
                #     mail_to = mail_to + ' +240min '
                #     is_buy = True

                # if self.is_trader_growup(self.minute60_trader, 0.3):
                #     if self.is_ma_growup_long(self.minute3_trader) and self.is_ma_growup_long(self.minute5_trader) and self.is_ma_growup_long(self.minute10_trader) and self.is_ma_growup_long(self.minute15_trader) and self.is_ma_growup_long(self.minute30_trader) : 
                #         print(' +60min convergence!')
                #         mail_to = mail_to + ' +60min convergence! '
                #         is_buy = True
                #         is_write_db = True

                # if self.day_trader.is_goup_with_volume():
                #     print(' +day ')
                #     mail_to = mail_to + ' +day goup_with_volume '
                #     is_buy = True
                #     is_write_db = True

                # if self.minute60_trader.is_goup_with_volume():
                #     print(' +60 ')
                #     mail_to = mail_to + ' +60 goup_with_volume '
                #     is_buy = True
                #     is_write_db = True

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


