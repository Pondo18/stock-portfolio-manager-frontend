import yfinance as yf

import pandas as pd

from pandas_datareader import data as pdr

yf.pdr_override()


def get_holding_data(holding):
    obj = yf.Ticker(holding)
    holding_data = obj.history()


def get_price_of_holding(holding):
    obj = yf.Ticker(holding)
    holding_data = obj.history("1d")
    price = holding_data["Open"].values[0]
    price = round(price, 2)
    print(price)
    return price


def holding_exists(holding):
    obj = yf.Ticker(holding)
    holding_data = obj.history("1d")
    no_data = holding_data.values
    if no_data.size == 0:
        return False
    else:
        return True

