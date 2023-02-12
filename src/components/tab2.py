from dash import html, dcc

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