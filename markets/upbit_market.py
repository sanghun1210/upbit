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

    def get_market_filters(self):
        #대세를 보려면 주봉을 봐야 한다.
        market_list = ['KRW-UPP', 'KRW-FLOW', 'KRW-AXS', 'KRW-SAND', 'KRW-STX', 'KRW-POLY', 'KRW-FCT2', 'KRW-IOST', 'KRW-AQT', 'KRW-TON', 'KRW-GLM', 'KRW-CRE', 'KRW-REP', 'KRW-XEM', 'KRW-TT', 'KRW-DAWN']
        return market_list


    def get_margin(self, a, b):
        ma = 0
        if a > b:
            ma = ((a - b) / a) * 100
        else : 
            ma = ((b - a) / b) * 100
        return ma

    
            
    def init_traders(self, market_name, src_logger):
        # self.minute1_trader = Minute1Trader(market_name, 120)
        # time.sleep(0.1)
        # self.minute3_trader = Minute3Trader(market_name, 120)
        # time.sleep(0.1)
        # self.minute5_trader = Minute5Trader(market_name, 120, src_logger)
        # time.sleep(0.1)
        # self.minute10_trader = Minute10Trader(market_name, 120, src_logger)
        time.sleep(0.1)
        self.minute15_trader = Minute15Trader(market_name, 120, src_logger)
        time.sleep(0.1)
        self.minute30_trader = Minute30Trader(market_name, 80, src_logger)
        time.sleep(0.1)
        self.minute60_trader = Minute60Trader(market_name, 80, src_logger)
        time.sleep(0.1)
        self.minute240_trader = Minute240Trader(market_name, 80, src_logger)
        time.sleep(0.1)
        self.day_trader = DayTrader(market_name, 40, src_logger)
        time.sleep(0.1)
        self.week_trader = WeekTrader(market_name, 20, src_logger)

    def mov_avr_line_check_point(self, trader, max_margin):
        if (trader.ma(10) <= trader.ma(40) and self.get_margin(trader.ma(10), trader.ma(40)) <= 0.1) or \
            (trader.ma(10) > trader.ma(40) and self.get_margin(trader.ma(10), trader.ma(40)) <= max_margin):
            return 1
        elif trader.ma(10) > trader.ma(40) :
            if (trader.ma(5) <= trader.ma(20) and self.get_margin(trader.ma(5), trader.ma(20)) <= 0.1) or \
                (trader.ma(5) > trader.ma(20) and self.get_margin(trader.ma(5), trader.ma(20)) <= max_margin):
                return 1
            elif trader.ma(5) > trader.ma(20):
                if trader.ma(5) > trader.ma(10) and self.get_margin(trader.ma(5), trader.ma(10)) <= max_margin:
                    return 1
        return 0

    def is_nice_trader(self, trader, max_bol_width):
        self.logger.info('get_bollinger_bands_width(8) ==> ' + str(trader.get_bollinger_bands_width(8)))
        self.logger.info('self.get_margin(self.ma(5), self.ma(20)) ==> ' + str(self.get_margin(trader.ma(5), trader.ma(20))))
        self.logger.info('trader.rsi(0, 14), trader.rsi_ma(5), trader.rsi_ma(10)==> ' + str(trader.rsi(0, 14)) + ' ' + str(trader.rsi_ma(5)) + ' ' + str(trader.rsi_ma(10)))

        if (trader.ma(5) <= trader.ma(20) and self.get_margin(trader.ma(5), trader.ma(20)) < 0.3) or \
            (trader.ma(5) > trader.ma(20) and self.get_margin(trader.ma(5), trader.ma(20)) < 0.5):
            current_rsi = trader.rsi(0, 14)
            print('rsi check->')
            if current_rsi >= 45 and current_rsi <= 60:
                mos = trader.get_momentum_list()
                self.logger.info('mos[0], mos[5], mos[8] : '+  str(mos[0]) + ' ' + str(mos[5]) + ' ' + str(mos[8]))
                print('mos[0], mos[5], mos[8] : '+  str(mos[0]) + ' ' + str(mos[5]) + ' ' + str(mos[8]))
                print('rsi[0], rsi[1] : '+  str(trader.rsi(0,14)) + ' ' + str(trader.rsi(1,14)))
                if mos[0] > (mos[3] + 1) and trader.rsi(0, 14) > trader.rsi_ma(3) and trader.candles[0].trade_price > trader.ma(5):
                    self.mail_to = self.mail_to + 'good pattern'
                    return True
        
        if trader.get_bollinger_bands_width(8) < max_bol_width:
            stdev = trader.get_bollinger_bands_standard_deviation(8)
            low_band = trader.ma(8) - (stdev * 2)
            if low_band >= trader.candles[0].low_price and trader.rsi(0, 14) <= 50:
                print('it\'s low')
                self.mail_to = self.mail_to + 'low pattern'
                return True

    def is_nice_trader60(self, trader, max_bol_width):
        self.logger.info('get_bollinger_bands_width(8) ==> ' + str(trader.get_bollinger_bands_width(8)))
        self.logger.info('self.get_margin(self.ma(5), self.ma(20)) ==> ' + str(self.get_margin(trader.ma(5), trader.ma(20))))
        self.logger.info('trader.rsi(0, 14), trader.rsi_ma(5), trader.rsi_ma(10)==> ' + str(trader.rsi(0, 14)) + ' ' + str(trader.rsi_ma(5)) + ' ' + str(trader.rsi_ma(10)))

        if self.get_margin(trader.ma(5), trader.ma(20)) < 0.4 :
            current_rsi = trader.rsi(0, 14)
            print('rsi check->')
            if current_rsi >= 45 and current_rsi <= 60:
                mos = trader.get_momentum_list()
                self.logger.info('mos[0], mos[5], mos[8] : '+  str(mos[0]) + ' ' + str(mos[5]) + ' ' + str(mos[8]))
                print('mos[0], mos[5], mos[8] : '+  str(mos[0]) + ' ' + str(mos[5]) + ' ' + str(mos[8]))
                print('rsi[0], rsi[1] : '+  str(trader.rsi(0,14)) + ' ' + str(trader.rsi(1,14)))
                if mos[0] > (mos[3] + 1) and trader.rsi(0, 14) > trader.rsi_ma(3) and trader.candles[0].trade_price > trader.ma(5):
                    self.mail_to = self.mail_to + 'good pattern'
                    return True

        if trader.get_bollinger_bands_width(8) < max_bol_width:
            stdev = trader.get_bollinger_bands_standard_deviation(8)
            low_band = trader.ma(8) - (stdev * 2)
            if low_band >= trader.candles[0].low_price and trader.rsi(0, 14) <= 50:
                print('it\'s low')
                self.mail_to = self.mail_to + 'low pattern'
                return True

    def find_best_markets(self, market_group_name):
        market_name_list = []
        
        self.market_group = self.get_market_groups(market_group_name)
        
        for market in self.market_group:
            market_name = market.get("market")
            is_buy = False
            is_write_db = False

            filters = self.get_market_filters()

            try:
                print('checking...', market_name)
                self.logger.info('checking... ' +  market_name)

                self.init_traders(market_name, self.logger)
                self.mail_to = market_name + ':'    
                self.mail_to = self.mail_to 

                self.logger.info(market_name)

                mos_day = self.day_trader.get_momentum_list()
                mos_240 = self.minute240_trader.get_momentum_list()
                mos_60 = self.minute60_trader.get_momentum_list()

                if self.day_trader.candles[0].trade_price >= self.day_trader.ma(10) and self.day_trader.rsi(0, 14) > 50:
                    self.logger.info('check 240 ======================================')
                    if self.is_nice_trader(self.minute240_trader, 12):
                        print('check240_good')
                        self.mail_to = self.mail_to + ' minute 240 good'
                        is_buy = True

                if self.day_trader.candles[0].trade_price >= self.day_trader.ma(10) and self.day_trader.rsi(0, 14) > 50:
                    self.logger.info('check 60 ======================================')
                    if self.is_nice_trader60(self.minute60_trader, 7):
                        print('check60_good')
                        self.mail_to = self.mail_to + ' minute 60 good'
                        is_buy = True

                # if self.minute240_trader.candles[0].trade_price >= self.minute240_trader.ma(10) and self.minute240_trader.rsi(0, 14) > 50:
                #     self.logger.info('check 30 ======================================')
                #     if self.is_nice_trader(self.minute30_trader, 4):
                #         print('check30_good')
                #         self.mail_to = self.mail_to + ' minute 30 good'
                #         is_buy = True


                # if self.minute60_trader.candles[0].trade_price >= self.minute60_trader.ma(5) and self.minute60_trader.rsi(0,14) > 50:
                #     if self.is_nice_trader(self.minute15_trader):
                #         print('check15_good')
                #         mail_to = mail_to + ' minute 15 good'
                #         is_buy = True

                # temp_point = self.check30_point() * 0.7
                # print('check30_point :' + str(temp_point))
                # self.logger.info('check30_point :' + str(temp_point))
                # point += temp_point

                    
                if is_write_db:
                    print('write_database')
                    self.write_log(market_name, str(self.minute30_trader.candles[0].trade_price))

                if is_buy :
                    market_name_list.append(self.mail_to)

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


