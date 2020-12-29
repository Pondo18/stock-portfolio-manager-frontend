import yfinance as yf

import pandas as pd

from pandas_datareader import data as pdr

yf.pdr_override()


def get_current_price_of_holding(holding):
    obj = yf.Ticker(holding)
    holding_data = obj.history("1d")
    price = holding_data["Open"].values[0]
    price = round(price, 2)
    return price


def holding_exists(holding):
    obj = yf.Ticker(holding)
    holding_data = obj.history("1d")
    no_data = holding_data.values
    if no_data.size == 0:
        return False
    else:
        return True


def get_holding_price_for_period(holding, period):
    obj = yf.Ticker(holding)
    holding_data = obj.history(period)
    price = holding_data["Open"]
    return price


def get_all_holdings_prices(holdings, period):
    tickers = yf.Tickers(holdings)
    all_holdings = []
    for holding in holdings:
        tickers.tickers


def get_holding_sector(holding):
    ticker = yf.Ticker(holding)
    return ticker.info["sector"]
