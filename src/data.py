from datetime import datetime
from eod import EodHistoricalData
import pickle
import pandas as pd
import numpy as np
import yfinance as yf
import os
from set_up import *

from utils import get_historical_portfolio, get_buying_portfolio, get_profits_per_actor, update_portfolio_values

"""
portfolio table : Ticker.index, Title, Type, Currency, Quantity, amount_euro
cashflows : Date.index, Ticker, Stock, Quantity, Price, Conversion_rate, Price_euro, Total_amount, Charges
cashflows_aggregate : Ticker.index, Quantity, Total_buying_amount_euro, Charges
data : dictionary of price history by ticker
"""

#
# def update_stock_data(tickers, portfolio_series, portfolio_table):
#     data_update = {}
#     for ticker in portfolio_table.index:
#         print(ticker)
#         data_ticker = yf.download(ticker, start='2022-05-17')['Close']
#         data_update[ticker] = pd.DataFrame.from_dict(data_ticker)
#         data_update[ticker] = data_update[ticker].rename(columns={'Close': 'Close'})
#         last_eur_usd = yf.download('EURUSD=X')[['Close']].tail(1)
#         if portfolio_table.loc[ticker, 'Currency'] == '$':
#             data_update[ticker]['price_euro'] = data_update[ticker].Close / last_eur_usd
#             data_update[ticker]['returns'] = price_table.Close.pct_change()
#         elif portfolio_table.loc[ticker, 'Currency'] == '€':
#             data_update[ticker]['price_euro'] = price_table.Close / 1
#             data_update[ticker]['returns'] = price_table.Close.pct_change()
#     print(data_update.keys())
#     portfolio_series = update_portfolio_values(data_update, portfolio_series, portfolio_table)
#     return portfolio_series
