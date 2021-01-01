import yfinance as yf


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


if __name__ == "__main__":
    yf.pdr_override()
