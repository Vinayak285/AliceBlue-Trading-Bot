import pandas as pd
import os
from time import sleep
import datetime
from constants import LOGS_PATH, TRANSACTIONS_LOGS, TRANS_PATH, TICKERS_PATH, NIFTY50_TICKERS

from alice_blue import AliceBlue
from constants import USERNAME, PASSWORD, TWO_FA, APP_SECRET, APP_ID


def get_today_date():
    return datetime.datetime.today().strftime('%Y-%m-%d')


def round_(x, base=.05):
    return base * round(x / base)


def get_client_balance(client):
    bal_resp = client.get_balance()
    balance = float(bal_resp['data']['cash_positions'][0]['net'])
    return balance


def wait_till_trading_close():
    while True:
        now = datetime.datetime.now()
        current_time = [now.hour, now.minute, now.second]
        if current_time == [15, 0, 0]:
            break
        else:
            sleep(0.5)
    print("Trading window closed, exiting...")


def get_client(contracts_download=True):
    try:
        access_token = AliceBlue.login_and_get_access_token(username=USERNAME, password=PASSWORD, twoFA=TWO_FA,
                                                            app_id=APP_ID, api_secret=APP_SECRET)

        if contracts_download:
            client = AliceBlue(username=USERNAME, password=PASSWORD, access_token=access_token,
                               master_contracts_to_download=["NSE"])
        else:
            client = AliceBlue(username=USERNAME, password=PASSWORD, access_token=access_token)

        print("Logged in successfully!")

    except:
        print("Failed logging in!")
        print("Trying again in 1 minute...")
        sleep(60)
        return get_client()

    return client


def nifty50_tickers(path=TICKERS_PATH):
    df = pd.read_csv(path)
    df.columns = [i.lower().strip().replace(" ", "_") for i in df.columns]
    tickers = df.symbol.tolist()
    return tickers


def load_transactions_logs():
    if not os.path.exists(LOGS_PATH):
        trans_logs = TRANSACTIONS_LOGS
    else:
        trans_logs = pd.read_csv(LOGS_PATH).to_dict("list")
    return trans_logs


def update_transactions(trans_logs, entry):
    """entry: Datetime, Ticker, Order Type, Order ID, Quantity"""
    for i, j in zip(trans_logs.keys(), entry):
        trans_logs[i].append(j)
    return trans_logs


def save_transactions_logs(trans_logs):
    if not os.path.exists(TRANS_PATH):
        os.mkdir(TRANS_PATH)

    df = pd.DataFrame(trans_logs)
    if os.path.exists(LOGS_PATH):
        df2 = pd.read_csv(LOGS_PATH)
        df = df.append(df2)
        df.sort_index(inplace=True)
    df.to_csv(LOGS_PATH, index=False)
    print("Saved transaction logs successfully!")
