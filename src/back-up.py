## today_real = np.datetime64('today', 'D')
# today = datetime.datetime.today()
# if np.is_busday(datetime.date.today().strftime("%Y-%m-%d")):
#     today_real = today.date()
# else:
#     offset = max(0, (today.weekday() + 6) % 7 - 3)
#     timedelta = datetime.timedelta(offset)
#     today_real = str((today - timedelta).date())
#     today_real = datetime.datetime.strptime(today_real, '%Y-%m-%d').date()
# print('Today:', today_real)
# starting = np.datetime64("2022-02-15")

#all commented above is supposed to be the get_date function

# def get_historical_portfolio(cashflows, data, today, time_period):
#     historical_portfolio = {}
#     time_periods = np.unique(cashflows.index.astype(str))
#     time_periods = np.append(time_periods, today.astype(str))
#     for start, end in zip(time_periods[:-1], time_periods[1:]):  # problems on the dates
#         historical_period_portfolio = []
#         portfolio_date = []
#         cash = cashflows.drop(columns=['Stock', 'Price', 'Conversion_rate', 'Price_euro'])
#         portfolio_period = cash.loc[cashflows.index <= datetime.datetime.strptime(start, '%Y-%m-%d')].reset_index(
#             drop=True)  # retrieve the portfolio of the period
#         portfolio_period = portfolio_period.groupby(['Ticker']).sum().reset_index()
#         portfolio_period = portfolio_period.set_index(
#             'Ticker')  # portfolio of the starting day of the period with the quantity
#         delta_days = pd.bdate_range(start, end)
#         for day in delta_days:
#             day = str(day)[0:10]
#             portfolio_date.append(day)
#             amount_portfolio = 0
#             for ticker in portfolio_period.index:
#                 datetime_day = datetime.datetime.strptime(day, '%Y-%m-%d')
#                 if datetime_day not in data[ticker].index:
#                     if datetime_day - datetime.timedelta(1) not in data[ticker].index:
#                         data[ticker].loc[datetime_day] = data[ticker].loc[datetime_day - datetime.timedelta(3)]
#                     else:
#                         data[ticker].loc[datetime_day] = data[ticker].loc[datetime_day - datetime.timedelta(1)]
#                 data[ticker] = data[ticker].sort_index()
#                 price_end_period = data[ticker].loc[day, time_period]
#                 amount_portfolio += portfolio_period.loc[ticker, 'Quantity'] * price_end_period
#             historical_period_portfolio.append(amount_portfolio)
#         historical_portfolio[end] = pd.DataFrame(historical_period_portfolio, index=portfolio_date,
#                                                  columns=['Portfolio_value'])
#
#     return historical_portfolio

# def get_buying_portfolio(cashflows, data, today):
#     historical_portfolio = {}
#     time_periods = np.unique(cashflows.index.astype(str))
#     time_periods = np.append(time_periods, today.astype(str))
#     historical_portfolio['2022-02-25'] = pd.DataFrame([0])
#     for start, end in zip(time_periods[:-1], time_periods[1:]):
#         historical_period_portfolio = []
#         portfolio_date = []
#         cash = cashflows.drop(columns=['Stock', 'Price', 'Conversion_rate', 'Price_euro'])
#         portfolio_period = cash.loc[cashflows.index <= datetime.datetime.strptime(start, '%Y-%m-%d')].reset_index(
#             drop=True)  # retrieve the portfolio of the period
#         portfolio_period = portfolio_period.groupby(['Ticker']).sum().reset_index()
#         portfolio_period = portfolio_period.set_index(
#             'Ticker')  # portfolio of the starting day of the period with the quantity
#         cash_movements = cashflows.drop(columns=['Stock', 'Price', 'Conversion_rate'])
#         movements = cash_movements.loc[cashflows.index == start].reset_index(
#             drop=True)  # retrieve the movements at the start of the period
#         amounts_movement = sum(movements.Quantity * movements.Price_euro)
#         first_day_amount = historical_portfolio[start].iloc[-1] + amounts_movement
#         portfolio_date.append(start)
#         historical_period_portfolio.append(first_day_amount.to_numpy()[0])
#         # define the first day as the last value of portfolio + movements in cashflows
#         delta_days = pd.bdate_range(str(pd.to_datetime(start) + datetime.timedelta(days=1)), end)
#         for day in delta_days:
#             day = str(day)[0:10]
#             amount_portfolio = 0
#             portfolio_date.append(day)
#             for ticker in portfolio_period.index:
#                 datetime_day = datetime.datetime.strptime(day, '%Y-%m-%d')
#                 if datetime_day not in data[ticker].index:
#                     if datetime_day - datetime.timedelta(1) not in data[ticker].index:
#                         data[ticker].loc[datetime_day] = data[ticker].loc[datetime_day - datetime.timedelta(3)]
#                     else:
#                         data[ticker].loc[datetime_day] = data[ticker].loc[datetime_day - datetime.timedelta(1)]
#                 price_end_period = data[ticker].loc[day, 'price_euro']
#                 amount_portfolio += portfolio_period.loc[ticker, 'Quantity'] * price_end_period
#             historical_period_portfolio.append(amount_portfolio)
#         historical_portfolio[end] = pd.DataFrame(historical_period_portfolio, index=portfolio_date,
#                                                  columns=['Portfolio_value'])
#
#     del historical_portfolio['2022-02-25']
#     return historical_portfolio