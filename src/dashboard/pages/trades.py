"""
Trades page for the ZeroBot dashboard
"""
import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_trades_layout(trade_bot):
    """Create the trades page layout"""
    layout = dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H2("Trade Management", className="mb-3"),
                html.P("Monitor and manage your active trades and view detailed trade history.", className="text-muted")
            ])
        ], className="mb-4"),
        
        # Tabs for Active Trades and Trade History
        dbc.Tabs([
            # Active Trades Tab
            dbc.Tab([
                dbc.Row([
                    # Active Trades Stats
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H4("Active Trades", className="card-title"),
                                        html.H2(id="active-trades-count-page", className="display-4 text-center"),
                                    ])
                                ], className="h-100 border-primary")
                            ], width=4),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H4("Unrealized P&L", className="card-title"),
                                        html.H2(id="unrealized-pnl", className="display-4 text-center"),
                                    ])
                                ], className="h-100 border-success")
                            ], width=4),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H4("Invested Capital", className="card-title"),
                                        html.H2(id="invested-capital", className="display-4 text-center"),
                                    ])
                                ], className="h-100 border-info")
                            ], width=4),
                        ], className="mb-4"),
                        
                        # Active Trades Table
                        dbc.Card([
                            dbc.CardHeader([
                                html.H4("Active Trades", className="d-inline"),
                                dbc.Button("Refresh", id="refresh-active-trades", color="primary", size="sm", className="float-end"),
                            ]),
                            dbc.CardBody([
                                html.Div(id="active-trades-table-page"),
                            ])
                        ]),
                    ], width=8),
                    
                    # Trade Details
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Trade Details"),
                            dbc.CardBody([
                                html.Div(id="trade-details", className="text-center text-muted", children=[
                                    html.P("Select a trade to view details"),
                                    html.I(className="fas fa-chart-line fa-3x mt-3")
                                ])
                            ])
                        ], className="mb-4 h-100")
                    ], width=4),
                ], className="mb-4"),
                
                # Price Chart for Selected Trade
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.H4("Price Chart", className="d-inline"),
                                dbc.ButtonGroup([
                                    dbc.Button("1D", id="timeframe-1d", color="primary", size="sm", outline=True, className="me-1"),
                                    dbc.Button("1W", id="timeframe-1w", color="primary", size="sm", outline=True, className="me-1"),
                                    dbc.Button("1M", id="timeframe-1m", color="primary", size="sm", outline=True),
                                ], className="float-end"),
                            ]),
                            dbc.CardBody([
                                dcc.Graph(
                                    id="trade-price-chart",
                                    config={"displayModeBar": False},
                                    style={"height": "400px"},
                                )
                            ])
                        ])
                    ])
                ])
            ], label="Active Trades", tab_id="active-trades"),
            
            # Trade History Tab
            dbc.Tab([
                dbc.Row([
                    # Trade History Stats
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H4("Total Trades", className="card-title"),
                                        html.H2(id="total-trades-count", className="display-4 text-center"),
                                    ])
                                ], className="h-100 border-primary")
                            ], width=3),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H4("Win Rate", className="card-title"),
                                        html.H2(id="win-rate-page", className="display-4 text-center"),
                                    ])
                                ], className="h-100 border-success")
                            ], width=3),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H4("Avg. Profit", className="card-title"),
                                        html.H2(id="avg-profit-page", className="display-4 text-center"),
                                    ])
                                ], className="h-100 border-info")
                            ], width=3),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H4("Avg. Loss", className="card-title"),
                                        html.H2(id="avg-loss-page", className="display-4 text-center"),
                                    ])
                                ], className="h-100 border-danger")
                            ], width=3),
                        ], className="mb-4"),
                        
                        # Trade History Filters
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader("Trade History Filters"),
                                    dbc.CardBody([
                                        dbc.Row([
                                            dbc.Col([
                                                html.Label("Date Range"),
                                                dcc.DatePickerRange(
                                                    id="trade-date-range",
                                                    start_date=datetime.now() - timedelta(days=30),
                                                    end_date=datetime.now(),
                                                    display_format="YYYY-MM-DD",
                                                    className="w-100"
                                                )
                                            ], width=6),
                                            dbc.Col([
                                                html.Label("Symbol"),
                                                dcc.Dropdown(
                                                    id="trade-symbol-filter",
                                                    options=[],
                                                    placeholder="All Symbols",
                                                    className="w-100"
                                                )
                                            ], width=3),
                                            dbc.Col([
                                                html.Label("Result"),
                                                dcc.Dropdown(
                                                    id="trade-result-filter",
                                                    options=[
                                                        {"label": "All", "value": "all"},
                                                        {"label": "Profit", "value": "profit"},
                                                        {"label": "Loss", "value": "loss"}
                                                    ],
                                                    value="all",
                                                    className="w-100"
                                                )
                                            ], width=3),
                                        ]),
                                        dbc.Row([
                                            dbc.Col([
                                                dbc.Button("Apply Filters", id="apply-trade-filters", color="primary", className="mt-3")
                                            ], className="text-end")
                                        ])
                                    ])
                                ])
                            ])
                        ], className="mb-4"),
                        
                        # Trade History Table
                        dbc.Card([
                            dbc.CardHeader("Trade History"),
                            dbc.CardBody([
                                html.Div(id="trade-history-table-page"),
                            ])
                        ], className="mb-4"),
                        
                        # Trade Performance Charts
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader("Cumulative P&L"),
                                    dbc.CardBody([
                                        dcc.Graph(
                                            id="cumulative-pnl-chart",
                                            config={"displayModeBar": False},
                                            style={"height": "300px"},
                                        )
                                    ])
                                ])
                            ], width=6),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader("P&L Distribution"),
                                    dbc.CardBody([
                                        dcc.Graph(
                                            id="pnl-distribution-chart",
                                            config={"displayModeBar": False},
                                            style={"height": "300px"},
                                        )
                                    ])
                                ])
                            ], width=6),
                        ])
                    ])
                ])
            ], label="Trade History", tab_id="trade-history"),
        ], id="trades-tabs", active_tab="active-trades"),
    ], fluid=True)
    
    return layout

