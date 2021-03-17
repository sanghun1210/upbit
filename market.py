import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode

import requests

access_key = 'H9ivtJHuRDDbHoLrjcZF1VzANakAl7jlMKUTBPwx'
secret_key = '669PEGw3ExqC2a1gxyMguuRNjAXd0YcYVHBiHftC'
server_url = 'https://api.upbit.com'

class Market():
    def __init__(self, market_name):
        self.market_name = market_name
        self.bid_fee

    def check(self):
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


    def bid(self, money):
        query = {
            'market': ' ',
            'side': 'bid',
            'volume': '0.01',
            'price': '100.0',
            'ord_type': 'limit',
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

        res = requests.post(server_url + "/v1/orders", params=query, headers=headers)


