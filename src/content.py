from dash import Dash, html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import yfinance as yf
import os

import plotly.graph_objects as go

app = Dash(__name__)
application = app.server
app.title = 'Umbrella on AWS'

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
    style={'width': '100%', 'float': 'left'},
    children=[
        html.Div(style={'width': '64%', 'float': 'left', 'border-radius': '5px',
                        'margin': '10px', 'padding': '15px', 'position': 'relative',
                        'box-shadow': '2px 2px 2px lightgrey', 'background-color': 'rgb(255,255,255)'},
                 children=[
                     dcc.Graph(id="portfolio_graph")]
                 ),
        html.Div(style={'width': '30%', 'float': 'left', 'border-radius': '5px',
                        'margin': '10px', 'padding': '15px', 'position': 'relative',
                        'box-shadow': '2px 2px 2px lightgrey', 'background-color': 'rgb(255,255,255)'},
                 children=[
                     html.Div(
                         style={'display': 'inline-block'},
                         children=[
                             dcc.Graph(id="pie_stocks")
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

heatmap = html.Div(
    className='pretty_container row',
    children=[
        dcc.Graph(id='heatmap',
                   className='pretty_container', style={'width': '100%'}
                   )
    ])

cash_info_table_stock = html.Div(
    className='pretty_container row',
    children=[
        html.Div(
            className='scrollable-table-container',
            style={'height': '600px', 'overflow': 'auto'},
            children=[
                html.Table(id='cashflows',
                           className='pretty_container',
                           )                
            ]
        ),
        html.Div(
            className='scrollable-table-container',
            style={'height': '600px', 'overflow': 'auto'},
            children=[                
                html.Table(id='actor_deposits',
                           className='pretty_container',
                           )
            ]
        )

    ])

var = html.Div(
    className='pretty_container row',
    children=[
        html.Div(style={'width': '60%', 'float': 'left', 'border-radius': '5px',
                        'margin': '10px', 'padding': '15px', 'position': 'relative',
                        'box-shadow': '2px 2px 2px lightgrey', 'background-color': 'rgb(255,255,255)'},
                 children=[
                     dcc.Graph(id="histogram"), ]
                 ),
        html.Div(style={'width': '60%', 'float': 'left', 'border-radius': '5px',
                        'margin': '10px', 'padding': '15px', 'position': 'relative',
                        'box-shadow': '2px 2px 2px lightgrey', 'background-color': 'rgb(255,255,255)'},
                 children=[
                     html.Div(
                         className="pretty_container row",
                         children=[
                             html.Table(id='table_var', className='pretty_container', style={'width': '100%'})
                         ]
                     )

                 ]
                 )
    ])

time_series_returns = html.Div(
    className='pretty_container row',
    children=[html.Div(style={'width': '100%', 'float': 'left', 'border-radius': '5px',
                        'margin': '10px', 'padding': '15px', 'position': 'relative',
                        'box-shadow': '2px 2px 2px lightgrey', 'background-color': 'rgb(255,255,255)'},
                 children=[
                     dcc.Graph(id="returns_time_series"), ]
                 )])

# LAYOUT
app.layout = html.Div(
                      style={'display': 'flex', 'flex-direction': 'column'},
                      children=[
                          # dcc.Interval(id='interval_update',
                          #              interval=50000),
                          html.Div(id='update'),
                          dcc.Location(id='url', refresh=False),
                          html.Link(rel='stylesheet', href='input_files/stylesheet.css'),
                          banner,
                          html.Div([
                              dcc.Tabs([
                                  dcc.Tab(label='Main Information', children=[
                                      main_info_graphs,
                                      main_info_table_stock,
                                      heatmap
                                  ]),
                                  dcc.Tab(label='Cashflows Information', children=[
                                      cash_info_table_stock
                                  ]),
                                  dcc.Tab(label='Risk Management', children=[
                                      var,
                                      time_series_returns
                                  ]),
                              ])
                          ]),

                      ])
