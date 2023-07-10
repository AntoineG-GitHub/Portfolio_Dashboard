from datetime import datetime
from dash import Input, Output, html
import plotly.graph_objects as go
from dash import dcc
import plotly.express as px
from flask import send_from_directory
from utils.set_up import *
import plotly.figure_factory as ff
from utils.utils import get_profits_per_actor
from pages.layout import app


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
def compute_total_holdings(n):
    total_holdings = sum(portfolio_table['amount_euro'])
    total_holdings = np.round(total_holdings, 2)
    return str(total_holdings) + "€"

@app.callback(
    Output(component_id='todays_change', component_property='children'),
    Input(component_id='update', component_property='n_clicks')
)
def compute_todays_change(n_clicks):
    max_period = max(portfolio_series.keys())
    last_value_2d = portfolio_series[max_period].iloc[-2, :].values[0]
    last_value = portfolio_series[max_period].iloc[-1, :].values[0]
    daily_change = np.round((last_value - last_value_2d), 3)
    return str(daily_change) + "€"


@app.callback(
    Output(component_id='profit', component_property='children'),
    Input(component_id='update', component_property='n_clicks')
)
def compute_profits(n_clicks):
    total_profit = 0
    for ticker in cashflows_ticker.index:  # for all ticker traded
        total_buying_amount_ticker = cashflows.loc[cashflows.Ticker == ticker].Total_amount.sum()  # Get the total amount of buying price-selling price to compute the margin on that ticker stock
        # TODO: Use this data to create new table to inform about prodit by stock
        if ticker in portfolio_table.index:
            present_value_ticker = portfolio_table.loc[ticker, 'amount_euro'].sum()
        else:
            present_value_ticker = 0
        profit_ticker = present_value_ticker - total_buying_amount_ticker - cashflows.loc[
            cashflows.Ticker == ticker].Charges.sum()  # Profit is the total price difference minus charges
        total_profit += profit_ticker
    total_profit = np.round(total_profit + actor_deposits.loc[actor_deposits.Actor == 0].CashFlow.sum(), 2)

    return str(total_profit) + "€"


@app.callback(
    [Output(component_id='Antoine_profit', component_property='children'),
     Output(component_id='Arthur_profit', component_property='children'),
     Output(component_id='Dividend_profit', component_property='children')],
    Input(component_id='update', component_property='n_clicks')
)
def compute_personal_profit(n_clicks):
    print("compute personnal profits")
    portfolio_series_buying = get_buying_portfolio(cashflows, data, today)
    profit_period = {}
    costs_per_actor = {}
    time_periods = np.unique(cashflows.index.astype(str))
    time_periods = np.append(time_periods, today.strftime("%Y-%m-%d"))
    for start, end in zip(time_periods[:-1], time_periods[1:]):  # TODO: Do I have to substract the costs ?
        print(start, end)
        actor = {}
        start = str(start)[0:10]
        end = str(end)[0:10]
        costs_period = cashflows.Charges.loc[cashflows.index == start].sum()             
        actors_periods = actor_deposits.loc[pd.to_datetime(actor_deposits.index) <= pd.to_datetime(start)]        
        actors = np.unique(actors_periods.Actor.tolist())
        percentages = {}
        total = actors_periods.CashFlow.sum()
        actors = actors[actors != 0]
        for numbers in actors:
            percentages[numbers] = actors_periods.loc[actors_periods.Actor == numbers].CashFlow.sum() / total
            actor[numbers] = (percentages[numbers] * costs_period)
            print(actor)
        costs_per_actor[start] = actor
        profit_period[end] = get_profits_per_actor(start, end, portfolio_series_buying, actor_deposits)
    costs_per_actor[str(time_periods[-1])[0:10]] = {1: 0, 2: 0}
    antoine = 0
    arthur = 0
    for period in profit_period.keys():
        for actor in profit_period[period]:
            if actor == 1:
                antoine += profit_period[period][actor] - costs_per_actor[period][actor]
            elif actor == 2:
                arthur += profit_period[period][actor] - costs_per_actor[period][actor]
    antoine = antoine - costs_per_actor['2022-02-25'][1]
    arthur = arthur - costs_per_actor['2022-02-25'][2]
    return ["Antoine's Profit : " + str(np.round(antoine, 2)) + "€",
            "Arthur's Profit : " + str(np.round(arthur, 2)) + "€",
            "Dividend's Profit : " + str(np.round(actor_deposits.loc[actor_deposits.Actor == 0].CashFlow.sum(), 2)) + "€"]


