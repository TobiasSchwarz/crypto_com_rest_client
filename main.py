import json
import time
from pathlib import Path

import requests
import schedule

from client.request import API_Method, Request

counter = 0
config = json.load(open("./resources/config.json"))

base_url = config['url']['default_base']
print(base_url)
USDC_per_order = config['orders']['CRO_USDC']['USDC_per_order']
print(USDC_per_order)


def get_book() -> float:
    try:
        print("Current time: " + time.strftime("%H:%M:%S", time.localtime()))
        book_params: dict = {
            "instrument_name": "CRO_USDC",
            "depth": 5
        }

        print("Send Book CRO_USDC")
        book_req = requests.get(base_url + "public/get-book", book_params)
        book_req_ans = book_req.json()
        print(book_req_ans)
        print(book_req_ans['result'])
        print(book_req_ans['result']['instrument_name'])
        if book_req_ans['result']['instrument_name'] != "CRO_USDC":
            return -1.0
        else:
            print(book_req_ans['result']['data'][0])
            print(book_req_ans['result']['data'][0]['asks'][1][0])
            print(book_req_ans['result']['data'][0]['asks'][5][0])
            return book_req_ans['result']['data'][0]['asks'][5][0]
    except BaseException as ex:
        print(ex)
    return -1.0


def create_market_order():
    print("Current time: " + time.strftime("%H:%M:%S", time.localtime()))
    order_params = {
        "instrument_name": "CRO_USDC",
        "side": "BUY",
        "type": "MARKET",
        "notional": USDC_per_order
    }
    body = Request(counter, config['keys']['api_key'], config['keys']['secret_api_key'], API_Method.create_order,
                   order_params)
    print(body.req)
    print("Create Order CRO_USDC")
    try:

        order_req = requests.post(base_url + "private/create-order", json=body.req)
        order_req_ans = order_req.json()
        print(order_req_ans)
    except BaseException as ex:
        print(ex)


def create_limit_order(price: float, amount: float):
    print("Current time: " + time.strftime("%H:%M:%S", time.localtime()))
    order_params = {
        "instrument_name": "CRO_USDC",
        "side": "BUY",
        "type": "LIMIT",
        "price": price,
        "quantity": amount,
        "time_in_force": "FILL_OR_KILL",
        "exec_inst": "POST_ONLY"
    }
    body = Request(counter, config['keys']['api_key'], config['keys']['secret_api_key'], API_Method.create_order,
                   order_params)
    print(body.req)
    print("Create Order CRO_USDC")
    order_req = requests.post(base_url + "private/create-order", json=body.req)
    order_req_ans = order_req.json()
    print(order_req_ans)


def buy_book():
    print("Current time: " + time.strftime("%H:%M:%S", time.localtime()))
    price = get_book()
    if price < 0.01:
        print("Wrong price " + str(price))
    else:
        amount = round(USDC_per_order / price, 3)
        print(amount)
        create_limit_order(price, amount)


def start_schedule():
    schedule.every(10).minutes.do(get_book)
    schedule.run_all()
    for timestamps in config['orders']['CRO_USDC']['Times']:
        print("Buy schedule at " + timestamps)
        schedule.every().day.at(timestamps).do(create_market_order)


if __name__ == "__main__":
    start_schedule()
    while True:
        schedule.run_pending()
        time.sleep(1)
