"""
Strategies page for the ZeroBot dashboard
"""
import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_strategies_layout(trade_bot):
    """Create the strategies page layout"""
    layout = dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H2("Trading Strategies", className="mb-3"),
                html.P("Configure and monitor your trading strategies for optimal performance.", className="text-muted")
            ])
        ], className="mb-4"),
        
        # Strategy Overview
        dbc.Row([
            # Strategy Cards
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("Active Strategies", className="d-inline"),
                        dbc.Button("Add Strategy", id="add-strategy-button", color="success", size="sm", className="float-end")
                    ]),
                    dbc.CardBody([
                        # Strategy Cards
                        dbc.Row([
                            # Moving Average Crossover
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader([
                                        html.H5("Moving Average Crossover", className="d-inline"),
                                        dbc.Switch(
                                            id="ma-crossover-switch",
                                            value=True,
                                            className="float-end"
                                        )
                                    ]),
                                    dbc.CardBody([
                                        html.P("Uses short and long-term moving averages to identify trend changes and generate trading signals."),
                                        dbc.Row([
                                            dbc.Col([
                                                html.P("Performance:", className="mb-1"),
                                                html.H5("76% Win Rate", className="text-success")
                                            ], width=6),
                                            dbc.Col([
                                                html.P("Signal Quality:", className="mb-1"),
                                                dbc.Progress(value=76, color="success", className="mb-3", style={"height": "8px"})
                                            ], width=6)
                                        ]),
                                        dbc.Button("Configure", id="configure-ma-button", color="primary", size="sm", className="mt-2")
                                    ]),
                                    dbc.CardFooter([
                                        html.Small("Last Signal: BUY RELIANCE @ ₹2,450.75 (2 hours ago)", className="text-muted")
                                    ])
                                ], className="mb-3 strategy-card")
                            ], width=6),
                            
                            # RSI Strategy
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader([
                                        html.H5("RSI Strategy", className="d-inline"),
                                        dbc.Switch(
                                            id="rsi-switch",
                                            value=True,
                                            className="float-end"
                                        )
                                    ]),
                                    dbc.CardBody([
                                        html.P("Uses the Relative Strength Index to identify overbought and oversold conditions in the market."),
                                        dbc.Row([
                                            dbc.Col([
                                                html.P("Performance:", className="mb-1"),
                                                html.H5("68% Win Rate", className="text-success")
                                            ], width=6),
                                            dbc.Col([
                                                html.P("Signal Quality:", className="mb-1"),
                                                dbc.Progress(value=68, color="success", className="mb-3", style={"height": "8px"})
                                            ], width=6)
                                        ]),
                                        dbc.Button("Configure", id="configure-rsi-button", color="primary", size="sm", className="mt-2")
                                    ]),
                                    dbc.CardFooter([
                                        html.Small("Last Signal: BUY TCS @ ₹3,750.50 (5 hours ago)", className="text-muted")
                                    ])
                                ], className="mb-3 strategy-card")
                            ], width=6),
                            
                            # MACD Strategy
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader([
                                        html.H5("MACD Strategy", className="d-inline"),
                                        dbc.Switch(
                                            id="macd-switch",
                                            value=True,
                                            className="float-end"
                                        )
                                    ]),
                                    dbc.CardBody([
                                        html.P("Uses the Moving Average Convergence Divergence indicator to identify momentum changes."),
                                        dbc.Row([
                                            dbc.Col([
                                                html.P("Performance:", className="mb-1"),
                                                html.H5("72% Win Rate", className="text-success")
                                            ], width=6),
                                            dbc.Col([
                                                html.P("Signal Quality:", className="mb-1"),
                                                dbc.Progress(value=72, color="success", className="mb-3", style={"height": "8px"})
                                            ], width=6)
                                        ]),
                                        dbc.Button("Configure", id="configure-macd-button", color="primary", size="sm", className="mt-2")
                                    ]),
                                    dbc.CardFooter([
                                        html.Small("Last Signal: SELL HDFCBANK @ ₹1,650.25 (1 hour ago)", className="text-muted")
                                    ])
                                ], className="mb-3 strategy-card")
                            ], width=6),
                            
                            # Bollinger Bands Strategy
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader([
                                        html.H5("Bollinger Bands Strategy", className="d-inline"),
                                        dbc.Switch(
                                            id="bollinger-switch",
                                            value=False,
                                            className="float-end"
                                        )
                                    ]),
                                    dbc.CardBody([
                                        html.P("Uses Bollinger Bands to identify volatility and potential price reversals."),
                                        dbc.Row([
                                            dbc.Col([
                                                html.P("Performance:", className="mb-1"),
                                                html.H5("65% Win Rate", className="text-success")
                                            ], width=6),
                                            dbc.Col([
                                                html.P("Signal Quality:", className="mb-1"),
                                                dbc.Progress(value=65, color="warning", className="mb-3", style={"height": "8px"})
                                            ], width=6)
                                        ]),
                                        dbc.Button("Configure", id="configure-bollinger-button", color="primary", size="sm", className="mt-2")
                                    ]),
                                    dbc.CardFooter([
                                        html.Small("Last Signal: BUY INFY @ ₹1,420.75 (8 hours ago)", className="text-muted")
                                    ])
                                ], className="mb-3 strategy-card")
                            ], width=6),
                        ])
                    ])
                ], className="mb-4")
            ], width=8),
            
            # Strategy Performance
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Strategy Performance"),
                    dbc.CardBody([
                        dcc.Graph(
                            id="strategy-performance-chart",
                            config={"displayModeBar": False},
                            style={"height": "300px"}
                        )
                    ])
                ], className="mb-4"),
                
                dbc.Card([
                    dbc.CardHeader("Signal Distribution"),
                    dbc.CardBody([
                        dcc.Graph(
                            id="strategy-signal-distribution",
                            config={"displayModeBar": False},
                            style={"height": "300px"}
                        )
                    ])
                ])
            ], width=4)
        ]),
        
        # Strategy Backtest
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("Strategy Backtesting", className="d-inline"),
                        dbc.Button("Run Backtest", id="run-backtest-button", color="primary", size="sm", className="float-end")
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Select Strategy"),
                                dcc.Dropdown(
                                    id="backtest-strategy-dropdown",
                                    options=[
                                        {"label": "Moving Average Crossover", "value": "ma_crossover"},
                                        {"label": "RSI Strategy", "value": "rsi"},
                                        {"label": "MACD Strategy", "value": "macd"},
                                        {"label": "Bollinger Bands Strategy", "value": "bollinger"},
                                        {"label": "Supertrend Strategy", "value": "supertrend"}
                                    ],
                                    value="ma_crossover",
                                    className="mb-3"
                                )
                            ], width=4),
                            dbc.Col([
                                html.Label("Select Symbol"),
                                dcc.Dropdown(
                                    id="backtest-symbol-dropdown",
                                    options=[
                                        {"label": "RELIANCE", "value": "RELIANCE"},
                                        {"label": "TCS", "value": "TCS"},
                                        {"label": "INFY", "value": "INFY"},
                                        {"label": "HDFCBANK", "value": "HDFCBANK"},
                                        {"label": "ICICIBANK", "value": "ICICIBANK"}
                                    ],
                                    value="RELIANCE",
                                    className="mb-3"
                                )
                            ], width=4),
                            dbc.Col([
                                html.Label("Date Range"),
                                dcc.DatePickerRange(
                                    id="backtest-date-range",
                                    start_date=datetime.now() - timedelta(days=90),
                                    end_date=datetime.now(),
                                    display_format="YYYY-MM-DD",
                                    className="mb-3"
                                )
                            ], width=4)
                        ]),
                        
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(
                                    id="backtest-chart",
                                    config={"displayModeBar": False},
                                    style={"height": "400px"}
                                )
                            ])
                        ]),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H5("Backtest Results", className="card-title"),
                                        html.Div(id="backtest-results")
                                    ])
                                ])
                            ])
                        ], className="mt-3")
                    ])
                ])
            ])
        ])
    ], fluid=True)
    
    return layout

