import configparser
from alice_blue import TransactionType, ProductType
import datetime

config = configparser.ConfigParser()
config.read("keys.conf")
try:
    section = config["KEYS"]
except KeyError:
    raise Exception("Please configure your keys in keys.conf")

# credentials
APP_ID = config["KEYS"]["APP_ID"]
APP_NAME = config["KEYS"]["APP_NAME"]
APP_SECRET = config["KEYS"]["APP_SECRET"]
USERNAME = config["KEYS"]["USERNAME"]
PASSWORD = config["KEYS"]["PASSWORD"]
TWO_FA = config["KEYS"]["TWO_FA"]

# data directory
DATA_DIR = "data"
TRANS_PATH = "transactions"
LOGS_PATH = f"{TRANS_PATH}/{datetime.datetime.today().strftime('%Y-%m-%d')}-logs.csv"
TICKERS_PATH = f"metadata/ind_nifty50list.csv"
NIFTY50_TICKERS = "https://www1.nseindia.com/content/indices/ind_nifty50list.csv"

# Dictionaries
TRANSACTIONS = {
    TransactionType.Buy: 1,
    TransactionType.Sell: -1
}

TRANSACTIONS_INV = {
    1: TransactionType.Buy,
    -1: TransactionType.Sell
}

INTRADAY = {
    True: ProductType.Intraday,
    False: ProductType.Delivery
}

TRANSACTIONS_LOGS = {
    "Datetime": [],
    "Ticker": [],
    "Order ID": [],
    "Quantity": [],
}


# current position structure [quantity, oms_order_id, target, sl]
NULL_POS_RESP = [0, '', 0., 0.]


# Strategy parameters
# BBANDS PARAMETERS
STDEV = 2
N_PERIODS = 20
MA_TYPE = 1  # {0 : SMA, 1 : EMA, check the ma_type in talib for others}

# RSI
RSI_PERIOD = 14
RSI_OVERBOUGHT = 75
RSI_OVERSOLD = 25

# maximum rows
ROW_SIZE = 50

# Position params
PROFIT_EXIT = 0.5
LOSS_EXIT = 3


# max loss per trade
MAX_LOSS_PER_TRADE = 200
