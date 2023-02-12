from dash import html, dcc
from components.banner import *
from components.tab1 import *

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


