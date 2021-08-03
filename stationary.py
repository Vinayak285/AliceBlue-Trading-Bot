import pandas as pd
import datetime

DATA_DIR = "~/Desktop/vinayak_data/db/nifty500.h5"


def get_tradeable_tickers():
    df = pd.read_hdf(DATA_DIR, key='nifty500')
    df = df.loc[(slice(None), "adj_close"), :].droplevel(1)
    today = datetime.datetime.today()
    start_ = today - datetime.timedelta(days=10)
    start = start_.strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")
    print(df[start:end])


get_tradeable_tickers()