def register_strategies_callbacks(app, trade_bot):
    """Register callbacks for the strategies page"""
    
    # Strategy Performance Chart
    @app.callback(
        Output("strategy-performance-chart", "figure"),
        Input("interval-component", "n_intervals")
    )
    def update_strategy_performance_chart(n):
        # Generate sample data for strategy performance
        strategies = ["MA Crossover", "RSI", "MACD", "Bollinger"]
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        
        fig = go.Figure()
        
        # Generate random performance data for each strategy
        np.random.seed(42)  # For reproducibility
        base = 100
        
        for i, strategy in enumerate(strategies):
            # Create a random walk with positive drift
            performance = [base]
            for j in range(1, len(dates)):
                change = np.random.normal(0.2, 1.5)  # Mean positive drift
                performance.append(performance[-1] * (1 + change / 100))
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=performance,
                mode='lines',
                name=strategy
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
                'title': None
            },
            legend={
                'orientation': 'h',
                'yanchor': 'bottom',
                'y': 1.02,
                'xanchor': 'right',
                'x': 1
            },
            hovermode='x unified'
        )
        
        return fig
    
    # Strategy Signal Distribution
    @app.callback(
        Output("strategy-signal-distribution", "figure"),
        Input("interval-component", "n_intervals")
    )
    def update_signal_distribution(n):
        # Generate sample data for signal distribution
        strategies = ["MA Crossover", "RSI", "MACD", "Bollinger"]
        buy_signals = [42, 35, 38, 30]
        sell_signals = [38, 32, 35, 28]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=strategies,
            y=buy_signals,
            name='Buy Signals',
            marker_color='#00FF00'
        ))
        
        fig.add_trace(go.Bar(
            x=strategies,
            y=sell_signals,
            name='Sell Signals',
            marker_color='#FF0000'
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
                'title': 'Number of Signals'
            },
            legend={
                'orientation': 'h',
                'yanchor': 'bottom',
                'y': 1.02,
                'xanchor': 'right',
                'x': 1
            },
            barmode='group'
        )
        
        return fig
    
    # Backtest Chart
    @app.callback(
        [Output("backtest-chart", "figure"),
         Output("backtest-results", "children")],
        [Input("run-backtest-button", "n_clicks")],
        [State("backtest-strategy-dropdown", "value"),
         State("backtest-symbol-dropdown", "value"),
         State("backtest-date-range", "start_date"),
         State("backtest-date-range", "end_date")]
    )
    def run_backtest(n_clicks, strategy, symbol, start_date, end_date):
        if not n_clicks:
            # Return empty chart and results if button not clicked
            empty_fig = {
                'data': [],
                'layout': {
                    'paper_bgcolor': 'rgba(0,0,0,0)',
                    'plot_bgcolor': 'rgba(0,0,0,0)',
                    'xaxis': {'showgrid': False},
                    'yaxis': {'showgrid': False},
                    'annotations': [{
                        'text': 'Run a backtest to see results',
                        'xref': 'paper',
                        'yref': 'paper',
                        'showarrow': False,
                        'font': {'size': 20, 'color': 'white'}
                    }]
                }
            }
            
            empty_results = html.P("No backtest results yet. Click 'Run Backtest' to begin.", className="text-muted")
            
            return empty_fig, empty_results
        
        # Generate sample backtest data
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Generate price data
        np.random.seed(42)  # For reproducibility
        base_price = 1000
        prices = [base_price]
        for i in range(1, len(dates)):
            change = np.random.normal(0, 20)
            prices.append(max(prices[-1] + change, 1))  # Ensure price is positive
        
        # Generate signals
        signals = np.zeros(len(dates))
        for i in range(10, len(dates), 20):
            if i + 10 < len(dates):
                signals[i] = 1  # Buy signal
                signals[i + 10] = -1  # Sell signal
        
        # Create figure
        fig = go.Figure()
        
        # Add price line
        fig.add_trace(go.Scatter(
            x=dates,
            y=prices,
            mode='lines',
            name='Price',
            line={'width': 2, 'color': '#FFFFFF'}
        ))
        
        # Add buy signals
        buy_dates = [dates[i] for i in range(len(signals)) if signals[i] == 1]
        buy_prices = [prices[i] for i in range(len(signals)) if signals[i] == 1]
        
        fig.add_trace(go.Scatter(
            x=buy_dates,
            y=buy_prices,
            mode='markers',
            name='Buy Signal',
            marker={'size': 10, 'color': '#00FF00', 'symbol': 'triangle-up'}
        ))
        
        # Add sell signals
        sell_dates = [dates[i] for i in range(len(signals)) if signals[i] == -1]
        sell_prices = [prices[i] for i in range(len(signals)) if signals[i] == -1]
        
        fig.add_trace(go.Scatter(
            x=sell_dates,
            y=sell_prices,
            mode='markers',
            name='Sell Signal',
            marker={'size': 10, 'color': '#FF0000', 'symbol': 'triangle-down'}
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
                'title': 'Price (₹)'
            },
            legend={
                'orientation': 'h',
                'yanchor': 'bottom',
                'y': 1.02,
                'xanchor': 'right',
                'x': 1
            }
        )
        
        # Generate backtest results
        total_trades = len(buy_dates)
        winning_trades = int(total_trades * 0.7)  # 70% win rate
        losing_trades = total_trades - winning_trades
        
        avg_profit = 50  # ₹50 per winning trade
        avg_loss = 30  # ₹30 per losing trade
        
        total_profit = winning_trades * avg_profit
        total_loss = losing_trades * avg_loss
        net_profit = total_profit - total_loss
        
        roi = (net_profit / base_price) * 100
        
        # Create results table
        results = html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6("Total Trades"),
                    html.H4(f"{total_trades}")
                ], width=3),
                dbc.Col([
                    html.H6("Win Rate"),
                    html.H4(f"{(winning_trades / total_trades * 100):.1f}%", className="text-success")
                ], width=3),
                dbc.Col([
                    html.H6("Net Profit"),
                    html.H4(f"₹{net_profit:,.2f}", className="text-success")
                ], width=3),
                dbc.Col([
                    html.H6("ROI"),
                    html.H4(f"{roi:.2f}%", className="text-success")
                ], width=3)
            ]),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    html.H6("Winning Trades"),
                    html.H4(f"{winning_trades}")
                ], width=3),
                dbc.Col([
                    html.H6("Losing Trades"),
                    html.H4(f"{losing_trades}")
                ], width=3),
                dbc.Col([
                    html.H6("Avg. Profit"),
                    html.H4(f"₹{avg_profit:,.2f}")
                ], width=3),
                dbc.Col([
                    html.H6("Avg. Loss"),
                    html.H4(f"₹{avg_loss:,.2f}")
                ], width=3)
            ])
        ])
        
        return fig, results
