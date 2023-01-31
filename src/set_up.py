import os
import pandas as pd
import numpy as np
import pickle
import yfinance as yf
from utils import get_historical_portfolio, get_buying_portfolio, process_cashflows, get_date

os.chdir(r"d:\Users\Antoine\Documents\Umbrella_Fund\Code_projects\Dashboard")

portfolio_table, cashflows, actor_deposits, cashflows_aggregate, cashflows_ticker, tickers = process_cashflows("Cashflows.xlsx")
print("portfolio_table \n", portfolio_table.head(3))
print("cashflows \n", cashflows.head(3))
print("actor_deposits \n", actor_deposits.head(3))
print("cashflows_aggregate \n", cashflows_aggregate.head(3))
print("cashflows_ticker \n", cashflows_ticker.head(3))
starting, today = get_date()

# # data = import_stock_data()
data = {}  # dictionary of tickers and table with history of price
for ticker in tickers.index:
    data_ticker = yf.download(ticker)[['Open', 'Close']]
    data[ticker] = pd.DataFrame.from_dict(data_ticker)
    data[ticker] = data[ticker].rename(columns={'Close': 'Close', 'Open': 'Open'})
eur_usd = yf.download('EURUSD=X')[['Open', 'Close']]

# for ticker in data.keys():
#     today = data[ticker].tail(1).index
#     if today.values != np.datetime64(today_real):
#         data[ticker] = pd.concat([data[ticker], pd.DataFrame(data[ticker].tail(1)[['Open', 'Close']].values,
#                                                              index=[pd.to_datetime(today_real)],
#                                                              columns=['Open', 'Close'])])
# last_eur_usd = eur_usd['Close'].iloc[-1]
# two_days_eur_usd = eur_usd['Close'].iloc[-2]
# today = data[list(data.keys())[0]].tail(1).index
#
# for ticker in data:  # Add a price_euro column in the data
#     price_table = data[str(ticker)]
#     if cashflows_ticker.loc[ticker, 'Currency'] == '$':
#         price_table['price_euro'] = price_table.Close / last_eur_usd
#         price_table['price_euro_yesterday'] = price_table.Open / two_days_eur_usd
#         price_table['returns'] = price_table.Close.pct_change()
#     elif cashflows_ticker.loc[ticker, 'Currency'] == '€':
#         price_table['price_euro'] = price_table.Close / 1
#         price_table['price_euro_yesterday'] = price_table.Open / 1
#         price_table['returns'] = price_table.Close.pct_change()

# If we are not on a business day, I add a row for each ticker's dataframe with the price of the last business day
for ticker in data.keys():
    last_date = data[ticker].tail(1).index
    if last_date.values != np.datetime64(today):
        data[ticker] = pd.concat([data[ticker],
                                 pd.DataFrame(data[ticker].tail(1)[['Open', 'Close']].values,
                                 index=[pd.to_datetime(today)],
                                 columns=['Open', 'Close'])])

# Get the last and second to last EUR/USD exchange rate
last_eur_usd = eur_usd['Close'].iloc[-1]
two_days_eur_usd = eur_usd['Close'].iloc[-2]

# Add a price_euro column in the data
for ticker in data:
    price_table = data[ticker]
    if cashflows_ticker.loc[ticker, 'Currency'] == '$':
        price_table['price_euro'] = price_table.Close / last_eur_usd
        price_table['price_euro_yesterday'] = price_table.Open / two_days_eur_usd
        price_table['returns'] = price_table.Close.pct_change()
    elif cashflows_ticker.loc[ticker, 'Currency'] == '€':
        price_table['price_euro'] = price_table.Close
        price_table['price_euro_yesterday'] = price_table.Open
        price_table['returns'] = price_table.Close.pct_change()


total_amount_euro = []
for ticker in portfolio_table.index:
    total_amount_euro.append(portfolio_table.loc[ticker, 'Quantity'] * data[ticker].tail(1)['price_euro'].iloc[0])
portfolio_table['amount_euro'] = total_amount_euro


portfolio_series = get_historical_portfolio(cashflows, data, today, 'price_euro')
portfolio_series_yesterday = get_historical_portfolio(cashflows, data, today, 'price_euro_yesterday')
portfolio_series_buying = get_buying_portfolio(cashflows, data, today)

profit_period = {}
time_periods = np.unique(pd.to_datetime(cashflows.index))
time_periods = np.append(time_periods, today)

time_serie = []
time_serie.append([0])
for keys in portfolio_series.keys():
    returns = portfolio_series[keys].reset_index()[
        'Portfolio_value'].pct_change()
    time_serie.append(returns)
result = []
for sublist in time_serie:
    for item in sublist:
        result.append(item)
result = [x for x in result if str(x) != 'nan']
print(result)
price_update2 = data["SPYD.DE"].loc['2022-02-25':]
if str(today) not in price_update2.index:
    print("not in:", pd.to_datetime(today), price_update2.index.values[-1])
    price_update2.loc[pd.to_datetime(today)] = price_update2.tail(1)["Close"]
portfolio_returns = pd.DataFrame(result, index=price_update2.index, columns=['returns']).mul(100)
print(portfolio_returns)
portfolio_returns['day_of_week'] = portfolio_returns.index.to_series().dt.day_name()
portfolio_returns['sign'] = np.where(portfolio_returns['returns'] > 0, 'positive', 'negative')
print(portfolio_returns.tail(5))

# Le dashboard ne prend pas la variation hors horaires boursiers et donc le return une fois 17h30 passé est completement différent vu qu'il oublie ce qui close à 17h30
