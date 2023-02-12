from dash import html

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