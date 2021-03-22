import os
import jwt
import uuid
import hashlib
import json
from urllib.parse import urlencode
from candle import *

import requests

access_key = 'y4YiH7yQ6IV7DH1kr8aaDxrNwrirvxqZxHRAY3gO'
secret_key = 'nKowNJTxJ1xyTiQLLNZp1G6NKYP5txsR2OxDY1DV'
server_url = 'https://api.upbit.com'

class Market():
    def __init__(self, market_name):
        self.market_name = market_name
        self.is_already_have_this = False

    def is_already_have(self):
        query = {
            'market': self.market_name,
        }
        query_string = urlencode(query).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, secret_key)
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        res = requests.get(server_url + "/v1/orders/chance", params=query, headers=headers)
        print(res.json())
        ask_account = res.json()["ask_account"]
        coin_balance = ask_account["balance"]
        print(coin_balance)
        self.is_already_have_this = (coin_balance != '0.0')
        print("is_already_have_this coin : ", self.is_already_have_this)
        return self.is_already_have_this
        
    def bid(self, money):            
        query = {
            'market': self.market_name,
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
            'access_key': access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, secret_key)
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        res = requests.post(server_url + "/v1/orders", params=query, headers=headers)


