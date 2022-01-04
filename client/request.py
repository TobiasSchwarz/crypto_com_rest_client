import hashlib
import hmac
import string
import time
from enum import Enum


class API_Method(Enum):
    get_instruments = "public/get-instruments"
    get_book = "public/get-book"
    create_order = "private/create-order"


class Request:
    def __init__(self, request_id: int, api_key: string, api_secret_key: string, api_method: API_Method, params: dict):
        self.id = request_id
        self.api_key = api_key
        self.api_secret_key = api_secret_key
        self.api_method = api_method.value
        self.params = params
        self.req = self.create_request()
        self.add_signature()

    def create_request(self):
        return {
            "id": self.id,
            "method": self.api_method,
            "api_key": self.api_key,
            "params": self.params,
            "nonce": int(time.time() * 1000)
        }

    def add_signature(self):
        # First ensure the params are alphabetically sorted by key
        param_string = ""

        if "params" in self.req:
            for key in sorted(self.req['params']):
                param_string += key
                param_string += str(self.req['params'][key])

        sig_payload = self.req['method'] + str(self.req['id']) + self.req['api_key'] + param_string + str(
            self.req['nonce'])

        self.req['sig'] = hmac.new(
            bytes(str(self.api_secret_key), 'utf-8'),
            msg=bytes(sig_payload, 'utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