@app.callback(
    Output(component_id='portfolio_graph', component_property='figure'),
    Input(component_id='update', component_property='n_clicks')
)
def portfolio_graph(n_clicks):
    price_update = yf.download('SPYD', start='2022-02-26', progress=False)['Close']
    if pd.to_datetime(today) not in pd.to_datetime(price_update.index):
        price_update.loc[str(today)] = price_update.tail(1).values[0]
    price_update = pd.DataFrame(price_update, columns=['Close'], index=price_update.index)
    spyd = np.exp(np.log1p(price_update['Close'].pct_change()).cumsum())
    spyd = np.append([1], spyd)
    spyd = spyd[~np.isnan(spyd)]

    result = portfolio_returns.returns.divide(100).values
    result = np.exp(np.log1p(result).cumsum())
    two = go.Scatter(x=price_update.index, y=spyd, name="S&P500")
    portfolio = go.Scatter(x=portfolio_returns.index, y=np.array(result), name="Portfolio")
    fig = go.Figure(
        data=two,
        layout_title_text="Relative evolution of the portfolio compared to the market"
    )
    fig.add_trace(portfolio)
    fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Cumulative returns',
        plot_bgcolor='white',
        paper_bgcolor='white',
        yaxis_range=[min(np.concatenate((spyd, np.array(result)))) - 0.01,
                     max(np.concatenate((spyd, np.array(result))))],
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

    return fig


