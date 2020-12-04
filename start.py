import yfinance as yf


msft = yf.Ticker("SAP")

opt = msft.option_chain('2020-12-18')
print(opt)
