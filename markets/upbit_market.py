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

class UpbitMarket(BaseMarket):
    def __init__(self):
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
        self.minute1_trader = None

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

    #60분봉 기세확인 10분봉 고업드매수량
    # 하락장에서는 비활성화
    # 상승장 또는 횡보장에서는 유효하므로 다시 활성화를 고려한다.
    # def is_60ma_up_with_volume10min(self):
    #     return self.minute60_trader.is_ma_growup() and self.minute10_trader.is_goup_with_volume(3)

    # def is_60ma_up_with_volume3min(self):
    #     return self.minute60_trader.is_ma_growup() and self.minute3_trader.is_goup_with_volume(3)

    # #30분봉 기세확인 5분봉 고업드매수량
    # def is_30ma_up_with_volume5min(self):
    #     return self.minute30_trader.is_ma_growup() and self.minute5_trader.is_goup_with_volume(3)

    # #240분봉 기세확인 1시간봉 고업위즈 매수량
    # def is_240ma_up_with_volume60min(self):
    #     return self.minute240_trader.is_ma_growup() and self.minute60_trader.is_goup_with_volume(3)

    # #240분봉 기세확인 1시간봉 고업위즈 매수량
    # def is_240ma_up_with_volume30min(self):
    #     return self.minute240_trader.is_ma_growup() and self.minute30_trader.is_goup_with_volume(3)

    # def is_240ma_up_with_volume15min(self):
    #     return self.minute240_trader.is_ma_growup() and self.minute15_trader.is_goup_with_volume(3)

    ######################################################################

    def is_trader_growup(self, trader):
        if trader.is_ma50_over_than_ma15() == False :
            return trader.is_ma_growup_lite()
        else :
            return trader.is_ma_growup() 
            

    def init_traders(self, market_name):
        self.week_trader = WeekTrader(market_name, 5)
        time.sleep(0.1)
        self.day_trader = DayTrader(market_name, 50)
        time.sleep(0.1)
        self.minute240_trader = Minute240Trader(market_name, 50)
        time.sleep(0.1)
        self.minute60_trader = Minute60Trader(market_name, 50)
        time.sleep(0.1)
        self.minute30_trader = Minute30Trader(market_name, 50)
        time.sleep(0.1)
        self.minute15_trader = Minute15Trader(market_name, 50)
        time.sleep(0.1)
        self.minute10_trader = Minute10Trader(market_name, 50)
        time.sleep(0.1)
        self.minute5_trader = Minute5Trader(market_name, 50)
        time.sleep(0.1)
        # self.minute3_trader = Minute3Trader(market_name, 50)
        # time.sleep(0.1)
        # self.minute1_trader = Minute1Trader(market_name, 50)
        # time.sleep(0.1)

    def find_best_markets(self, market_group_name):
        market_name_list = []
        
        self.market_group = self.get_market_groups(market_group_name)
            
        for market in self.market_group:
            is_check5_growup = False
            is_check15_growup = False
            is_check15_growup = False
            is_check30_growup = False
            is_check60_growup = False
            is_check240_growup = False
            is_checkday_growup = False
            market_name = market.get("market")

            try:
                print('checking...', market_name)
                self.init_traders(market_name)
                mail_to = market_name + ':'

                if self.is_trader_growup(self.minute15_trader):
                    ma_str = self.minute15_trader.get_ma_print()
                    print(' - 15min : '+ ma_str)
                    mail_to = mail_to + '[ 15min : '+ ma_str  
                    if self.minute15_trader.is_ma_volume_up() : 
                        mail_to = mail_to + ' v_up! ]'
                    else :
                        mail_to = mail_to + ' ]'
                        
                if self.is_trader_growup(self.minute30_trader):
                    ma_str = self.minute30_trader.get_ma_print()
                    print(' - 30min : '+ ma_str)
                    mail_to = mail_to + '[ 30min : '+ ma_str  
                    if self.minute30_trader.is_ma_volume_up() : 
                        mail_to = mail_to + ' v_up! ]'
                    else :
                        mail_to = mail_to + ' ]'

                if self.is_trader_growup(self.minute60_trader):
                    ma_str = self.minute60_trader.get_ma_print()
                    print(' - 60min : '+ ma_str)
                    mail_to = mail_to + '[ 60min : '+ ma_str  
                    if self.minute60_trader.is_ma_volume_up() : 
                        mail_to = mail_to + ' v_up! ]'
                    else :
                        mail_to = mail_to + ' ]'

                if self.is_trader_growup(self.minute240_trader):
                    ma_str = self.minute240_trader.get_ma_print()
                    print(' - 240min : '+ ma_str)
                    mail_to = mail_to + '[ 240min : '+ ma_str  
                    if self.minute240_trader.is_ma_volume_up() : 
                        mail_to = mail_to + ' v_up! ]'
                    else :
                        mail_to = mail_to + ' ]'

                if self.is_trader_growup(self.day_trader):
                    ma_str = self.day_trader.get_ma_print()
                    print(' - day : '+ ma_str)
                    mail_to = mail_to + '[ day : '+ ma_str  
                    if self.day_trader.is_ma_volume_up() : 
                        mail_to = mail_to + ' v_up! ]'
                    else :
                        mail_to = mail_to + ' ]'

                mail_to = mail_to + ' => ' + str(self.minute10_trader.candles[0].trade_price)
                is_buy = False
                max_count = 1

                if self.is_trader_growup(self.minute15_trader):
                    if self.is_trader_growup(self.minute30_trader) and self.is_trader_growup(self.minute5_trader):
                        print('30min go to check!!!!')
                        mail_to = mail_to + ' => (+15min)'
                #        is_buy = True


                if self.is_trader_growup(self.minute60_trader) :
                    if self.is_trader_growup(self.minute240_trader) and self.is_trader_growup(self.minute30_trader):
                        print('60min go to check!!!!')
                        mail_to = mail_to + ' => (+60min)'
                #        is_buy = True

                if self.is_trader_growup(self.minute240_trader) :
                    if self.is_trader_growup(self.day_trader) and self.is_trader_growup(self.minute60_trader) :
                        print('240min go to check!!!!')
                        mail_to = mail_to + ' => (+240min)'
                        is_buy = True

                # if self.is_trader_growup(self.minute240_trader) and self.is_trader_growup(self.minute60_trader):
                #     # 앞으로의 미래를 주도할 코인
                #     # 앞으로 꼭 가져갈 코인
                #         print('day go to check!!!!')
                #         mail_to = mail_to + ' (+ day)'
                #         is_buy = True

                if is_buy == False :
                    continue

                market_name_list.append(mail_to)
                    
            except Exception as e:
                print("raise error ", e)
            
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


