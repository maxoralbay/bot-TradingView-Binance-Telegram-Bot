import json, time, config
from api.binance_features_api import BinanceFeaturesApi
from api.message_filter_functions import *
from flask import Flask, request, jsonify
from handler import *
import logging
from logging.config import fileConfig
## add date with time
## add where it is coming from
##logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
fileConfig('logging_config.ini')
logger = logging.getLogger()
app = Flask(__name__)

# added logger to handle all logs
# bot = MainBot() #Handles all telegram communication
def get_timestamp():
    timestamp = time.strftime("%Y-%m-%d %X")
    return timestamp


def tradingview_formatter(data: str):
    pairs = data.split()
    # Use dictionary comprehension to create the dictionary
    return {pair.split('=')[0]: pair.split('=')[1] for pair in pairs}


def clean_symbol(symbol: str):
    # BINANCE:BTCUSDT
    return symbol.split(':')[1]


## add index page
@app.route('/')
def index():
    print(get_timestamp(), "Service is running!")
    return 'Welcome to the Binance Alert bot'


## ---- RECEIVE TRADINGVIEW WEBHOOK AND PLACE ORDER ---- ##
@app.route('/alert-binance', methods=['POST'])
def webhook_process():
    # client = Binance(config.API_KEY, config.SECRET_KEY)
    client = BinanceFeaturesApi(config.API_KEY, config.SECRET_KEY)
    ## get plain/text data from tradingview
    raw_data = request.data.decode('utf-8')

    data = tradingview_formatter(raw_data)
    logger.info('raw_data', data)
    try:
        if data["code"] == config.CODE:
            symbol = clean_symbol(data['symbol'])
            type = data['type'].upper()
            quantity = data['quantity']
            side = data['side'].upper()
            price = data['current_price'] or 0
            timeInForce = data['timeInForce'] or 'GTC'
            order_response = None
            if type == 'MARKET':
                order_response = client.market_order(symbol, side, type, quantity, price)
            elif type == 'LIMIT':
                order_response = client.limit_order(symbol, side, type, timeInForce, quantity, price)

            logger.info(f'order_response: {order_response}')
            return {
                    'code': 'success'
                }
        else:
            logging.error('Invalid code')
            # admin_message(tradingview_symbol, tradingview_quantity, "Denied")
            return {
                'code': "failed",
                'message': "Check console log for error"
            }
    except Exception as e:
        logger.error(str(e))
        return {
            'code': 'failed',
            'message': str(e)
        }
