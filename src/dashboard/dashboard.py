"""
Dashboard module for the ZeroBot application
"""
import logging
import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import dash_daq as daq
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import request, redirect

# Import page layouts
from src.dashboard.pages.trades import create_trades_layout, register_trades_callbacks
from src.dashboard.pages.strategies import create_strategies_layout, register_strategies_callbacks
from src.dashboard.pages.analytics import create_analytics_layout, register_analytics_callbacks
from src.dashboard.pages.settings import create_settings_layout, register_settings_callbacks

logger = logging.getLogger(__name__)

def create_dashboard(trade_bot):
    """Create the dashboard application"""
    # Initialize the Dash app
    app = dash.Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.CYBORG, 
            'https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap',
            'https://use.fontawesome.com/releases/v5.15.4/css/all.css'
        ],
        suppress_callback_exceptions=True,
        meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}]
    )
    
    # Set the title
    app.title = "ZeroBot - Automated Trading Bot"
    
    # Create the app layout
    app.layout = html.Div([
        # URL location component
        dcc.Location(id='url', refresh=False),
        
        # Page content
        html.Div(id='page-content'),
        
        # Interval component for refreshing data
        dcc.Interval(
            id='interval-component',
            interval=5000,  # 5 seconds
            n_intervals=0
        )
    ])
    
    # Login page
    login_layout = html.Div([
        html.Div([
            html.Div([
                html.Img(src='/assets/logo.svg', className='login-logo'),
                html.H1("ZeroBot", className='login-title'),
                html.H3("Automated Trading Bot", className='login-subtitle'),
                
                html.Div([
                    dbc.Button("Login with Zerodha", id='login-button', color='success', size='lg', className='login-button'),
                    dbc.Button("Demo Mode", id='demo-button', color='primary', size='lg', className='login-button ms-2'),
                    html.Div(id='login-status')
                ], className='login-form')
            ], className='login-container')
        ], className='login-page')
    ])
    
    # Main dashboard layout
    def create_main_layout():
        return html.Div([
            # Navbar
            dbc.Navbar(
                dbc.Container([
                    html.A(
                        dbc.Row([
                            dbc.Col(html.Img(src='/assets/logo.svg', height="40px")),
                            dbc.Col(dbc.NavbarBrand("ZeroBot", className="ms-2"))
                        ], align="center", className="g-0"),
                        href="/",
                        style={"textDecoration": "none"}
                    ),
                    dbc.NavbarToggler(id="navbar-toggler"),
                    dbc.Collapse(
                        dbc.Nav([
                            dbc.NavItem(dbc.NavLink([html.I(className="fas fa-chart-line me-2"), "Dashboard"], href="/")),
                            dbc.NavItem(dbc.NavLink([html.I(className="fas fa-exchange-alt me-2"), "Trades"], href="/trades")),
                            dbc.NavItem(dbc.NavLink([html.I(className="fas fa-brain me-2"), "Strategies"], href="/strategies")),
                            dbc.NavItem(dbc.NavLink([html.I(className="fas fa-chart-bar me-2"), "Analytics"], href="/analytics")),
                            dbc.NavItem(dbc.NavLink([html.I(className="fas fa-cog me-2"), "Settings"], href="/settings")),
                            dbc.NavItem(dbc.NavLink([html.I(className="fas fa-sign-out-alt me-2"), "Logout"], href="/logout"))
                        ], className="ms-auto", navbar=True),
                        id="navbar-collapse",
                        navbar=True
                    )
                ], fluid=True),
                color="dark",
                dark=True,
                className="mb-4"
            ),
            
            # Demo mode notice
            dbc.Alert(
                [
                    html.H4("Demo Mode Active", className="alert-heading"),
                    html.P(
                        "You are currently using ZeroBot in demo mode with simulated data. "
                        "To use real trading, please configure your Zerodha API credentials in the .env file."
                    ),
                ],
                color="info",
                dismissable=True,
                className="mb-4 mx-4"
            )
        ])
    
    # Home dashboard layout (overview)
    home_layout = dbc.Container([
        # Status and controls row
        dbc.Row([
            # Bot status card
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Bot Status"),
                    dbc.CardBody([
                        html.Div([
                            daq.PowerButton(
                                id='power-button',
                                on=False,
                                color='#00FF00',
                                size=48
                            ),
                            html.Div(id='bot-status-text', children="Stopped", className='ms-3')
                        ], className='d-flex align-items-center')
                    ])
                ], className='h-100')
            ], width=3),
            
            # Account info card
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Account Information"),
                    dbc.CardBody([
                        html.Div([
                            html.Div([
                                html.P("Available Margin", className='stat-label'),
                                html.H3(id='available-margin', children="₹0.00", className='stat-value')
                            ], className='stat-item'),
                            html.Div([
                                html.P("Used Margin", className='stat-label'),
                                html.H3(id='used-margin', children="₹0.00", className='stat-value')
                            ], className='stat-item'),
                            html.Div([
                                html.P("Active Trades", className='stat-label'),
                                html.H3(id='active-trades-count', children="0", className='stat-value')
                            ], className='stat-item')
                        ], className='d-flex justify-content-between')
                    ])
                ], className='h-100')
            ], width=9)
        ], className='mb-4'),
        
        # Performance metrics row
        dbc.Row([
            # P&L card
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Today's P&L"),
                    dbc.CardBody([
                        html.H2(id='today-pnl', children="₹0.00", className='metric-value'),
                        html.P(id='today-pnl-percent', children="0.00%", className='metric-change')
                    ], className='text-center')
                ], className='h-100 metric-card')
            ], width=3),
            
            # Win rate card
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Win Rate"),
                    dbc.CardBody([
                        html.H2(id='win-rate', children="0%", className='metric-value'),
                        html.P(id='win-rate-trades', children="0/0 trades", className='metric-change')
                    ], className='text-center')
                ], className='h-100 metric-card')
            ], width=3),
            
            # Avg profit card
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Avg. Profit"),
                    dbc.CardBody([
                        html.H2(id='avg-profit', children="₹0.00", className='metric-value'),
                        html.P(id='avg-profit-percent', children="0.00%", className='metric-change')
                    ], className='text-center')
                ], className='h-100 metric-card')
            ], width=3),
            
            # Avg loss card
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Avg. Loss"),
                    dbc.CardBody([
                        html.H2(id='avg-loss', children="₹0.00", className='metric-value'),
                        html.P(id='avg-loss-percent', children="0.00%", className='metric-change')
                    ], className='text-center')
                ], className='h-100 metric-card')
            ], width=3)
        ], className='mb-4'),
        
        # Charts row
        dbc.Row([
            # P&L chart
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("P&L History"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='pnl-chart',
                            config={'displayModeBar': False},
                            className='chart'
                        )
                    ])
                ], className='h-100')
            ], width=8),
            
            # Trade distribution
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Trade Distribution"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='trade-distribution',
                            config={'displayModeBar': False},
                            className='chart'
                        )
                    ])
                ], className='h-100')
            ], width=4)
        ], className='mb-4'),
        
        # Active trades table
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Span("Active Trades", className="h5"),
                        dbc.Button(
                            [html.I(className="fas fa-external-link-alt me-2"), "View All"],
                            href="/trades",
                            color="link",
                            size="sm",
                            className="float-end"
                        )
                    ]),
                    dbc.CardBody([
                        html.Div(id='active-trades-table')
                    ])
                ])
            ], width=12)
        ], className='mb-4'),
        
        # Trade history
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Span("Recent Trade History", className="h5"),
                        dbc.Button(
                            [html.I(className="fas fa-external-link-alt me-2"), "View All"],
                            href="/trades",
                            color="link",
                            size="sm",
                            className="float-end"
                        )
                    ]),
                    dbc.CardBody([
                        html.Div(id='trade-history-table')
                    ])
                ])
            ], width=12)
        ])
    ], fluid=True)
    
    # Route to different pages
    @app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname')
    )
    def display_page(pathname):
        if pathname == '/login/callback':
            # Handle Zerodha callback
            request_token = request.args.get('request_token')
            if request_token:
                success = trade_bot.login(request_token)
                if success:
                    return redirect('/')
            
            return login_layout
        
        elif pathname == '/login/demo-callback':
            # Handle demo login
            success = trade_bot.login("demo_token")
            if success:
                return redirect('/')
            
            return login_layout
        
        elif pathname == '/logout':
            # Handle logout
            # In a real app, you would clear the session
            return redirect('/login')
        
        elif trade_bot.is_authenticated():
            # Show appropriate page based on pathname
            main_layout = create_main_layout()
            
            if pathname == '/trades':
                page_content = create_trades_layout(trade_bot)
                return html.Div([main_layout, html.Div(page_content, id="page-layout")])
            elif pathname == '/strategies':
                page_content = create_strategies_layout(trade_bot)
                return html.Div([main_layout, html.Div(page_content, id="page-layout")])
            elif pathname == '/analytics':
                page_content = create_analytics_layout(trade_bot)
                return html.Div([main_layout, html.Div(page_content, id="page-layout")])
            elif pathname == '/settings':
                page_content = create_settings_layout(trade_bot)
                return html.Div([main_layout, html.Div(page_content, id="page-layout")])
            else:
                # Default to home dashboard
                return html.Div([main_layout, html.Div(home_layout, id="page-layout")])
        
        else:
            # Show login page if not authenticated
            return login_layout
    
    # Login button callback
    @app.callback(
        Output('login-status', 'children'),
        [Input('login-button', 'n_clicks'),
         Input('demo-button', 'n_clicks')],
        prevent_initial_call=True
    )
    def login_handler(login_clicks, demo_clicks):
        # Determine which button was clicked
        ctx = dash.callback_context
        if not ctx.triggered:
            return ""
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if button_id == 'login-button' and login_clicks:
            login_url = trade_bot.login()
            return html.Div([
                html.P("Redirecting to Zerodha login..."),
                dcc.Location(href=login_url, id='login-redirect')
            ])
        elif button_id == 'demo-button' and demo_clicks:
            return html.Div([
                html.P("Logging in to demo mode..."),
                dcc.Location(href='/login/demo-callback', id='demo-redirect')
            ])
        
        return ""
    
    # Power button callback
    @app.callback(
        [Output('bot-status-text', 'children'),
         Output('bot-status-text', 'className')],
        Input('power-button', 'on')
    )
    def toggle_bot(on):
        if on:
            success = trade_bot.start()
            if success:
                return "Running", "ms-3 text-success"
            else:
                return "Error", "ms-3 text-danger"
        else:
            trade_bot.stop()
            return "Stopped", "ms-3 text-danger"
    
    # Update account info
    @app.callback(
        [Output('available-margin', 'children'),
         Output('used-margin', 'children'),
         Output('active-trades-count', 'children')],
        Input('interval-component', 'n_intervals')
    )
    def update_account_info(n):
        # Get margin information
        margins = trade_bot.get_margins()
        
        if margins:
            available = margins['equity']['available']['cash']
            used = margins['equity']['utilised']['debits']
        else:
            available = 0
            used = 0
        
        # Get active trades count
        active_trades = len(trade_bot.get_active_trades())
        
        return f"₹{available:,.2f}", f"₹{used:,.2f}", str(active_trades)
    
    # Update performance metrics
    @app.callback(
        [Output('today-pnl', 'children'),
         Output('today-pnl-percent', 'className'),
         Output('today-pnl', 'className'),
         Output('win-rate', 'children'),
         Output('win-rate-trades', 'children'),
         Output('avg-profit', 'children'),
         Output('avg-profit-percent', 'children'),
         Output('avg-loss', 'children'),
         Output('avg-loss-percent', 'children')],
        Input('interval-component', 'n_intervals')
    )
    def update_metrics(n):
        # Get metrics
        metrics = trade_bot.get_metrics()
        
        # Calculate values
        net_pnl = metrics['net_pnl']
        pnl_percent = (net_pnl / trade_bot.capital) * 100 if trade_bot.capital > 0 else 0
        
        win_rate = metrics['win_rate']
        total_trades = metrics['total_trades']
        winning_trades = metrics['winning_trades']
        
        avg_profit = metrics['avg_profit']
        avg_profit_percent = (avg_profit / trade_bot.capital) * 100 if trade_bot.capital > 0 else 0
        
        avg_loss = metrics['avg_loss']
        avg_loss_percent = (avg_loss / trade_bot.capital) * 100 if trade_bot.capital > 0 else 0
        
        # Determine classes for styling
        pnl_class = 'metric-change text-success' if net_pnl >= 0 else 'metric-change text-danger'
        pnl_value_class = 'metric-value text-success' if net_pnl >= 0 else 'metric-value text-danger'
        
        return (
            f"₹{net_pnl:,.2f}",
            pnl_class,
            pnl_value_class,
            f"{win_rate:.2f}%",
            f"{winning_trades}/{total_trades} trades",
            f"₹{avg_profit:,.2f}",
            f"{avg_profit_percent:.2f}%",
            f"₹{avg_loss:,.2f}",
            f"{avg_loss_percent:.2f}%"
        )
    
    # Update P&L chart
    @app.callback(
        Output('pnl-chart', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def update_pnl_chart(n):
        # Get trade history
        trade_history = trade_bot.get_trade_history()
        
        if not trade_history:
            # Return empty chart if no trades
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
    
    # Update trade distribution chart
    @app.callback(
        Output('trade-distribution', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def update_trade_distribution(n):
        # Get metrics
        metrics = trade_bot.get_metrics()
        
        # Get values
        winning_trades = metrics['winning_trades']
        losing_trades = metrics['losing_trades']
        
        if winning_trades == 0 and losing_trades == 0:
            # Return empty chart if no trades
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
        
        # Create the figure
        fig = go.Figure()
        
        # Add the pie chart
        fig.add_trace(go.Pie(
            labels=['Winning Trades', 'Losing Trades'],
            values=[winning_trades, losing_trades],
            marker={'colors': ['#00FF00', '#FF0000']},
            textinfo='percent',
            hole=0.6
        ))
        
        # Update layout
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin={'l': 20, 'r': 20, 't': 20, 'b': 20},
            showlegend=True,
            legend={
                'orientation': 'h',
                'yanchor': 'bottom',
                'y': -0.2,
                'xanchor': 'center',
                'x': 0.5
            }
        )
        
        return fig
    
    # Update active trades table
    @app.callback(
        Output('active-trades-table', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_active_trades_table(n):
        # Get active trades
        active_trades = trade_bot.get_active_trades()
        
        if not active_trades:
            return html.P("No active trades", className='text-center text-muted my-3')
        
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
            pnl_class = 'text-success' if pnl >= 0 else 'text-danger'
            
            # Create row
            row = html.Tr([
                html.Td(f"{exchange}:{symbol}"),
                html.Td(f"{quantity}"),
                html.Td(f"₹{buy_price:.2f}"),
                html.Td(f"₹{current_price:.2f}"),
                html.Td(f"₹{pnl:.2f}", className=pnl_class),
                html.Td(f"{pnl_percent:.2f}%", className=pnl_class),
                html.Td(
                    dbc.Button("Close", color="danger", size="sm", id={'type': 'close-trade-button', 'index': order_id})
                )
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
                        html.Th("Action")
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
    
    # Update trade history table
    @app.callback(
        Output('trade-history-table', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_trade_history_table(n):
        # Get trade history
        trade_history = trade_bot.get_trade_history()
        
        if not trade_history:
            return html.P("No trade history", className='text-center text-muted my-3')
        
        # Create table rows
        rows = []
        for trade in trade_history[:5]:  # Only show the 5 most recent trades
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
            pnl_class = 'text-success' if pnl >= 0 else 'text-danger'
            
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
    
    # Register callbacks for each page
    register_trades_callbacks(app, trade_bot)
    register_strategies_callbacks(app, trade_bot)
    register_analytics_callbacks(app, trade_bot)
    register_settings_callbacks(app, trade_bot)
    
    return app
