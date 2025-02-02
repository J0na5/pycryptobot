import json
import os
import sys

import pandas
import pytest
import urllib3

BINANCE_CONFIG_JSON = 'binance_config.json'
MOCK_MARKET = 'BTCEUR'

# disable insecure ssl warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.append('.')
# pylint: disable=import-error
from models.exchange.binance import AuthAPI, PublicAPI


def test_instantiate_authapi_without_error():
    api_key = "0000000000000000000000000000000000000000000000000000000000000000"
    api_secret = "0000000000000000000000000000000000000000000000000000000000000000"
    exchange = AuthAPI(api_key, api_secret)
    assert type(exchange) is AuthAPI


def test_instantiate_authapi_with_api_key_error():
    api_key = "ERROR"
    api_secret = "0000000000000000000000000000000000000000000000000000000000000000"

    with pytest.raises(SystemExit) as execinfo:
        AuthAPI(api_key, api_secret)
    assert str(execinfo.value) == 'Binance API key is invalid'


def test_instantiate_authapi_with_api_secret_error():
    api_key = "0000000000000000000000000000000000000000000000000000000000000000"
    api_secret = "ERROR"

    with pytest.raises(SystemExit) as execinfo:
        AuthAPI(api_key, api_secret)
    assert str(execinfo.value) == 'Binance API secret is invalid'


def test_instantiate_authapi_with_api_url_error():
    api_key = "0000000000000000000000000000000000000000000000000000000000000000"
    api_secret = "0000000000000000000000000000000000000000000000000000000000000000"
    api_url = "ERROR"

    with pytest.raises(ValueError) as execinfo:
        AuthAPI(api_key, api_secret, api_url)
    assert str(execinfo.value) == 'Binance API URL is invalid'


def test_instantiate_publicapi_without_error():
    exchange = PublicAPI()
    assert type(exchange) is PublicAPI


def test_config_json_exists_and_valid():
    file = _get_config_file()
    assert os.path.exists(file) == True
    with open(file) as config_file:
        config = json.load(config_file)
        if 'api_key' in config and 'api_secret' in config and 'api_pass' in config and 'api_url' in config:
            api_key = config['api_key']
            api_secret = config['api_secret']
            api_url = config['api_url']
            AuthAPI(api_key, api_secret, api_url)
        elif 'api_key' in config['binance'] and 'api_secret' in config['binance'] and 'api_url' in config['binance']:
            api_key = config['binance']['api_key']
            api_secret = config['binance']['api_secret']
            api_url = config['binance']['api_url']
            AuthAPI(api_key, api_secret, api_url)


def test_get_account(mocker):
    client_response = {
        'makerCommission': 10,
        'takerCommission': 10,
        'buyerCommission': 0,
        'sellerCommission': 0,
        'canTrade': True,
        'canWithdraw': True,
        'canDeposit': True,
        'updateTime': 1620861508183,
        'accountType': 'SPOT',
        'balances': [
            {'asset': 'BTC', 'free': '0.00000000', 'locked': '0.00000000'},
            {'asset': 'LTC', 'free': '0.00000000', 'locked': '0.24944000'}
        ],
        'permissions': ['SPOT']
    }

    with open(_get_config_file()) as config_file:
        config = json.load(config_file)

        api_key = ''
        api_secret = ''
        api_url = ''
        if 'api_key' in config and 'api_secret' in config and 'api_pass' in config and 'api_url' in config:
            api_key = config['api_key']
            api_secret = config['api_secret']
            api_url = config['api_url']
            AuthAPI(api_key, api_secret, api_url)
        elif 'api_key' in config['binance'] and 'api_secret' in config['binance'] and 'api_url' in config['binance']:
            api_key = config['binance']['api_key']
            api_secret = config['binance']['api_secret']
            api_url = config['binance']['api_url']
            AuthAPI(api_key, api_secret, api_url)

    exchange = AuthAPI(api_key, api_secret, api_url)
    assert type(exchange) is AuthAPI

    mocker.patch("models.exchange.binance.Client.get_account", return_value=client_response)
    df = exchange.getAccount()
    assert type(df) is pandas.core.frame.DataFrame

    actual = df.columns.to_list()
    expected = ['currency', 'balance', 'hold', 'available']
    assert len(actual) == len(expected)
    assert all([a == b for a, b in zip(actual, expected)])


def test_get_fees_with_market(mocker):
    client_response = {'success': True, 'tradeFee': [{'maker': 0.001, 'symbol': 'CHZUSDT', 'taker': 0.001}]}
    with open(_get_config_file()) as config_file:
        config = json.load(config_file)

        api_key = ''
        api_secret = ''
        api_url = ''
        if 'api_key' in config and 'api_secret' in config and 'api_pass' in config and 'api_url' in config:
            api_key = config['api_key']
            api_secret = config['api_secret']
            api_url = config['api_url']
            AuthAPI(api_key, api_secret, api_url)
        elif 'api_key' in config['binance'] and 'api_secret' in config['binance'] and 'api_url' in config['binance']:
            api_key = config['binance']['api_key']
            api_secret = config['binance']['api_secret']
            api_url = config['binance']['api_url']
            AuthAPI(api_key, api_secret, api_url)

    exchange = AuthAPI(api_key, api_secret, api_url)
    assert type(exchange) is AuthAPI

    mocker.patch("models.exchange.binance.Client.get_trade_fee", return_value=client_response)
    df = exchange.getFees(MOCK_MARKET)
    assert type(df) is pandas.core.frame.DataFrame

    assert len(df) == 1

    actual = df.columns.to_list()
    expected = ['maker_fee_rate', 'taker_fee_rate', 'usd_volume', 'market']
    assert len(actual) == len(expected)
    assert all([a == b for a, b in zip(actual, expected)])


