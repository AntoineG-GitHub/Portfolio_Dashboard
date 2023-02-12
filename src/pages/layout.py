from dash import html, dcc, Dash
from components.banner import *
from components.tab1 import *
from components.tab2 import *
from components.tab3 import *

# LAYOUT

app = Dash(__name__)
application = app.server
app.title = 'Umbrella'


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