def register_trades_callbacks(app, trade_bot):
    """Register callbacks for the trades page"""
    
    # Update active trades count
    @app.callback(
        Output("active-trades-count-page", "children"),
        Input("interval-component", "n_intervals")
    )
    def update_active_trades_count(n):
        active_trades = trade_bot.get_active_trades()
        return len(active_trades)
    
    # Update unrealized P&L
    @app.callback(
        [Output("unrealized-pnl", "children"),
         Output("unrealized-pnl", "className")],
        Input("interval-component", "n_intervals")
    )
    def update_unrealized_pnl(n):
        active_trades = trade_bot.get_active_trades()
        
        total_pnl = 0
        for order_id, trade in active_trades.items():
            instrument = trade['instrument']
            quantity = trade['quantity']
            buy_price = trade['buy_price']
            current_price = buy_price * (1 + np.random.uniform(-0.05, 0.05))  # Simulate price change
            pnl = (current_price - buy_price) * quantity
            total_pnl += pnl
        
        pnl_class = "display-4 text-center text-success" if total_pnl >= 0 else "display-4 text-center text-danger"
        
        return f"₹{total_pnl:,.2f}", pnl_class
    
    # Update invested capital
    @app.callback(
        Output("invested-capital", "children"),
        Input("interval-component", "n_intervals")
    )
    def update_invested_capital(n):
        active_trades = trade_bot.get_active_trades()
        
        total_invested = 0
        for order_id, trade in active_trades.items():
            quantity = trade['quantity']
            buy_price = trade['buy_price']
            invested = buy_price * quantity
            total_invested += invested
        
        return f"₹{total_invested:,.2f}"
    
    # Update active trades table
    @app.callback(
        Output("active-trades-table-page", "children"),
        [Input("interval-component", "n_intervals"),
         Input("refresh-active-trades", "n_clicks")]
    )
    def update_active_trades_table(n, clicks):
        active_trades = trade_bot.get_active_trades()
        
        if not active_trades:
            return html.Div([
                html.P("No active trades", className="text-center text-muted my-3"),
                html.I(className="fas fa-chart-line fa-3x text-center d-block text-muted")
            ])
        
        # Create table rows
        rows = []
        for order_id, trade in active_trades.items():
            instrument = trade['instrument']
            symbol = instrument['tradingsymbol']
            exchange = instrument['exchange']
            quantity = trade['quantity']
            buy_price = trade['buy_price']
            current_price = buy_price * (1 + np.random.uniform(-0.05, 0.05))  # Simulate price change
            pnl = (current_price - buy_price) * quantity
            pnl_percent = (pnl / (buy_price * quantity)) * 100
            
            # Determine class for styling
            pnl_class = "text-success" if pnl >= 0 else "text-danger"
            
            # Create row
            row = html.Tr([
                html.Td(f"{exchange}:{symbol}"),
                html.Td(f"{quantity}"),
                html.Td(f"₹{buy_price:.2f}"),
                html.Td(f"₹{current_price:.2f}"),
                html.Td(f"₹{pnl:.2f}", className=pnl_class),
                html.Td(f"{pnl_percent:.2f}%", className=pnl_class),
                html.Td([
                    dbc.Button("View", color="primary", size="sm", className="me-1", id={"type": "view-trade-button", "index": order_id}),
                    dbc.Button("Close", color="danger", size="sm", id={"type": "close-trade-button", "index": order_id})
                ])
            ])
            
            rows.append(row)
        
        # Create table
        table = dbc.Table(
            [
                html.Thead(
                    html.Tr([
                        html.Th("Symbol"),
                        html.Th("Quantity"),
                        html.Th("Buy Price"),
                        html.Th("Current Price"),
                        html.Th("P&L"),
                        html.Th("P&L %"),
                        html.Th("Actions")
                    ])
                ),
                html.Tbody(rows)
            ],
            bordered=True,
            hover=True,
            responsive=True,
            striped=True
        )
        
        return table
    
    # Update trade history stats
    @app.callback(
        [Output("total-trades-count", "children"),
         Output("win-rate-page", "children"),
         Output("avg-profit-page", "children"),
         Output("avg-loss-page", "children")],
        Input("interval-component", "n_intervals")
    )
    def update_trade_history_stats(n):
        metrics = trade_bot.get_metrics()
        
        total_trades = metrics['total_trades']
        win_rate = metrics['win_rate']
        avg_profit = metrics['avg_profit']
        avg_loss = metrics['avg_loss']
        
        return str(total_trades), f"{win_rate:.1f}%", f"₹{avg_profit:,.2f}", f"₹{avg_loss:,.2f}"
    
    # Update trade history table
    @app.callback(
        Output("trade-history-table-page", "children"),
        [Input("interval-component", "n_intervals"),
         Input("apply-trade-filters", "n_clicks")],
        [State("trade-date-range", "start_date"),
         State("trade-date-range", "end_date"),
         State("trade-symbol-filter", "value"),
         State("trade-result-filter", "value")]
    )
    def update_trade_history_table(n, clicks, start_date, end_date, symbol, result):
        trade_history = trade_bot.get_trade_history()
        
        if not trade_history:
            return html.Div([
                html.P("No trade history", className="text-center text-muted my-3"),
                html.I(className="fas fa-history fa-3x text-center d-block text-muted")
            ])
        
        # Apply filters if they exist
        filtered_history = trade_history
        if start_date and end_date:
            # Filter by date range
            pass
        
        if symbol:
            # Filter by symbol
            pass
        
        if result and result != "all":
            # Filter by result
            pass
        
        # Create table rows
        rows = []
        for trade in filtered_history:
            instrument = trade['instrument']
            symbol = instrument['tradingsymbol']
            exchange = instrument['exchange']
            quantity = trade['quantity']
            buy_price = trade['buy_price']
            sell_price = trade['sell_price']
            pnl = trade['pnl']
            pnl_percent = (pnl / (buy_price * quantity)) * 100
            timestamp = trade['sell_timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            reason = trade['reason'].capitalize()
            
            # Determine class for styling
            pnl_class = "text-success" if pnl >= 0 else "text-danger"
            
            # Create row
            row = html.Tr([
                html.Td(f"{exchange}:{symbol}"),
                html.Td(f"{quantity}"),
                html.Td(f"₹{buy_price:.2f}"),
                html.Td(f"₹{sell_price:.2f}"),
                html.Td(f"₹{pnl:.2f}", className=pnl_class),
                html.Td(f"{pnl_percent:.2f}%", className=pnl_class),
                html.Td(reason),
                html.Td(timestamp)
            ])
            
            rows.append(row)
        
        # Create table
        table = dbc.Table(
            [
                html.Thead(
                    html.Tr([
                        html.Th("Symbol"),
                        html.Th("Quantity"),
                        html.Th("Buy Price"),
                        html.Th("Sell Price"),
                        html.Th("P&L"),
                        html.Th("P&L %"),
                        html.Th("Reason"),
                        html.Th("Timestamp")
                    ])
                ),
                html.Tbody(rows)
            ],
            bordered=True,
            hover=True,
            responsive=True,
            striped=True
        )
        
        return table
    
    # Update cumulative P&L chart
    @app.callback(
        Output("cumulative-pnl-chart", "figure"),
        Input("interval-component", "n_intervals")
    )
    def update_cumulative_pnl_chart(n):
        trade_history = trade_bot.get_trade_history()
        
        if not trade_history:
            return {
                'data': [],
                'layout': {
                    'paper_bgcolor': 'rgba(0,0,0,0)',
                    'plot_bgcolor': 'rgba(0,0,0,0)',
                    'xaxis': {'showgrid': False},
                    'yaxis': {'showgrid': False},
                    'annotations': [{
                        'text': 'No trade data available',
                        'xref': 'paper',
                        'yref': 'paper',
                        'showarrow': False,
                        'font': {'size': 20, 'color': 'white'}
                    }]
                }
            }
        
        # Create dataframe from trade history
        df = pd.DataFrame(trade_history)
        df['timestamp'] = pd.to_datetime(df['sell_timestamp'])
        df = df.sort_values('timestamp')
        
        # Calculate cumulative P&L
        df['cumulative_pnl'] = df['pnl'].cumsum()
        
        # Create the figure
        fig = go.Figure()
        
        # Add the line
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['cumulative_pnl'],
            mode='lines+markers',
            name='P&L',
            line={'width': 3, 'color': '#00FF00'},
            marker={'size': 8, 'color': '#00FF00'}
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
                'title': None,
                'tickprefix': '₹'
            },
            hovermode='x unified'
        )
        
        return fig
    
    # Update P&L distribution chart
    @app.callback(
        Output("pnl-distribution-chart", "figure"),
        Input("interval-component", "n_intervals")
    )
    def update_pnl_distribution_chart(n):
        trade_history = trade_bot.get_trade_history()
        
        if not trade_history:
            return {
                'data': [],
                'layout': {
                    'paper_bgcolor': 'rgba(0,0,0,0)',
                    'plot_bgcolor': 'rgba(0,0,0,0)',
                    'xaxis': {'showgrid': False},
                    'yaxis': {'showgrid': False},
                    'annotations': [{
                        'text': 'No trade data available',
                        'xref': 'paper',
                        'yref': 'paper',
                        'showarrow': False,
                        'font': {'size': 20, 'color': 'white'}
                    }]
                }
            }
        
        # Create dataframe from trade history
        df = pd.DataFrame(trade_history)
        
        # Create the figure
        fig = px.histogram(
            df,
            x="pnl",
            color_discrete_sequence=['#00FF00'],
            opacity=0.8,
            marginal="box",
            histnorm="probability density"
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
                'title': "P&L (₹)"
            },
            yaxis={
                'showgrid': True,
                'gridcolor': '#444',
                'showline': True,
                'linecolor': '#444',
                'linewidth': 1,
                'title': "Frequency"
            },
            bargap=0.1
        )
        
        return fig
