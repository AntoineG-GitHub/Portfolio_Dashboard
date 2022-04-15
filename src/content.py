from dash import Dash, html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import yfinance as yf
import os

import plotly.graph_objects as go

app = Dash(__name__)

os.chdir("../")
print(os.getcwd())

# CONTENT
banner = html.Div(id='banner',
                  className='pretty_container row',
                  children=[
                      html.Div(
                          className='pretty_container',
                          children=[
                              html.Div(
                                  children=[
                                      html.H1('Umbrella Portfolio Dashboard'),
                                  ]
                              ),
                              html.Div(id='date_info_title')
                          ], style={'width': '90%'}
                      ),
                      html.Div(
                          className='pretty_container',
                          children=[
                              html.Div(
                                  children=[
                                      html.H3('Total Holdings '),
                                      html.Div(className="total_holdings", id='total_holdings'),
                                  ]
                              ),

                          ]
                      ),
                      html.Div(
                          className='pretty_container',
                          children=[
                              html.Div(
                                  children=[
                                      html.H3("Today's Change"),
                                      html.Div(className="total_holdings", id='todays_change'),
                                      # html.Div(className="daily_change", id='todays_change_percentage'),
                                  ]
                              ),

                          ]
                      ),
                      html.Div(
                          className='pretty_container three columns',
                          children=[
                              html.Div(
                                  children=[
                                      html.H3("Total Profit :"),
                                      html.Div(className="total_holdings", id='profit')
                                  ]
                              ),

                          ]
                      ),
                      html.Div(
                          className='column',
                          children=[
                              html.Div(id='Antoine_profit',
                                       className='pretty_container'),
                              html.Div(id='Arthur_profit',
                                       className='pretty_container'),
                          ]

                      )
                  ])

main_info_graphs = html.Div(
    className='parent',
    children=[
        html.Div(className="pretty_container twelve columns",
                 children=[
                     dcc.Graph(id="portfolio_graph", style={'width': '99%'})]
                 ),
        html.Div(
            children=[
                html.Div(
                    className="pretty_container",
                    children=[
                        dcc.Graph(id="pie_stocks", style={'display': 'inline-block'})
                    ]
                )

            ]
        )
    ]
)

main_info_table_stock = html.Div(
    className='pretty_container row',
    children=[
        html.Table(id='table_stocks',
                   className='pretty_container', style={'width': '100%'}
                   )
    ])

cash_info_table_stock = html.Div(
    className='pretty_container row',
    children=[
        html.Table(id='cashflows',
                   className='pretty_container'
                   ),
        html.Table(id='actor_deposits',
                   className='pretty_container'
                   )
    ])

# LAYOUT
app.layout = html.Div(id="main_container",
                      style={'display': 'flex', 'flex-direction': 'column'},
                      children=[
                          html.Div(id='update'),
                          dcc.Location(id='url', refresh=False),
                          html.Link(rel='stylesheet', href='input_files/stylesheet.css'),
                          banner,
                          html.Div([
                              dcc.Tabs([
                                  dcc.Tab(label='Main Information', children=[
                                      main_info_graphs,
                                      main_info_table_stock
                                  ]),
                                  dcc.Tab(label='Cashflows Information', children=[
                                      cash_info_table_stock
                                  ]),
                                  dcc.Tab(label='Risk Management', children=[

                                  ]),
                              ])
                          ]),

                      ])
