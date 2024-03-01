from flask import request, jsonify
import csv
import logging
import os
from binance.error import ClientError
from binance.lib.utils import config_logging
from binance.um_futures import UMFutures
config_logging(logging, logging.DEBUG)
from message_filter_functions import *
class BinanceFeaturesApi(object):
    FUTURES_TESTNET_URL = 'https://testnet.binancefuture.com'
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.um_futures_client = UMFutures(key=api_key, secret=secret_key, base_url=self.FUTURES_TESTNET_URL)

    def get_account(self):
        ''' Returns account info '''
        try:
            account_info = self.um_futures_client.get_account()
            logging.info('Account info', account_info)
        except ClientError as error:
            logging.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )

        return account_info

    def send_order(self, order_type, message):
        raw_message = message.text
        if order_type == "limit":
            order_params = limit_order_message_filter(raw_message)
            order_response = self.limit_order(order_params[0], order_params[1], order_params[2], order_params[3], order_params[4], order_params[5])
            order_confirmation = order_message(order_response) #Telegram message sent to user
        elif order_type == "market":
            order_params = market_order_message_filter(raw_message)
            order_response = self.market_order(order_params[0], order_params[1], order_params[2], order_params[3])
            order_confirmation = order_message(order_response) #Telegram message sent to user
        return order_confirmation

    def market_order(self, symbol, side, type, quantity, price):
        ''' Executes limit orders/Depending on type of order commands '''
        response = None
        try:
            order_dictionary = {
                'symbol': symbol,
                'side': side,
                'type': type,
                'quantity': quantity,
                'recvWindow': 59999
            }
            response = self.um_futures_client.new_order(**order_dictionary)
            logging.info('Market order response', response)
        except ClientError as error:
            logging.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )
            return False
        return response

    def limit_order(self, symbol, side, type, quantity, price, timeInForce="GTC"):
            ''' Executes limit orders/Depending on type of order commands '''
            try:
                order_dictionary = {
                    'symbol': symbol,
                    'side': side,
                    'type': type,
                    'quantity': quantity,
                    'price': price,
                    'timeInForce': timeInForce,
                    'recvWindow': 59999
                }
                response = self.um_futures_client.limit_order(**order_dictionary)
                logging.info(response)
            except ClientError as error:
                logging.error(
                    "Found error. status: {}, error code: {}, error message: {}".format(
                        error.status_code, error.error_code, error.error_message
                    )
                )
                return False

            return response

    def cancel_order(self, message):
        try:
            cancel_order_params = cancel_order_message_filter(message)
            dict = { 'symbol': cancel_order_params[0], 'orderId': cancel_order_params[1], "recvWindow": 59999 }
            response = self.um_futures_client(**dict)
            print(response)
            return response
        except Exception as e:
            print(str(e))