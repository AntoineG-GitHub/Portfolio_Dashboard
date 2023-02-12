from dash import html, dcc

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