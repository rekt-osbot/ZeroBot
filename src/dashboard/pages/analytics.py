"""
Analytics page for the ZeroBot dashboard
"""
import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_analytics_layout(trade_bot):
    """Create the analytics page layout"""
    layout = dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H2("Market Analytics", className="mb-3"),
                html.P("Advanced market analysis and performance metrics to optimize your trading strategy.", className="text-muted")
            ])
        ], className="mb-4"),
        
        # Market Overview
        dbc.Row([
            # Market Summary
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("Market Summary", className="d-inline"),
                        dbc.ButtonGroup([
                            dbc.Button("1D", id="market-1d", color="primary", size="sm", outline=True, className="me-1"),
                            dbc.Button("1W", id="market-1w", color="primary", size="sm", outline=True, className="me-1"),
                            dbc.Button("1M", id="market-1m", color="primary", size="sm", outline=True, className="me-1"),
                            dbc.Button("3M", id="market-3m", color="primary", size="sm", outline=True),
                        ], className="float-end"),
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            # NSE Index
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H5("NIFTY 50", className="card-title"),
                                        html.H3("22,456.80", className="text-success"),
                                        html.P([
                                            html.Span("▲ 245.20 (1.10%)", className="text-success"),
                                            html.Span(" Today", className="text-muted ms-2")
                                        ])
                                    ])
                                ], className="mb-3 border-success")
                            ], width=6),
                            
                            # BSE Index
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H5("SENSEX", className="card-title"),
                                        html.H3("73,890.50", className="text-success"),
                                        html.P([
                                            html.Span("▲ 780.40 (1.07%)", className="text-success"),
                                            html.Span(" Today", className="text-muted ms-2")
                                        ])
                                    ])
                                ], className="mb-3 border-success")
                            ], width=6),
                        ]),
                        
                        # Market Index Chart
                        dcc.Graph(
                            id="market-index-chart",
                            config={"displayModeBar": False},
                            style={"height": "300px"}
                        )
                    ])
                ], className="mb-4")
            ], width=8),
            
            # Market Movers
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Top Movers"),
                    dbc.CardBody([
                        # Tabs for Gainers and Losers
                        dbc.Tabs([
                            dbc.Tab([
                                html.Div(id="top-gainers", className="mt-3")
                            ], label="Top Gainers", tab_id="gainers"),
                            
                            dbc.Tab([
                                html.Div(id="top-losers", className="mt-3")
                            ], label="Top Losers", tab_id="losers"),
                        ], id="movers-tabs", active_tab="gainers")
                    ])
                ], className="mb-4 h-100")
            ], width=4)
        ]),
        
        # Performance Analysis
        dbc.Row([
            # Performance Metrics
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Performance Metrics"),
                    dbc.CardBody([
                        dbc.Row([
                            # Profit Factor
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H5("Profit Factor", className="card-title"),
                                        html.Div([
                                            html.Span("2.4", className="display-4 text-success")
                                        ], className="text-center"),
                                        html.P("Ratio of gross profit to gross loss", className="text-muted text-center small mt-2")
                                    ])
                                ], className="mb-3")
                            ], width=3),
                            
                            # Sharpe Ratio
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H5("Sharpe Ratio", className="card-title"),
                                        html.Div([
                                            html.Span("1.8", className="display-4 text-success")
                                        ], className="text-center"),
                                        html.P("Risk-adjusted return measure", className="text-muted text-center small mt-2")
                                    ])
                                ], className="mb-3")
                            ], width=3),
                            
                            # Max Drawdown
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H5("Max Drawdown", className="card-title"),
                                        html.Div([
                                            html.Span("12.5%", className="display-4 text-danger")
                                        ], className="text-center"),
                                        html.P("Maximum observed loss", className="text-muted text-center small mt-2")
                                    ])
                                ], className="mb-3")
                            ], width=3),
                            
                            # Expectancy
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H5("Expectancy", className="card-title"),
                                        html.Div([
                                            html.Span("₹250", className="display-4 text-success")
                                        ], className="text-center"),
                                        html.P("Average expected profit per trade", className="text-muted text-center small mt-2")
                                    ])
                                ], className="mb-3")
                            ], width=3),
                        ]),
                        
                        # Performance Chart
                        dcc.Graph(
                            id="performance-chart",
                            config={"displayModeBar": False},
                            style={"height": "300px"}
                        )
                    ])
                ], className="mb-4")
            ], width=8),
            
            # Trade Analysis
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Trade Analysis"),
                    dbc.CardBody([
                        # Trade Distribution by Time
                        dcc.Graph(
                            id="trade-time-distribution",
                            config={"displayModeBar": False},
                            style={"height": "200px"}
                        ),
                        
                        html.Hr(),
                        
                        # Trade Distribution by Symbol
                        dcc.Graph(
                            id="trade-symbol-distribution",
                            config={"displayModeBar": False},
                            style={"height": "200px"}
                        )
                    ])
                ], className="mb-4")
            ], width=4)
        ]),
        
        # Market Correlation
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Market Correlation Matrix"),
                    dbc.CardBody([
                        dcc.Graph(
                            id="correlation-matrix",
                            config={"displayModeBar": False},
                            style={"height": "400px"}
                        )
                    ])
                ])
            ])
        ])
    ], fluid=True)
    
    return layout

