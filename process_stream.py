import pandas as pd
import numpy as np
import os
import datetime
import talib

from constants import DATA_DIR, STDEV, N_PERIODS, MA_TYPE, RSI_PERIOD, ROW_SIZE
from helpers import get_today_date

pd.options.mode.chained_assignment = None


def get_date(date):
    """convert unix timestamp to pandas datetime object"""
    date = pd.to_datetime(datetime.datetime.fromtimestamp(date).strftime("%Y-%m-%d %H:%M"))
    return date


def initiate_df():
    df = pd.DataFrame(columns=["Open", "High", "Low", "LTP", "BidQty", "BidRate",
                               "OffQty", "OffRate", "uBand", "mBand", "lBand", "RSI"])
    return df


def gen_bbands(df):
    df['uBand'], df['mBand'], df['lBand'] = talib.BBANDS(df["LTP"], timeperiod=N_PERIODS, nbdevup=STDEV,
                                                         nbdevdn=STDEV, matype=MA_TYPE)
    return df


def gen_rsi(df):
    df["RSI"] = talib.RSI(df["LTP"], timeperiod=RSI_PERIOD)

    return df


def _save_df(df, name):
    file_name = f'{DATA_DIR}/{name}-{get_today_date()}.csv'
    if os.path.exists(file_name):
        df2 = pd.read_csv(file_name, index_col=0, parse_dates=True)
        df = df.append(df2)
        df.sort_index(inplace=True)
    df.to_csv(file_name)
    print(f'Saved {name}-{get_today_date()}.csv successfully')


def save_dfs(dfs):
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
    for (ticker, df) in dfs.items():
        if not df.empty:
            _save_df(df, ticker)


def bad_data(df, data):
    if not df.empty:
        prev_p = df.iloc[-1, 3]
        if any(abs(i / prev_p - 1) > .2 for i in data):
            print(f"Error in some data: \nPrevious price {prev_p}")
            print(f"Current price stream: ", *data, sep='\t')
            return True
    return False


def update_df(df, data):
    req_data = [data["open"], data["high"], data["low"], data["ltp"],
                data["best_bid_quantity"], data["best_bid_price"],
                data["best_ask_quantity"], data["best_ask_price"],
                np.nan, np.nan, np.nan, np.nan]  # for BBANDS and RSI

    # check for any unexpected error in data stream
    if bad_data(df, req_data[:4]):
        return df

    date = get_date(data['exchange_time_stamp'])

    if not df.empty:
        if date == df.index[-1]:
            ltp = req_data[3]
            df.iloc[-1, -8:-4] = req_data[-8:-4]  # bids-offers
            df.iloc[-1, 3] = ltp  # close
            if ltp > df.iloc[-1, 1]:  # high
                df.iloc[-1, 1] = ltp
            elif ltp < df.iloc[-1, 2]:  # low
                df.iloc[-1, 2] = ltp
        else:
            df.loc[date] = req_data  # new date
            df.iloc[-1, 0] = df.iloc[-2, 3]  # new open on next candle = close/ltp of previous candle
    else:
        df.loc[date] = req_data  # first row

    df.drop_duplicates(inplace=True)

    # keeping only ROW_SIZE for reducing memory usage
    if df.shape[0] > ROW_SIZE:
        df = df.iloc[-ROW_SIZE:, ]

    # generate rsi
    if df.shape[0] >= RSI_PERIOD:
        df = gen_rsi(df)

    # generate bbands
    if df.shape[0] >= N_PERIODS:
        df = gen_bbands(df)

    return df
