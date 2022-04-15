from dash import Input, Output, html
import plotly.graph_objects as go
import yfinance as yf
from dash import dcc
from content import app
import pandas as pd
import os
import numpy as np
from datetime import datetime
from flask import send_from_directory
from data import *


@app.server.route('/input_files/<path:path>')
def static_file(path):
    static_folder = os.path.join(os.getcwd(), 'input_files')
    return send_from_directory(static_folder, path)


@app.callback(
    Output("date_info_title", "children"),
    Input("update", "n_clicks")
)
def display_date_and_hour_refesh(n_clicks):
    return 'Last updated on {}'.format(datetime.now().strftime('%A %d %Y, %H:%M:%S'))


@app.callback(
    Output(component_id='total_holdings', component_property='children'),
    Input(component_id='update', component_property='n_clicks')
)
def compute_total_holdings(n_clicks):
    print("total holdings")
    total_holdings = sum(portfolio_table['amount_euro'])
    total_holdings = np.round(total_holdings, 2)
    return str(total_holdings) + "€"


@app.callback(
    Output(component_id='todays_change', component_property='children'),
    Input(component_id='update', component_property='n_clicks')
)
def compute_todays_change(n_clicks):
    print("Today's Change")
    total_change = {}
    max_period = max(portfolio_series.keys())
    last_value_2d = portfolio_series_yesterday[max_period].iloc[-2, :].values
    print(last_value_2d)
    last_value = portfolio_series[max_period].iloc[-1:, :].values
    print(last_value)
    daily_change = np.round((last_value - last_value_2d)[0][0], 3)
    return str(daily_change) + "€"


@app.callback(
    Output(component_id='todays_change_percentage', component_property='children'),
    Input(component_id='update', component_property='n_clicks')
)
def compute_todays_percentage_change(n_clicks):
    print("Today's Change")
    # I thin I have to compare it with the portfolio series with the exchange rate of yesterday
    max_period = max(portfolio_series.keys())
    last_value_2d = portfolio_series_yesterday[max_period].iloc[-1:, :]
    last_value = portfolio_series[max_period].iloc[-1:, :]
    daily_change_percentage = np.round(last_value_2d.pct_change().iloc[-1].values, 3) * 100
    return str(daily_change_percentage) + "%"


@app.callback(
    Output(component_id='profit', component_property='children'),
    Input(component_id='update', component_property='n_clicks')
)
def compute_profits(n_clicks):
    print("Portfolio's Profit")
    initial_deposit = cashflows_aggregate.Total_buying_amount_euro.sum()
    total_holdings = sum(portfolio_table['amount_euro'])
    profit = np.round(total_holdings - initial_deposit, 2) - cashflows.Charges.sum()

    return str(profit) + "€"


@app.callback(
    [Output(component_id='Antoine_profit', component_property='children'),
     Output(component_id='Arthur_profit', component_property='children')],
    Input(component_id='update', component_property='n_clicks')
)
def compute_personal_profit(n_clicks):
    print("Portfolio's Profit")
    portfolio_series_buying = get_buying_portfolio(cashflows, data, today)

    profit_period = {}
    time_periods = np.unique(pd.to_datetime(cashflows.index))
    time_periods = np.append(time_periods, today)

    for start, end in zip(time_periods[:-1], time_periods[1:]):
        start = str(start)[0:10]
        end = str(end)[0:10]
        profit_period[end] = get_profits_per_actor(start, end, portfolio_series_buying, actor_deposits,
                                                   portfolio_series)
    antoine = 0
    arthur = 0
    for key in profit_period.keys():
        for key_2 in profit_period[key]:
            if key_2 == 1:
                antoine += profit_period[key][key_2]
            elif key_2 == 2:
                arthur += profit_period[key][key_2]

    return ["Antoine's Profit : " + str(np.round(antoine, 2)) + "€",
            "Arthur's Profit : " + str(np.round(arthur, 2)) + "€"]


@app.callback(
    Output(component_id='portfolio_graph', component_property='figure'),
    Input(component_id='update', component_property='n_clicks')
)
def portfolio_graph(n_clicks):
    print("update_price")
    price_update = yf.download('SPYD', start='2022-02-25', progress=False).iloc[1:]
    spyd = (price_update['Close'] / price_update['Close'].iloc[0]).to_numpy()

    time_serie = []
    time_serie.append([1])
    tmp = 1
    for keys in portfolio_series.keys():
        normalize = portfolio_series[keys].reset_index()['Portfolio_value'].iloc[0]
        time_serie.append(tmp * portfolio_series[keys].reset_index()['Portfolio_value'].iloc[1:] / normalize)
        tmp = (portfolio_series[keys]['Portfolio_value'].iloc[1:] / normalize).iloc[-1]

    result = []
    for sublist in time_serie:
        for item in sublist:
            result.append(item)

    two = go.Scatter(x=price_update.index, y=spyd, name="S&P500")
    portfolio = go.Scatter(x=price_update.index, y=np.array(result), name="Portfolio")
    fig = go.Figure(
        data=two,
        layout_title_text="Relative evolution of the portfolio compared to the market"
    )
    fig.add_trace(portfolio)
    fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Normalized Value',
        plot_bgcolor='white',
        paper_bgcolor='white',
        yaxis_range=[min(np.concatenate((spyd, np.array(result))))-0.01, max(np.concatenate((spyd, np.array(result))))],
        margin=go.layout.Margin(
            l=5,  # left margin
            r=5,  # right margin
            b=5,  # bottom margin
            t=70,  # top margin
        )
    )
    fig.update_xaxes(showline=False,
                     linewidth=1,
                     linecolor='grey')
    fig.update_yaxes(showline=False,
                     linewidth=1,
                     linecolor='grey',
                     )
    # fig.add_shape(type='line',
    #               x0='2022-02-24',
    #               y0=1,
    #               x1=today,
    #               y1=1,
    #               line=dict(color='black', width=1),
    #               xref='x',
    #               yref='y'
    #               )

    return fig