@app.callback(
    Output(component_id='pie_stocks', component_property='figure'),
    Input(component_id='update', component_property='n_clicks')
)
def compute_pie_stocks(n_clicks):
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
    fig.update_layout(
        width=510,
        height=445,
        autosize=True,
        legend=dict(
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
#ajoute les données de cashflows dans le html
def update_table_stock(n_clicks):   
    cashflows_table = cashflows.reset_index(drop=False).copy()    
    cashflows_table= cashflows_table.astype(str) 
    df = pd.DataFrame(cashflows_table)
    value = [html.Tr([html.Th(col) for col in df.columns])] + \
            [html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
             for i in range(min(len(df), 26))]

    return value


@app.callback(
    Output(component_id='actor_deposits', component_property='children'),
    Input(component_id='update', component_property='n_clicks')
)
#aucune idée de pq il affiche pas la date
def update_table_actors(n_clicks):
    actors_table = actor_deposits.copy()
    actors_table.Actor.loc[actors_table.Actor == 1] = "Antoine"
    actors_table.Actor.loc[actors_table.Actor == 2] = "Arthur"
    actors_table.Actor.loc[actors_table.Actor == 0] = "Dividends"
    actors_table= actors_table.astype(str)
    df = pd.DataFrame(actors_table)
    value = [html.Tr([html.Th(col) for col in df.columns])] + \
            [html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
             for i in range(min(len(df), 26))]
   

    return value


@app.callback(
    Output(component_id='histogram', component_property='figure'),
    Input(component_id='update', component_property='n_clicks')
)
def compute_histogram(n_clicks):
    total_holdings = np.zeros(250)
    total_holdings = np.reshape(total_holdings, (-1, 1))
    for tick in portfolio_table.index:
        price_update = data[tick]['returns'].iloc[-250:]
        weighted_returns = price_update * portfolio_table.loc[portfolio_table.index == tick][
            'Quantity'].values.squeeze()
        weighted_returns = np.reshape(np.array(weighted_returns), (-1, 1))
        total_holdings = np.hstack([weighted_returns, total_holdings])
    total_holdings = pd.DataFrame(total_holdings).iloc[:, 1:]
    portfolio_returns = total_holdings.sum(axis=1)
    portfolio_returns.columns = ['returns']

    group_labels = ['Normal Distribution']
    fig2 = ff.create_distplot([portfolio_returns.values.tolist()], group_labels, curve_type='normal')
    normal_x = fig2.data[1]['x']
    normal_y = fig2.data[1]['y']

    normal = go.Scatter(x=normal_x, y=normal_y, mode='lines', line=dict(color='black', width=2),
                        name='normal')

    two = px.histogram(portfolio_returns, histnorm='probability density',
                       color_discrete_sequence=['indianred'], marginal="rug")
    fig = go.Figure(
        data=two,
        layout_title_text="Histogram of portfolio's returns"
    )
    fig.update_layout(
        autosize=False,
        width=550,
        height=550,
        xaxis_title='Returns',
        yaxis_title='',
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False,
        margin=go.layout.Margin(
            l=5,  # left margin
            r=5,  # right margin
            b=5,  # bottom margin
            t=70,  # top margin
        )
    )
    fig.add_traces([normal])
    fig.update_xaxes(showline=False,
                     linewidth=1,
                     linecolor='grey')
    fig.update_yaxes(showline=False,
                     linewidth=1,
                     linecolor='grey',
                     )

    return fig


@app.callback(
    Output(component_id='table_var', component_property='children'),
    Input(component_id='update', component_property='n_clicks')
)
def compute_risk_table(n_clicks):
    spyd_2 = yf.download('SPYD', start='2022-02-25', progress=False)['Close'].pct_change().iloc[1:]
    total_holdings = np.zeros(250)
    total_holdings = np.reshape(total_holdings, (-1, 1))
    historical_portfolio = np.zeros(250)
    for tick in portfolio_table.index:
        price_update = data[tick]['Close'].iloc[-250:]
        returns_update = data[tick]['returns'].iloc[-250:]
        ticker_amount = price_update * portfolio_table.loc[portfolio_table.index == tick][
            'Quantity'].values.squeeze()
        historical_portfolio += ticker_amount
    portfolio_returns = pd.DataFrame(historical_portfolio).pct_change()
    portfolio_returns = portfolio_returns.iloc[5:]
    # total_holdings = pd.DataFrame(total_holdings).iloc[:, 1:]
    # portfolio_returns = total_holdings.sum(axis=1)
    portfolio_returns.columns = ['returns']

    data_dic = {}
    data_dic['Mean'] = ['Mean', np.round(np.mean(portfolio_returns)[0] * 100, 1), np.round(np.mean(spyd_2) * 100, 1)]
    data_dic['Mediane'] = ['Mediane', np.round(np.median(portfolio_returns) * 100, 1),
                           np.round(np.median(spyd_2) * 100, 1)]
    data_dic['Standard Deviation'] = ['Volatility', np.round(np.std(portfolio_returns)[0] * 100, 1),
                                      np.round(np.std(spyd_2) * 100, 1)]
    data_dic['VAR_95'] = ['Historical daily Value at Risk 95%', np.round(np.percentile(portfolio_returns, 95) * 100, 1),
                          np.round(np.percentile(spyd_2, 95) * 100, 1)]
    data_dic['VAR_99'] = ['Historical daily Value at Risk 99%', np.round(np.percentile(portfolio_returns, 99) * 100, 1),
                          np.round(np.percentile(spyd_2, 99) * 100, 1)]

    df = pd.DataFrame(data_dic).transpose()
    df.columns = ["Metrics", "Portfolio", "S&P500"]
    value = [html.Tr([html.Th(col) for col in df.columns])] + \
            [html.Tr([html.Td(str(df.iloc[i][col])) for col in df.columns])
             for i in range(min(len(df), 26))]

    return value


@app.callback(
    Output(component_id='heatmap', component_property='figure'),
    Input(component_id='update', component_property='n_clicks')
)
def display_heatmap(n_clicks):
    portfolio_returns_heatmap = portfolio_returns.iloc[-30:, :]
    days = portfolio_returns_heatmap['day_of_week'].iloc[0:5].tolist()
    trigger = portfolio_returns_heatmap['day_of_week'].iloc[0]
    start_of_week = portfolio_returns_heatmap.loc[portfolio_returns_heatmap['day_of_week'] == trigger].index.tolist()
    portfolio_returns_heatmap_returns = np.array(portfolio_returns_heatmap['returns'])
    portfolio_returns_heatmap_returns = np.reshape(portfolio_returns_heatmap_returns, (6, 5))

    fig = px.imshow(portfolio_returns_heatmap_returns, color_continuous_midpoint=0,
                    labels=dict(x="Day of Week", y="Start of the week"),
                    x=days,
                    y=start_of_week, text_auto=True, color_continuous_scale=['red', 'green']
                    )
    fig.update_xaxes(side="top")

    return fig


@app.callback(
    Output(component_id='returns_time_series', component_property='figure'),
    Input(component_id='update', component_property='n_clicks')
)
def display_heatmap(n_clicks):
    #portfolio_returns_heatmap = portfolio_returns
    # portfolio_returns_heatmap_returns_np = np.array(portfolio_returns_heatmap['returns'])

    spyd_2 = yf.download('SPYD', start='2022-02-25', progress=False)['Close'].pct_change().iloc[1:]
    total_holdings = np.zeros(250)
    total_holdings = np.reshape(total_holdings, (-1, 1))
    historical_portfolio = np.zeros(250)
    for tick in portfolio_table.index:
        index = data[tick].iloc[-250:].index
        price_update = data[tick]['Close'].iloc[-250:]
        returns_update = data[tick]['returns'].iloc[-250:]
        ticker_amount = price_update * portfolio_table.loc[portfolio_table.index == tick][
            'Quantity'].values.squeeze()
        historical_portfolio += ticker_amount
    portfolio_returns = pd.DataFrame(historical_portfolio).pct_change()
    portfolio_returns = portfolio_returns.iloc[5:]

    pd_risk = pd.DataFrame(historical_portfolio, index=index).pct_change().iloc[15:, :].mul(100)
    risk = pd_risk.loc[pd_risk['Close'] < np.round(np.percentile(pd_risk['Close'], 5))]

    portfolio = go.Scatter(x=pd_risk.index, y=np.array(pd_risk['Close']), name="Portfolio")
    fig = go.Figure(
        data=portfolio,
        layout_title_text="Evolution of the returns over the last 250 days"
    )
    fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Returns (%)',
        plot_bgcolor='white',
        paper_bgcolor='white',
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
    # normal = go.Scatter(x=portfolio_returns_heatmap.index, y=np.zeros(len(portfolio_returns_heatmap)), mode='lines', line=dict(color='red', width=2),
    #                     name='zero', opacity=0.1)
    fig.add_trace(go.Scatter(x=risk.index, y=risk['Close'], mode='markers', name="VaR 95 Exceedance"))
    return fig
