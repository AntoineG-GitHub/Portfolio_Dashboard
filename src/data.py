from eod import EodHistoricalData
import pickle
import pandas as pd
import numpy as np
import yfinance as yf

from utils import get_historical_portfolio, get_buying_portfolio, get_profits_per_actor

"""
portfolio table : Ticker.index, Title, Type, Currency, Quantity, amount_euro
cashflows : Date.index, Ticker, Stock, Quantity, Price, Conversion_rate, Price_euro, Total_amount, Charges
cashflows_aggregate : Ticker.index, Quantity, Total_buying_amount_euro, Charges
data : dictionary of price history by ticker
"""

key = '6238f2fd825054.08947800'

call = EodHistoricalData(key)

portfolio_table = pd.read_excel("Cashflows.xlsx", sheet_name="Portfolio")
portfolio_table.index = portfolio_table.Ticker
portfolio_table = portfolio_table.drop(columns=['Ticker'])
cashflows = pd.read_excel("Cashflows.xlsx", sheet_name="Cashflows")
cashflows.index = cashflows.Date
cashflows = cashflows.drop(columns=['Date'])
actor_deposits = pd.read_excel("Cashflows.xlsx", sheet_name="Deposits")
actor_deposits.index = actor_deposits.Date
cashflows_aggregate = cashflows.drop(columns=['Stock', 'Price', 'Conversion_rate', 'Price_euro'])
cashflows_aggregate = cashflows_aggregate.groupby(['Ticker']).sum(['Quantity', 'Total_amount', 'Charges'])
cashflows_aggregate = cashflows_aggregate.rename(columns={'Total_amount': 'Total_buying_amount_euro'})
cashflows_aggregate = cashflows_aggregate.loc[cashflows_aggregate.Quantity != 0]

today = np.datetime64('today', 'D')
starting = np.datetime64("2022-02-15")

tickers = cashflows[['Ticker', 'Type', 'Currency']].reset_index()
tickers = pd.DataFrame(tickers.groupby(['Ticker', 'Type', 'Currency']).size().reset_index())
tickers.index = tickers.Ticker
###############################################
# data = {}
# for ticker in tickers.index:
#     print(ticker)
#     if tickers.loc[ticker]['Type'] == 'ETF':
#         data_ticker = call.get_prices_eod(ticker)
#         data_ticker = pd.DataFrame(data_ticker)
#         data_ticker.set_index('date', inplace=True)
#         data_ticker = data_ticker['close']
#         data[ticker] = pd.DataFrame.from_dict(data_ticker)
#         data[ticker] = data[ticker].rename(columns={'close': 'Close'})
#         print(data_ticker)
#     else:
#         data_ticker = yf.download(ticker)['Close']
#         data[ticker] = pd.DataFrame.from_dict(data_ticker)
#         data[ticker] = data[ticker].rename(columns={'Close': 'Close'})
# eur_usd = yf.download('EURUSD=X')
# pickle.dump(data, open("data.p", "wb"))
# pickle.dump(eur_usd, open("eur_usd.p", "wb"))
################################################
with open("eur_usd.p", "rb") as p:
    eur_usd = pickle.load(p)
    p.close()

with open("data.p", "rb") as f:
    data = pickle.load(f)
    f.close()

last_eur_usd = eur_usd.tail(1)['Close'].iloc[0]
total_amount_euro = []
for ticker in data:  # Add a price_euro column in the data
    price_table = data[str(ticker)]
    if portfolio_table.loc[ticker, 'Currency'] == '$':
        price_table['price_euro'] = price_table.Close / last_eur_usd
        total_amount_euro.append(portfolio_table.loc[ticker, 'Quantity'] * \
                                 data[ticker].tail(1)['price_euro'].iloc[0])
    elif portfolio_table.loc[ticker, 'Currency'] == '€':
        price_table['price_euro'] = price_table.Close / 1
        total_amount_euro.append(portfolio_table.loc[ticker, 'Quantity'] * \
                                 data[ticker].tail(1)['price_euro'].iloc[0])
portfolio_table['amount_euro'] = total_amount_euro

two_days_eur_usd = eur_usd.tail(2)['Close'].iloc[0]
total_amount_euro = []
for ticker in data:
    price_table = data[str(ticker)]
    if portfolio_table.loc[ticker, 'Currency'] == '$':
        price_table['price_euro_yesterday'] = price_table.Close / two_days_eur_usd
    elif portfolio_table.loc[ticker, 'Currency'] == '€':
        price_table['price_euro_yesterday'] = price_table.Close / 1




print("Portfolio_table", "\n", portfolio_table.head())
print("Cashflows:", "\n", cashflows)
print("Cashflow aggregate :", "\n", cashflows_aggregate)
print("Actor Deposits:", "\n", actor_deposits)
print("data:", data.keys())

portfolio_series = get_historical_portfolio(cashflows, data, today, 'price_euro')
portfolio_series_yesterday = get_historical_portfolio(cashflows, data, today, 'price_euro_yesterday')
portfolio_series_buying = get_buying_portfolio(cashflows, data, today)

profit_period = {}
time_periods = np.unique(pd.to_datetime(cashflows.index))
time_periods = np.append(time_periods, today)

for start, end in zip(time_periods[:-1], time_periods[1:]):
    start = str(start)[0:10]
    end = str(end)[0:10]
    profit_period[end] = get_profits_per_actor(start, end, portfolio_series_buying, actor_deposits, portfolio_series)

print("Profit_period:", "\n", profit_period)