@app.callback(
    Output(component_id='pie_stocks', component_property='figure'),
    Input(component_id='update', component_property='n_clicks')
)
def compute_pie_stocks(n_clicks):
    print("update_price")
    total_holdings = {}
    for tick in portfolio_table.index:
        price_update = data[tick]['Close'].iloc[-1]
        total_holdings[tick] = price_update * portfolio_table.loc[portfolio_table.index == tick][
            'Quantity'].values.squeeze()

    labels = list(total_holdings.keys())
    values = list(total_holdings.values())
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)],
                    layout_title_text="Pie Chart of the portfolio"
                    )
    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.8
    ))

    return fig


@app.callback(
    Output(component_id='table_stocks', component_property='children'),
    Input(component_id='update', component_property='n_clicks')
)
def update_table_stock(n_clicks):
    data_dic = {}
    ticker_column = []
    price = []
    currency = []
    name = []
    quantity = []
    percentage = []
    total_profit = []
    graph = []
    for ticker in portfolio_table.index:
        ticker_column.append(ticker)
        name.append(portfolio_table.loc[ticker, 'Title'])
        currency.append(portfolio_table.loc[ticker, 'Currency'])
        quantity.append(portfolio_table.loc[ticker, 'Quantity'])
        price.append(data[ticker]['Close'].iloc[-1])
        percentage.append(data[ticker]['Close'].iloc[-2:].pct_change().iloc[-1] * 100)
        price_update = data[ticker]['Close'].iloc[-253:]
        two = [go.Scatter(x=price_update.index, y=price_update.to_numpy())]
        fig = go.Figure(
            data=two
        )
        fig.update_layout(
            autosize=False,
            width=300,
            height=50,
            margin=go.layout.Margin(
                l=0,  # left margin
                r=0,  # right margin
                b=0,  # bottom margin
                t=0,  # top margin
            ),
            showlegend=False,
        )
        # x axis
        fig.update_xaxes(visible=False)
        # y axis
        fig.update_yaxes(visible=False)
        graph.append(dcc.Graph(figure=fig))

    data_dic['Ticker'] = ticker_column
    data_dic['Name'] = name
    data_dic['Type'] = portfolio_table['Type']
    data_dic['Price'] = np.round(price, 2)
    data_dic['Currency'] = currency
    data_dic['Quantity'] = quantity
    data_dic['Daily percentage change'] = np.round(percentage, 2)
    data_dic['Total amount (€)'] = np.round(portfolio_table['amount_euro'], 2)
    data_dic['Graph'] = graph
    df = pd.DataFrame(data_dic)
    value = [html.Tr([html.Th(col) for col in df.columns])] + \
            [html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
             for i in range(min(len(df), 26))]

    return value


@app.callback(
    Output(component_id='cashflows', component_property='children'),
    Input(component_id='update', component_property='n_clicks')
)
def update_table_stock(n_clicks):
    cashflows_table = cashflows.reset_index().copy()
    cashflows_table.Date = cashflows_table.Date.astype(str)[0:10]
    df = pd.DataFrame(cashflows_table)
    value = [html.Tr([html.Th(col) for col in df.columns])] + \
            [html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
             for i in range(min(len(df), 26))]

    return value


@app.callback(
    Output(component_id='actor_deposits', component_property='children'),
    Input(component_id='update', component_property='n_clicks')
)
def update_table_actors(n_clicks):
    actors_table = actor_deposits.copy()
    actors_table.Actor.loc[actors_table.Actor == 1] = "Antoine"
    actors_table.Actor.loc[actors_table.Actor == 2] = "Arthur"
    actors_table.Actor.loc[actors_table.Actor == 0] = "Dividends"
    actors_table.Date = actors_table.Date.astype(str)[0:10]
    df = pd.DataFrame(actors_table)
    value = [html.Tr([html.Th(col) for col in df.columns])] + \
            [html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
             for i in range(min(len(df), 26))]

    return value
