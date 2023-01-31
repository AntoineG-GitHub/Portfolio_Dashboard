import numpy as np
from datetime import datetime, timedelta
import datetime
import pandas as pd


def get_historical_portfolio(cashflows, data, today, time_period):
    historical_portfolio = {}
    time_periods = np.unique(cashflows.index.astype(str))
    time_periods = np.append(time_periods, today.strftime("%d/%m/%Y"))

    for start, end in zip(time_periods[:-1], time_periods[1:]):
        portfolio_period = cashflows.loc[cashflows.index <= pd.to_datetime(start)].reset_index(drop=True)
        portfolio_period = portfolio_period.groupby(['Ticker']).sum().reset_index()
        portfolio_period = portfolio_period.set_index('Ticker')
        portfolio_date = pd.bdate_range(start, end)
        historical_period_portfolio = []

        for day in portfolio_date:
            amount_portfolio = 0
            for ticker in portfolio_period.index:
                if day not in data[ticker].index:
                    if day - pd.Timedelta(1, unit='d') not in data[ticker].index:
                        data[ticker].loc[day] = data[ticker].loc[day - pd.Timedelta(3, unit='d')]
                    else:
                        data[ticker].loc[day] = data[ticker].loc[day - pd.Timedelta(1, unit='d')]
                data[ticker] = data[ticker].sort_index()
                price_end_period = data[ticker].loc[day, time_period]
                amount_portfolio += portfolio_period.loc[ticker, 'Quantity'] * price_end_period
            historical_period_portfolio.append(amount_portfolio)

        historical_portfolio[end] = pd.DataFrame(historical_period_portfolio, index=portfolio_date,
                                                 columns=['Portfolio_value'])

    return historical_portfolio

def get_buying_portfolio(cashflows, data, today):
    historical_portfolio = {}
    time_periods = np.unique(cashflows.index.astype(str))
    time_periods = np.append(time_periods, today.strftime("%d/%m/%Y"))
    historical_portfolio['2022-02-25'] = pd.DataFrame([0])

    for start, end in zip(time_periods[:-1], time_periods[1:]):
        portfolio_date = []
        cash = cashflows.drop(columns=['Stock', 'Price', 'Conversion_rate', 'Price_euro'])
        portfolio_period = cash.loc[cashflows.index <= pd.to_datetime(start)].reset_index(drop=True)
        portfolio_period = portfolio_period.groupby(['Ticker']).sum().reset_index()
        portfolio_period = portfolio_period.set_index('Ticker')
        cash_movements = cashflows.drop(columns=['Stock', 'Price', 'Conversion_rate'])
        movements = cash_movements.loc[cashflows.index == start].reset_index(drop=True)
        amounts_movement = sum(movements.Quantity * movements.Price_euro)
        print(start)
        first_day_amount = historical_portfolio[start].iloc[-1] + amounts_movement
        portfolio_date.append(start)
        historical_period_portfolio = [first_day_amount.to_numpy()[0]]
        portfolio_date.extend(pd.bdate_range(start=pd.to_datetime(start) + pd.Timedelta(days=1), end=end))

        for day in portfolio_date[1:]:
            amount_portfolio = 0
            for ticker in portfolio_period.index:
                if day not in data[ticker].index:
                    if day - pd.Timedelta(1, unit='d') not in data[ticker].index:
                        data[ticker].loc[day] = data[ticker].loc[day - pd.Timedelta(3, unit='d')]
                    else:
                        data[ticker].loc[day] = data[ticker].loc[day - pd.Timedelta(1, unit='d')]
                data[ticker] = data[ticker].sort_index()
                price_end_period = data[ticker].loc[day, 'price_euro']
                amount_portfolio += portfolio_period.loc[ticker, 'Quantity'] * price_end_period
            historical_period_portfolio.append(amount_portfolio)

        historical_portfolio[end] = pd.DataFrame(historical_period_portfolio, index=portfolio_date,
                                                 columns=['Portfolio_value'])
    del historical_portfolio['2022-02-25']
    return historical_portfolio


