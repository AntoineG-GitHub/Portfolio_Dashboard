import os
import pandas as pd
import numpy as np
import pickle
import yfinance as yf
import datetime
from utils import get_historical_portfolio, get_buying_portfolio

print(os.getcwd())
os.chdir(r"d:\Users\Antoine\Documents\Umbrella_Fund\Code_projects\Dashboard")
# os.chdir(r"/home/ubuntu/Dashboard")
portfolio_table = pd.read_excel("Cashflows.xlsx", sheet_name="Portfolio")
portfolio_table.index = portfolio_table.Ticker
portfolio_table = portfolio_table.drop(columns=['Ticker'])
cashflows = pd.read_excel("Cashflows.xlsx", sheet_name="Cashflows")
cashflows.index = cashflows.Date
actor_deposits = pd.read_excel("Cashflows.xlsx", sheet_name="Deposits")
actor_deposits.index = actor_deposits.Date
cashflows_aggregate = cashflows.drop(columns=['Stock', 'Price', 'Conversion_rate', 'Price_euro'])
cashflows_aggregate = cashflows_aggregate.groupby(['Ticker']).sum(['Quantity', 'Total_amount', 'Charges'])
cashflows_aggregate = cashflows_aggregate.rename(columns={'Total_amount': 'Total_buying_amount_euro'})
cashflows_aggregate = cashflows_aggregate.loc[cashflows_aggregate.Quantity != 0]
cashflows_ticker = cashflows[['Ticker', 'Currency', 'Quantity']].groupby(['Ticker', 'Currency']).sum().reset_index()
cashflows_ticker.index = cashflows_ticker.Ticker
cashflows_ticker = cashflows_ticker.drop('Ticker', axis=1)

# today_real = np.datetime64('today', 'D')
today = datetime.datetime.today()
if np.is_busday(datetime.date.today().strftime("%Y-%m-%d")):
    today_real = today.date()
else:
    offset = max(0, (today.weekday() + 6) % 7 - 3)
    timedelta = datetime.timedelta(offset)
    today_real = str((today - timedelta).date())
    today_real = datetime.datetime.strptime(today_real, '%Y-%m-%d').date()
print('Today:', today_real)
starting = np.datetime64("2022-02-15")

tickers = cashflows[['Ticker', 'Type', 'Currency']].reset_index()
tickers = pd.DataFrame(tickers.groupby(['Ticker', 'Type', 'Currency']).size().reset_index())
tickers.index = tickers.Ticker

# data = import_stock_data()
data = {}
for ticker in tickers.index:
    data_ticker = yf.download(ticker)[['Open', 'Close']]
    data[ticker] = pd.DataFrame.from_dict(data_ticker)
    data[ticker] = data[ticker].rename(columns={'Close': 'Close', 'Open': 'Open'})
eur_usd = yf.download('EURUSD=X')[['Open', 'Close']]
pickle.dump(data, open("data.p", "wb"))
pickle.dump(eur_usd, open("eur_usd.p", "wb"))
with open("eur_usd.p", "rb") as p:
    eur_usd = pickle.load(p)
    p.close()

with open("data.p", "rb") as f:
    data = pickle.load(f)
    f.close()

for ticker in data.keys():
    today = data[ticker].tail(1).index
    if today.values != np.datetime64(today_real):
        data[ticker] = pd.concat([data[ticker], pd.DataFrame(data[ticker].tail(1)[['Open', 'Close']].values,
                                                             index=[pd.to_datetime(today_real)],
                                                             columns=['Open', 'Close'])])
last_eur_usd = eur_usd['Close'].iloc[-1]
two_days_eur_usd = eur_usd['Close'].iloc[-2]
today = data[list(data.keys())[0]].tail(1).index

for ticker in data:  # Add a price_euro column in the data
    price_table = data[str(ticker)]
    if cashflows_ticker.loc[ticker, 'Currency'] == '$':
        price_table['price_euro'] = price_table.Close / last_eur_usd
        price_table['price_euro_yesterday'] = price_table.Open / two_days_eur_usd
        price_table['returns'] = price_table.Close.pct_change()
    elif cashflows_ticker.loc[ticker, 'Currency'] == '€':
        price_table['price_euro'] = price_table.Close / 1
        price_table['price_euro_yesterday'] = price_table.Open / 1
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
if str(today_real) not in price_update2.index:
    print("not in:", pd.to_datetime(today_real), price_update2.index.values[-1])
    price_update2.loc[pd.to_datetime(today_real)] = price_update2.tail(1)["Close"]
portfolio_returns = pd.DataFrame(result, index=price_update2.index, columns=['returns']).mul(100)
print(portfolio_returns)
portfolio_returns['day_of_week'] = portfolio_returns.index.to_series().dt.day_name()
portfolio_returns['sign'] = np.where(portfolio_returns['returns'] > 0, 'positive', 'negative')
print(portfolio_returns.tail(5))

# Le dashboard ne prend pas la variation hors horaires boursiers
