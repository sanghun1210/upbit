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

    def is_week_240min_30min_good(self):
        return self.week_trader.is_goup_with_volume() and self.minute240_trader.is_goup_with_volume() and self.minute30_trader.is_goup_with_volume() and self.minute30_trader.is_ma_growup()

    def is_week_60min_good(self):
        return self.week_trader.is_goup_with_volume() and self.minute60_trader.is_goup_with_volume() and self.minute60_trader.is_ma_growup()

    def is_day_30min_good(self):
        return self.day_trader.is_goup_with_volume() and self.minute30_trader.is_goup_with_volume() and self.minute30_trader.is_ma_growup()

    def is_week_day_15min_good(self):
        return self.week_trader.is_goup_with_volume() and self.day_trader.is_goup_with_volume() and self.minute15_trader.is_goup_with_volume() and self.minute15_trader.is_ma_growup()

    def init_traders(self, market_name):
        self.week_trader = WeekTrader(market_name, 5)
        time.sleep(0.1)
        self.day_trader = DayTrader(market_name, 5)
        time.sleep(0.1)
        self.minute240_trader = Minute240Trader(market_name, 20)
        time.sleep(0.1)
        self.minute60_trader = Minute60Trader(market_name, 20)
        time.sleep(0.1)
        self.minute30_trader = Minute30Trader(market_name, 20)
        time.sleep(0.1)
        self.minute15_trader = Minute15Trader(market_name, 20)
        time.sleep(0.1)
        self.minute10_trader = Minute10Trader(market_name, 20)
        time.sleep(0.1)
        self.minute5_trader = Minute5Trader(market_name, 20)
        time.sleep(0.1)
        self.minute3_trader = Minute3Trader(market_name, 20)
        time.sleep(0.1)

    def find_best_markets(self, market_group_name):
        market_name_list = []
        
        if self.market_group == None:
            self.market_group = self.get_market_groups(market_group_name)
        
        for market in self.market_group:
            is_goup = False
            market_name = market.get("market")

            try:
                print('checking...', market_name)
                self.init_traders(market_name)
                mail_to = ""

                if self.is_week_240min_30min_good():
                    print('nice!! - is_week_240min_30min_good')
                    mail_to = mail_to + (market_name + ' (nice!! - is_week_240min_30min_good)')
                    is_goup = True
            
                if self.is_week_60min_good():
                    print('nice!! - is_week_60min_good')
                    mail_to = mail_to + (market_name + ' (nice!! - is_week_60min_good)')
                    is_goup = True

                if self.is_day_30min_good():
                    print('nice!! - is_day_30min_good')
                    mail_to = mail_to + (market_name + ' (nice!! - is_day_30min_good)')
                    is_goup = True

                if self.is_week_day_15min_good():
                    print('nice!! - is_week_day_15min_good')
                    mail_to = mail_to + (market_name + ' (nice!! - is_week_day_15min_good)')
                    is_goup = True

            except Exception as e:
                print("raise error ", e)

            # if self.is_240ma_up_with_volume60min():
            #     print('nice!! - is_240ma_up_with_volume60min')
            #     mail_to = mail_to + (market_name + ' (is_240ma_up_with_volume60min)')
            #     is_goup = True
            
            # if self.is_240ma_up_with_volume30min():
            #     print('is_240ma_up_with_volume30min')
            #     mail_to = mail_to + (market_name + ' (is_240ma_up_with_volume30min)')
            #     is_goup = True

            # if self.is_60_volume_5min_volumn():
            #     print('is_60_volume_5min_volumn')
            #     mail_to = mail_to + (market_name + ' (is_60_volume_5min_volumn)')
            #     is_goup = True
            
            # if self.is_240ma_up_with_volume15min():
            #     print('is_240ma_up_with_volume15min')
            #     mail_to = mail_to + (market_name + ' (is_240ma_up_with_volume15min)')
            #     is_goup = True

            # if self.is_60ma_up_with_volume3min():
            #     print('is_60ma_up_with_volume3min')
            #     mail_to = mail_to + (market_name + ' (is_60ma_up_with_volume3min)')
            #     is_goup = True

            #4시간 봉 볼륨업 10분봉 볼륨업
            # if self.is_240go_up_with_volume():
            #      print('is_240go_up_with_volume')
            #      mail_to = mail_to + (market_name + ' (is_240go_up_with_volume)')
            #      is_goup = True

            # if self.is_240go_up_with_volume():
            #     print('is_240go_up_with_volume')
            #     mail_to = mail_to + (market_name + ' (is_240go_up_with_volume)')
            #     is_goup = True
            
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