def get_profits_per_actor(start, end, portfolio_series_buying, actor_deposits):
    profit = portfolio_series_buying[end].iloc[-1].values - portfolio_series_buying[end].iloc[0].values
    print("profit from get_profit_per_actor:", profit)

    profits_per_actor = {}
    actors_periods = actor_deposits.loc[pd.to_datetime(actor_deposits.Date) <= pd.to_datetime(start)]
    actors = np.unique(actors_periods.Actor.tolist())
    percentages = {}
    total = actors_periods.CashFlow.sum()
    for numbers in actors:
        percentages[numbers] = actors_periods.loc[actors_periods.Actor == numbers].CashFlow.sum() / total
        profits_per_actor[numbers] = (percentages[numbers] * profit)[0]

    print("Amount-start:", portfolio_series_buying[end].iloc[0])
    print("Amount_end", portfolio_series_buying[end].iloc[-1])
    print("Period profit:", profit)
    print("Profit per actors:", profits_per_actor)
    return profits_per_actor


def update_portfolio_values(data_update, portfolio_series, portfolio_table):
    amount_portfolio = 0
    for ticker in portfolio_table.index:
        datetime_day = datetime.datetime.strptime(str(np.datetime64('today', 'D')), '%Y-%m-%d')
        if datetime_day not in data_update[ticker].index:
            if datetime_day - datetime.timedelta(1) not in data_update[ticker].index:
                data_update[ticker].loc[datetime_day] = data_update[ticker].loc[datetime_day - datetime.timedelta(3)]
            else:
                data_update[ticker].loc[datetime_day] = data_update[ticker].loc[datetime_day - datetime.timedelta(1)]
        price_end_period = data_update[ticker].loc[str(datetime_day), 'price_euro']
        amount_portfolio += portfolio_table.loc[ticker, 'Quantity'] * price_end_period
    portfolio_series.loc[np.datetime64('today', 'D'), 'Portfolio_value'] = amount_portfolio
    return portfolio_series


def process_cashflows(filename: str) -> tuple:
    portfolio_table = pd.read_excel(filename, sheet_name="Portfolio")
    portfolio_table.set_index("Ticker", inplace=True)
    cashflows = pd.read_excel(filename, sheet_name="Cashflows")
    cashflows["Date"] = pd.to_datetime(cashflows["Date"])
    cashflows.set_index("Date", inplace=True)
    actor_deposits = pd.read_excel(filename, sheet_name="Deposits")
    actor_deposits.set_index("Date", inplace=True)

    cashflows_aggregate = (
        cashflows.drop(columns=["Stock", "Price", "Conversion_rate", "Price_euro"])
            .groupby("Ticker")
            .sum(["Quantity", "Total_amount", "Charges"])
            .rename(columns={"Total_amount": "Total_buying_amount_euro"})
            .loc[lambda df: df.Quantity != 0]
    )
    cashflows_ticker = (
        cashflows[["Ticker", "Currency", "Quantity"]]
            .groupby(["Ticker", "Currency"])
            .sum()
            .reset_index()
            .set_index("Ticker")
        # .drop("Ticker", axis=1)
    )
    tickers = cashflows[['Ticker', 'Type', 'Currency']].reset_index()
    tickers = pd.DataFrame(tickers.groupby(['Ticker', 'Type', 'Currency']).size().reset_index())
    tickers.index = tickers.Ticker

    return portfolio_table, cashflows, actor_deposits, cashflows_aggregate, cashflows_ticker, tickers


def get_date():
    today = datetime.date.today()

    if not np.is_busday(today):
        offset = max(0, (today.weekday() + 6) % 7 - 3)
        today -= timedelta(offset)

    print('Today:', today)
    starting = np.datetime64("2022-02-15")
    return starting, today