def test_get_taker_fee_with_market(mocker):
    client_response = {'success': True, 'tradeFee': [{'maker': 0.001, 'symbol': 'CHZUSDT', 'taker': 0.001}]}
    with open(_get_config_file()) as config_file:
        config = json.load(config_file)

        api_key = ''
        api_secret = ''
        api_url = ''
        if 'api_key' in config and 'api_secret' in config and 'api_pass' in config and 'api_url' in config:
            api_key = config['api_key']
            api_secret = config['api_secret']
            api_url = config['api_url']
            AuthAPI(api_key, api_secret, api_url)
        elif 'api_key' in config['binance'] and 'api_secret' in config['binance'] and 'api_url' in config['binance']:
            api_key = config['binance']['api_key']
            api_secret = config['binance']['api_secret']
            api_url = config['binance']['api_url']
            AuthAPI(api_key, api_secret, api_url)

    exchange = AuthAPI(api_key, api_secret, api_url)
    assert type(exchange) is AuthAPI

    mocker.patch("models.exchange.binance.Client.get_trade_fee", return_value=client_response)
    fee = exchange.getTakerFee(MOCK_MARKET)
    assert type(fee) is float
    assert fee == 0.001


def test_get_maker_fee_with_market(mocker):
    client_response = {'success': True, 'tradeFee': [{'maker': 0.001, 'symbol': 'CHZUSDT', 'taker': 0.001}]}
    with open(_get_config_file()) as config_file:
        config = json.load(config_file)

        api_key = ''
        api_secret = ''
        api_url = ''
        if 'api_key' in config and 'api_secret' in config and 'api_pass' in config and 'api_url' in config:
            api_key = config['api_key']
            api_secret = config['api_secret']
            api_url = config['api_url']
            AuthAPI(api_key, api_secret, api_url)
        elif 'api_key' in config['binance'] and 'api_secret' in config['binance'] and 'api_url' in config['binance']:
            api_key = config['binance']['api_key']
            api_secret = config['binance']['api_secret']
            api_url = config['binance']['api_url']
            AuthAPI(api_key, api_secret, api_url)

    exchange = AuthAPI(api_key, api_secret, api_url)
    assert type(exchange) is AuthAPI

    mocker.patch("models.exchange.binance.Client.get_trade_fee", return_value=client_response)
    fee = exchange.getMakerFee(MOCK_MARKET)
    assert type(fee) is float
    assert fee == 0.001


def test_get_orders(mocker):
    client_response = [
        {
            'symbol': 'CHZUSDT',
            'orderId': 123456789,
            'orderListId': -1,
            'clientOrderId': 'SOME-CLIENT-ORDER-ID',
            'price': '0.00000000',
            'origQty': '31.30000000',
            'executedQty': '31.30000000',
            'cummulativeQuoteQty': '15.68161300',
            'status': 'FILLED',
            'timeInForce': 'GTC',
            'type': 'MARKET',
            'side': 'SELL',
            'stopPrice': '0.00000000',
            'icebergQty': '0.00000000',
            'time': 1616845743872,
            'updateTime': 1616845743872,
            'isWorking': True,
            'origQuoteOrderQty': '0.00000000'
        }
    ]

    with open(_get_config_file()) as config_file:
        config = json.load(config_file)

        api_key = ''
        api_secret = ''
        api_url = ''
        if 'api_key' in config and 'api_secret' in config and 'api_pass' in config and 'api_url' in config:
            api_key = config['api_key']
            api_secret = config['api_secret']
            api_url = config['api_url']
            AuthAPI(api_key, api_secret, api_url)
        elif 'api_key' in config['binance'] and 'api_secret' in config['binance'] and 'api_url' in config['binance']:
            api_key = config['binance']['api_key']
            api_secret = config['binance']['api_secret']
            api_url = config['binance']['api_url']
            AuthAPI(api_key, api_secret, api_url)

    exchange = AuthAPI(api_key, api_secret, api_url)
    assert type(exchange) is AuthAPI
    mocker.patch("models.exchange.binance.Client.get_all_orders", return_value=client_response)
    df = exchange.getOrders(MOCK_MARKET)

    assert len(df) > 0

    actual = df.columns.to_list()
    expected = ['created_at', 'market', 'action', 'type', 'size', 'filled', 'status', 'price']
    assert len(actual) == len(expected)
    assert all([a == b for a, b in zip(actual, expected)])


def _get_config_file():
    filename = BINANCE_CONFIG_JSON
    path_to_current_file = os.path.realpath(__file__)
    current_directory = os.path.split(path_to_current_file)[0]
    path_to_file = os.path.join(current_directory, filename)
    return path_to_file
