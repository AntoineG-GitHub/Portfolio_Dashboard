import numpy as np
import pandas as pd
import datetime


def get_historical_portfolio(cashflows, data, today, time_period):
    historical_portfolio = {}
    time_periods = np.unique(cashflows.Date.astype(str))
    time_periods = np.append(time_periods, today.astype(str))
    for start, end in zip(time_periods[:-1], time_periods[1:]): # problems on the dates
        historical_period_portfolio = []
        portfolio_date = []
        cash = cashflows.drop(columns=['Stock', 'Price', 'Conversion_rate', 'Price_euro'])
        portfolio_period = cash.loc[cashflows.index <= datetime.datetime.strptime(start, '%Y-%m-%d')].reset_index(drop=True)  # retrieve the portfolio of the period
        portfolio_period = portfolio_period.groupby(['Ticker']).sum().reset_index()
        portfolio_period = portfolio_period.set_index('Ticker')  # portfolio of the starting day of the period with the quantity
        delta_days = pd.bdate_range(start, end)
        for day in delta_days:
            day = str(day)[0:10]
            portfolio_date.append(day)
            amount_portfolio = 0
            for ticker in portfolio_period.index:
                datetime_day = datetime.datetime.strptime(day, '%Y-%m-%d')
                if datetime_day not in data[ticker].index:
                    if datetime_day-datetime.timedelta(1) not in data[ticker].index:
                        data[ticker].loc[datetime_day] = data[ticker].loc[datetime_day - datetime.timedelta(3)]
                    else:
                        data[ticker].loc[datetime_day] = data[ticker].loc[datetime_day-datetime.timedelta(1)]
                data[ticker] = data[ticker].sort_index()
                price_end_period = data[ticker].loc[day, time_period]
                amount_portfolio += portfolio_period.loc[ticker, 'Quantity'] * price_end_period
            historical_period_portfolio.append(amount_portfolio)
        historical_portfolio[end] = pd.DataFrame(historical_period_portfolio, index=portfolio_date, columns=['Portfolio_value'])


    return historical_portfolio


def get_buying_portfolio(cashflows, data, today):
    historical_portfolio = {}
    time_periods = np.unique(cashflows.Date.astype(str))
    time_periods = np.append(time_periods, today.astype(str))
    historical_portfolio['2022-02-25'] = pd.DataFrame([0])
    for start, end in zip(time_periods[:-1], time_periods[1:]):
        historical_period_portfolio = []
        portfolio_date = []
        cash = cashflows.drop(columns=['Stock', 'Price', 'Conversion_rate', 'Price_euro'])
        portfolio_period = cash.loc[cashflows.index <= datetime.datetime.strptime(start, '%Y-%m-%d')].reset_index(
            drop=True)  # retrieve the portfolio of the period
        portfolio_period = portfolio_period.groupby(['Ticker']).sum().reset_index()
        portfolio_period = portfolio_period.set_index('Ticker')  # portfolio of the starting day of the period with the quantity
        cash_movements = cashflows.drop(columns=['Stock', 'Price', 'Conversion_rate'])
        movements = cash_movements.loc[cashflows.index == start].reset_index(drop=True)  # retrieve the movements at the start of the period
        amounts_movement = sum(movements.Quantity * movements.Price_euro)
        first_day_amount = historical_portfolio[start].iloc[-1] + amounts_movement
        portfolio_date.append(start)
        historical_period_portfolio.append(first_day_amount.to_numpy()[0])
        # define the first day as the last value of portfolio + movements in cashflows
        delta_days = pd.bdate_range(str(pd.to_datetime(start) + datetime.timedelta(days=1)), end)
        for day in delta_days:
            day = str(day)[0:10]
            amount_portfolio = 0
            portfolio_date.append(day)
            for ticker in portfolio_period.index:
                datetime_day = datetime.datetime.strptime(day, '%Y-%m-%d')
                if datetime_day not in data[ticker].index:
                    if datetime_day-datetime.timedelta(1) not in data[ticker].index:
                        data[ticker].loc[datetime_day] = data[ticker].loc[datetime_day - datetime.timedelta(3)]
                    else:
                        data[ticker].loc[datetime_day] = data[ticker].loc[datetime_day-datetime.timedelta(1)]
                price_end_period = data[ticker].loc[day, 'price_euro']
                amount_portfolio += portfolio_period.loc[ticker, 'Quantity'] * price_end_period
            historical_period_portfolio.append(amount_portfolio)
        historical_portfolio[end] = pd.DataFrame(historical_period_portfolio, index=portfolio_date, columns=['Portfolio_value'])

    del historical_portfolio['2022-02-25']
    return historical_portfolio


def get_profits_per_actor(start, end, portfolio_series_buying, actor_deposits):
    profit = portfolio_series_buying[end].iloc[-1].values-portfolio_series_buying[end].iloc[0].values

    profits_per_actor = {}
    actors_periods = actor_deposits.loc[pd.to_datetime(actor_deposits.Date) <= pd.to_datetime(start)]
    actors = np.unique(actors_periods.Actor.tolist())
    percentages = {}
    total = actors_periods.CashFlow.sum()
    for numbers in actors:
        percentages[numbers] = actors_periods.loc[actors_periods.Actor == numbers].CashFlow.sum()/total
        profits_per_actor[numbers] = (percentages[numbers]*profit)[0]

    # print("Amount-start:", portfolio_series_buying[end].iloc[0])
    # print("Amount_end", portfolio_series_buying[end].iloc[-1])
    # print("Period profit:", profit)
    # print("Profit per actors:", profits_per_actor)
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