def register_analytics_callbacks(app, trade_bot):
    """Register callbacks for the analytics page"""
    
    # Market Index Chart
    @app.callback(
        Output("market-index-chart", "figure"),
        [Input("market-1d", "n_clicks"),
         Input("market-1w", "n_clicks"),
         Input("market-1m", "n_clicks"),
         Input("market-3m", "n_clicks")]
    )
    def update_market_index_chart(day_clicks, week_clicks, month_clicks, three_month_clicks):
        # Determine which button was clicked
        ctx = dash.callback_context
        if not ctx.triggered:
            # Default to 1 month view
            days = 30
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if button_id == "market-1d":
                days = 1
            elif button_id == "market-1w":
                days = 7
            elif button_id == "market-1m":
                days = 30
            else:  # 3 months
                days = 90
        
        # Generate sample data
        dates = pd.date_range(start=datetime.now() - timedelta(days=days), end=datetime.now(), freq='D')
        
        # Generate NIFTY data
        np.random.seed(42)  # For reproducibility
        nifty_base = 22000
        nifty_prices = [nifty_base]
        for i in range(1, len(dates)):
            change = np.random.normal(0.05, 1.0)  # Slight positive drift
            nifty_prices.append(nifty_prices[-1] * (1 + change / 100))
        
        # Generate SENSEX data
        sensex_base = 73000
        sensex_prices = [sensex_base]
        for i in range(1, len(dates)):
            change = np.random.normal(0.05, 1.0)  # Slight positive drift
            sensex_prices.append(sensex_prices[-1] * (1 + change / 100))
        
        # Create figure
        fig = go.Figure()
        
        # Add NIFTY line
        fig.add_trace(go.Scatter(
            x=dates,
            y=nifty_prices,
            mode='lines',
            name='NIFTY 50',
            line={'width': 2, 'color': '#00FF00'}
        ))
        
        # Add SENSEX line
        fig.add_trace(go.Scatter(
            x=dates,
            y=sensex_prices,
            mode='lines',
            name='SENSEX',
            line={'width': 2, 'color': '#FF9900'},
            yaxis="y2"
        ))
        
        # Update layout
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin={'l': 40, 'r': 40, 't': 10, 'b': 40},
            xaxis={
                'showgrid': False,
                'showline': True,
                'linecolor': '#444',
                'linewidth': 1,
                'title': None
            },
            yaxis={
                'showgrid': True,
                'gridcolor': '#444',
                'showline': True,
                'linecolor': '#444',
                'linewidth': 1,
                'title': 'NIFTY 50',
                'side': 'left'
            },
            yaxis2={
                'showgrid': False,
                'showline': True,
                'linecolor': '#444',
                'linewidth': 1,
                'title': 'SENSEX',
                'side': 'right',
                'overlaying': 'y'
            },
            legend={
                'orientation': 'h',
                'yanchor': 'bottom',
                'y': 1.02,
                'xanchor': 'right',
                'x': 1
            }
        )
        
        return fig
    
    # Top Gainers
    @app.callback(
        Output("top-gainers", "children"),
        Input("interval-component", "n_intervals")
    )
    def update_top_gainers(n):
        # Generate sample data for top gainers
        gainers = [
            {"symbol": "RELIANCE", "price": 2450.75, "change": 3.5},
            {"symbol": "TCS", "price": 3750.50, "change": 2.8},
            {"symbol": "INFY", "price": 1420.75, "change": 2.2},
            {"symbol": "HDFCBANK", "price": 1650.25, "change": 1.9},
            {"symbol": "ICICIBANK", "price": 950.80, "change": 1.7}
        ]
        
        # Create table rows
        rows = []
        for gainer in gainers:
            symbol = gainer["symbol"]
            price = gainer["price"]
            change = gainer["change"]
            
            # Create row
            row = html.Tr([
                html.Td(symbol),
                html.Td(f"₹{price:.2f}"),
                html.Td(f"▲ {change:.2f}%", className="text-success")
            ])
            
            rows.append(row)
        
        # Create table
        table = dbc.Table(
            [
                html.Thead(
                    html.Tr([
                        html.Th("Symbol"),
                        html.Th("Price"),
                        html.Th("Change")
                    ])
                ),
                html.Tbody(rows)
            ],
            bordered=False,
            hover=True,
            responsive=True,
            striped=True,
            size="sm"
        )
        
        return table
    
    # Top Losers
    @app.callback(
        Output("top-losers", "children"),
        Input("interval-component", "n_intervals")
    )
    def update_top_losers(n):
        # Generate sample data for top losers
        losers = [
            {"symbol": "BHARTIARTL", "price": 850.25, "change": -2.1},
            {"symbol": "ITC", "price": 420.50, "change": -1.8},
            {"symbol": "HINDUNILVR", "price": 2520.75, "change": -1.5},
            {"symbol": "KOTAKBANK", "price": 1750.30, "change": -1.3},
            {"symbol": "SBIN", "price": 650.90, "change": -1.1}
        ]
        
        # Create table rows
        rows = []
        for loser in losers:
            symbol = loser["symbol"]
            price = loser["price"]
            change = loser["change"]
            
            # Create row
            row = html.Tr([
                html.Td(symbol),
                html.Td(f"₹{price:.2f}"),
                html.Td(f"▼ {abs(change):.2f}%", className="text-danger")
            ])
            
            rows.append(row)
        
        # Create table
        table = dbc.Table(
            [
                html.Thead(
                    html.Tr([
                        html.Th("Symbol"),
                        html.Th("Price"),
                        html.Th("Change")
                    ])
                ),
                html.Tbody(rows)
            ],
            bordered=False,
            hover=True,
            responsive=True,
            striped=True,
            size="sm"
        )
        
        return table
    
    # Performance Chart
    @app.callback(
        Output("performance-chart", "figure"),
        Input("interval-component", "n_intervals")
    )
    def update_performance_chart(n):
        # Generate sample data
        dates = pd.date_range(start=datetime.now() - timedelta(days=90), end=datetime.now(), freq='D')
        
        # Generate portfolio value data
        np.random.seed(42)  # For reproducibility
        portfolio_base = 100000
        portfolio_values = [portfolio_base]
        for i in range(1, len(dates)):
            change = np.random.normal(0.1, 1.2)  # Positive drift
            portfolio_values.append(portfolio_values[-1] * (1 + change / 100))
        
        # Generate benchmark data
        benchmark_base = 100000
        benchmark_values = [benchmark_base]
        for i in range(1, len(dates)):
            change = np.random.normal(0.05, 1.0)  # Smaller positive drift
            benchmark_values.append(benchmark_values[-1] * (1 + change / 100))
        
        # Create figure
        fig = go.Figure()
        
        # Add portfolio line
        fig.add_trace(go.Scatter(
            x=dates,
            y=portfolio_values,
            mode='lines',
            name='ZeroBot Portfolio',
            line={'width': 2, 'color': '#00FF00'}
        ))
        
        # Add benchmark line
        fig.add_trace(go.Scatter(
            x=dates,
            y=benchmark_values,
            mode='lines',
            name='NIFTY 50 (Benchmark)',
            line={'width': 2, 'color': '#888888'}
        ))
        
        # Update layout
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin={'l': 40, 'r': 40, 't': 10, 'b': 40},
            xaxis={
                'showgrid': False,
                'showline': True,
                'linecolor': '#444',
                'linewidth': 1,
                'title': None
            },
            yaxis={
                'showgrid': True,
                'gridcolor': '#444',
                'showline': True,
                'linecolor': '#444',
                'linewidth': 1,
                'title': 'Portfolio Value (₹)'
            },
            legend={
                'orientation': 'h',
                'yanchor': 'bottom',
                'y': 1.02,
                'xanchor': 'right',
                'x': 1
            }
        )
        
        return fig
    
    # Trade Time Distribution
    @app.callback(
        Output("trade-time-distribution", "figure"),
        Input("interval-component", "n_intervals")
    )
    def update_trade_time_distribution(n):
        # Generate sample data
        hours = list(range(9, 16))  # Trading hours: 9 AM to 3 PM
        trades = [15, 22, 18, 25, 30, 20, 10]  # Number of trades per hour
        
        # Create figure
        fig = px.bar(
            x=hours,
            y=trades,
            labels={'x': 'Hour of Day', 'y': 'Number of Trades'},
            color_discrete_sequence=['#00FF00']
        )
        
        # Update layout
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin={'l': 40, 'r': 40, 't': 10, 'b': 40},
            xaxis={
                'showgrid': False,
                'showline': True,
                'linecolor': '#444',
                'linewidth': 1,
                'title': 'Hour of Day',
                'tickvals': hours,
                'ticktext': [f"{h}:00" for h in hours]
            },
            yaxis={
                'showgrid': True,
                'gridcolor': '#444',
                'showline': True,
                'linecolor': '#444',
                'linewidth': 1,
                'title': 'Number of Trades'
            }
        )
        
        return fig
    
    # Trade Symbol Distribution
    @app.callback(
        Output("trade-symbol-distribution", "figure"),
        Input("interval-component", "n_intervals")
    )
    def update_trade_symbol_distribution(n):
        # Generate sample data
        symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
        trades = [35, 28, 22, 18, 15]  # Number of trades per symbol
        
        # Create figure
        fig = px.pie(
            names=symbols,
            values=trades,
            color_discrete_sequence=['#00FF00', '#00CCFF', '#FF9900', '#FF00FF', '#FFFF00']
        )
        
        # Update layout
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin={'l': 10, 'r': 10, 't': 10, 'b': 10},
            legend={
                'orientation': 'h',
                'yanchor': 'bottom',
                'y': -0.2,
                'xanchor': 'center',
                'x': 0.5
            }
        )
        
        return fig
    
    # Correlation Matrix
    @app.callback(
        Output("correlation-matrix", "figure"),
        Input("interval-component", "n_intervals")
    )
    def update_correlation_matrix(n):
        # Generate sample correlation data
        symbols = ["NIFTY", "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "BHARTIARTL", "ITC", "HINDUNILVR", "KOTAKBANK"]
        
        # Create a correlation matrix with random values
        np.random.seed(42)  # For reproducibility
        corr_matrix = np.random.uniform(0.5, 1.0, size=(len(symbols), len(symbols)))
        
        # Make the matrix symmetric
        corr_matrix = (corr_matrix + corr_matrix.T) / 2
        
        # Set diagonal to 1.0
        np.fill_diagonal(corr_matrix, 1.0)
        
        # Create a DataFrame
        corr_df = pd.DataFrame(corr_matrix, index=symbols, columns=symbols)
        
        # Create figure
        fig = px.imshow(
            corr_df,
            color_continuous_scale='RdBu_r',
            zmin=-1,
            zmax=1
        )
        
        # Update layout
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin={'l': 40, 'r': 40, 't': 40, 'b': 40},
            coloraxis_colorbar={
                'title': 'Correlation',
                'thickness': 15,
                'len': 0.5,
                'y': 0.5
            }
        )
        
        return fig
