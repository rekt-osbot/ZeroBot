"""
Settings page for the ZeroBot dashboard
"""
import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import json

def create_settings_layout(trade_bot):
    """Create the settings page layout"""
    layout = dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H2("Settings", className="mb-3"),
                html.P("Configure your ZeroBot trading parameters and preferences.", className="text-muted")
            ])
        ], className="mb-4"),
        
        # Settings Tabs
        dbc.Tabs([
            # General Settings Tab
            dbc.Tab([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Trading Parameters"),
                            dbc.CardBody([
                                dbc.Form([
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Label("Trading Capital (₹)", html_for="capital-input"),
                                            dbc.Input(
                                                type="number",
                                                id="capital-input",
                                                value=5000,
                                                min=1000,
                                                step=1000
                                            ),
                                            dbc.FormText("Minimum capital: ₹1,000")
                                        ], width=6),
                                        dbc.Col([
                                            dbc.Label("Minimum Trades", html_for="min-trades-input"),
                                            dbc.Input(
                                                type="number",
                                                id="min-trades-input",
                                                value=3,
                                                min=1,
                                                max=10
                                            ),
                                            dbc.FormText("Minimum number of simultaneous trades")
                                        ], width=6)
                                    ], className="mb-3"),
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Label("Maximum Trades", html_for="max-trades-input"),
                                            dbc.Input(
                                                type="number",
                                                id="max-trades-input",
                                                value=5,
                                                min=1,
                                                max=20
                                            ),
                                            dbc.FormText("Maximum number of simultaneous trades")
                                        ], width=6),
                                        dbc.Col([
                                            dbc.Label("Risk Per Trade (%)", html_for="risk-input"),
                                            dbc.Input(
                                                type="number",
                                                id="risk-input",
                                                value=2,
                                                min=0.1,
                                                max=10,
                                                step=0.1
                                            ),
                                            dbc.FormText("Percentage of capital to risk per trade")
                                        ], width=6)
                                    ], className="mb-3"),
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Label("Stop Loss (%)", html_for="stop-loss-input"),
                                            dbc.Input(
                                                type="number",
                                                id="stop-loss-input",
                                                value=1.5,
                                                min=0.1,
                                                max=10,
                                                step=0.1
                                            ),
                                            dbc.FormText("Percentage below entry price to set stop loss")
                                        ], width=6),
                                        dbc.Col([
                                            dbc.Label("Target Profit (%)", html_for="target-input"),
                                            dbc.Input(
                                                type="number",
                                                id="target-input",
                                                value=3,
                                                min=0.1,
                                                max=20,
                                                step=0.1
                                            ),
                                            dbc.FormText("Percentage above entry price to set target")
                                        ], width=6)
                                    ], className="mb-3"),
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Button("Save Trading Parameters", id="save-trading-params", color="primary")
                                        ], className="text-end")
                                    ])
                                ])
                            ])
                        ], className="mb-4"),
                        
                        dbc.Card([
                            dbc.CardHeader("Trading Schedule"),
                            dbc.CardBody([
                                dbc.Form([
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Label("Trading Days"),
                                            dbc.Checklist(
                                                options=[
                                                    {"label": "Monday", "value": "monday"},
                                                    {"label": "Tuesday", "value": "tuesday"},
                                                    {"label": "Wednesday", "value": "wednesday"},
                                                    {"label": "Thursday", "value": "thursday"},
                                                    {"label": "Friday", "value": "friday"}
                                                ],
                                                value=["monday", "tuesday", "wednesday", "thursday", "friday"],
                                                id="trading-days",
                                                inline=True
                                            )
                                        ])
                                    ], className="mb-3"),
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Label("Trading Start Time", html_for="start-time-input"),
                                            dbc.Input(
                                                type="time",
                                                id="start-time-input",
                                                value="09:15"
                                            )
                                        ], width=6),
                                        dbc.Col([
                                            dbc.Label("Trading End Time", html_for="end-time-input"),
                                            dbc.Input(
                                                type="time",
                                                id="end-time-input",
                                                value="15:30"
                                            )
                                        ], width=6)
                                    ], className="mb-3"),
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Label("Auto Close Positions at End of Day"),
                                            dbc.Switch(
                                                id="auto-close-switch",
                                                value=True,
                                                label="Enabled"
                                            )
                                        ], width=6)
                                    ], className="mb-3"),
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Button("Save Schedule Settings", id="save-schedule", color="primary")
                                        ], className="text-end")
                                    ])
                                ])
                            ])
                        ])
                    ], width=8),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Application Settings"),
                            dbc.CardBody([
                                dbc.Form([
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Label("Theme"),
                                            dbc.RadioItems(
                                                options=[
                                                    {"label": "Dark", "value": "dark"},
                                                    {"label": "Light", "value": "light"}
                                                ],
                                                value="dark",
                                                id="theme-selection",
                                                inline=True
                                            )
                                        ])
                                    ], className="mb-3"),
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Label("Data Refresh Interval (seconds)", html_for="refresh-interval-input"),
                                            dbc.Input(
                                                type="number",
                                                id="refresh-interval-input",
                                                value=5,
                                                min=1,
                                                max=60
                                            )
                                        ])
                                    ], className="mb-3"),
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Label("Notifications"),
                                            dbc.Checklist(
                                                options=[
                                                    {"label": "Trade Execution", "value": "trade_exec"},
                                                    {"label": "Stop Loss Hit", "value": "stop_loss"},
                                                    {"label": "Target Reached", "value": "target"},
                                                    {"label": "Error Alerts", "value": "error"}
                                                ],
                                                value=["trade_exec", "stop_loss", "target", "error"],
                                                id="notification-settings"
                                            )
                                        ])
                                    ], className="mb-3"),
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Button("Save App Settings", id="save-app-settings", color="primary")
                                        ], className="text-end")
                                    ])
                                ])
                            ])
                        ], className="mb-4"),
                        
                        dbc.Card([
                            dbc.CardHeader("Debug Settings"),
                            dbc.CardBody([
                                dbc.Form([
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Label("Logging Level"),
                                            dbc.Select(
                                                id="log-level-select",
                                                options=[
                                                    {"label": "Debug", "value": "DEBUG"},
                                                    {"label": "Info", "value": "INFO"},
                                                    {"label": "Warning", "value": "WARNING"},
                                                    {"label": "Error", "value": "ERROR"},
                                                    {"label": "Critical", "value": "CRITICAL"}
                                                ],
                                                value="INFO"
                                            )
                                        ])
                                    ], className="mb-3"),
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Label("Demo Mode"),
                                            dbc.Switch(
                                                id="demo-mode-switch",
                                                value=True,
                                                label="Enabled"
                                            ),
                                            dbc.FormText("Use simulated data instead of real trading")
                                        ])
                                    ], className="mb-3"),
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Button("Save Debug Settings", id="save-debug-settings", color="primary")
                                        ], className="text-end")
                                    ])
                                ])
                            ])
                        ])
                    ], width=4)
                ])
            ], label="General", tab_id="general-settings"),
            
            # API Settings Tab
            dbc.Tab([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Zerodha API Credentials"),
                            dbc.CardBody([
                                dbc.Alert([
                                    html.H6("⚠️ Security Warning", className="alert-heading"),
                                    html.P([
                                        "For security reasons, it's recommended to set API credentials using environment variables in a ",
                                        html.Code(".env"), " file instead of entering them here. ",
                                        "This form is provided for testing purposes only."
                                    ]),
                                    html.P([
                                        "To use environment variables, create a ", html.Code(".env"), " file in your project root with:",
                                        html.Br(),
                                        html.Code("API_KEY=your_api_key_here"),
                                        html.Br(),
                                        html.Code("API_SECRET=your_api_secret_here")
                                    ])
                                ], color="warning", className="mb-3"),
                                dbc.Form([
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Label("API Key", html_for="api-key-input"),
                                            dbc.Input(
                                                type="password",
                                                id="api-key-input",
                                                placeholder="Enter your Zerodha API Key"
                                            )
                                        ])
                                    ], className="mb-3"),
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Label("API Secret", html_for="api-secret-input"),
                                            dbc.Input(
                                                type="password",
                                                id="api-secret-input",
                                                placeholder="Enter your Zerodha API Secret"
                                            )
                                        ])
                                    ], className="mb-3"),
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Label("Redirect URL", html_for="redirect-url-input"),
                                            dbc.Input(
                                                type="text",
                                                id="redirect-url-input",
                                                value="http://localhost:8000/login/callback"
                                            ),
                                            dbc.FormText("Must match the redirect URL configured in your Zerodha developer account")
                                        ])
                                    ], className="mb-3"),
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Button("Save API Credentials", id="save-api-credentials", color="primary")
                                        ], className="text-end")
                                    ])
                                ])
                            ])
                        ], className="mb-4"),
                        
                        dbc.Card([
                            dbc.CardHeader("API Connection Status"),
                            dbc.CardBody([
                                html.Div(id="api-status", children=[
                                    html.H4([
                                        html.I(className="fas fa-circle text-success me-2"),
                                        "Connected (Demo Mode)"
                                    ]),
                                    html.P("Using simulated data for testing", className="text-muted")
                                ])
                            ])
                        ], className="mb-4"),
                        
                        dbc.Card([
                            dbc.CardHeader("API Documentation"),
                            dbc.CardBody([
                                html.P([
                                    "For detailed information on the Zerodha KiteConnect API, please refer to the ",
                                    html.A("official documentation", href="https://kite.trade/docs/connect/v3/", target="_blank"),
                                    "."
                                ]),
                                html.P([
                                    "To create API credentials, visit the ",
                                    html.A("Zerodha Developer Console", href="https://developers.kite.trade/", target="_blank"),
                                    "."
                                ])
                            ])
                        ])
                    ], width=8),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("API Usage"),
                            dbc.CardBody([
                                html.Div([
                                    html.H5("Rate Limits"),
                                    html.P("Zerodha API has the following rate limits:"),
                                    html.Ul([
                                        html.Li("3 requests per second"),
                                        html.Li("300 requests per minute"),
                                        html.Li("1 order per second")
                                    ]),
                                    html.Hr(),
                                    html.H5("Current Usage"),
                                    dbc.Progress(value=15, color="success", className="mb-3", style={"height": "8px"}),
                                    html.P("45/300 requests used (15%)", className="text-muted")
                                ])
                            ])
                        ], className="mb-4"),
                        
                        dbc.Card([
                            dbc.CardHeader("API Testing"),
                            dbc.CardBody([
                                dbc.Button("Test API Connection", id="test-api-connection", color="primary", className="mb-3"),
                                html.Div(id="api-test-result")
                            ])
                        ])
                    ], width=4)
                ])
            ], label="API Settings", tab_id="api-settings"),
            
            # Backup & Restore Tab
            dbc.Tab([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Backup Settings"),
                            dbc.CardBody([
                                dbc.Form([
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Button("Export Settings", id="export-settings", color="primary", className="me-2"),
                                            dbc.Button("Export Trade History", id="export-trades", color="secondary")
                                        ])
                                    ], className="mb-3"),
                                    dbc.Row([
                                        dbc.Col([
                                            html.P("Last Backup: Never", id="last-backup-time", className="text-muted")
                                        ])
                                    ])
                                ])
                            ])
                        ], className="mb-4"),
                        
                        dbc.Card([
                            dbc.CardHeader("Restore Settings"),
                            dbc.CardBody([
                                dbc.Form([
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Label("Import Settings File"),
                                            dcc.Upload(
                                                id="upload-settings",
                                                children=html.Div([
                                                    "Drag and Drop or ",
                                                    html.A("Select a Settings File")
                                                ]),
                                                style={
                                                    "width": "100%",
                                                    "height": "60px",
                                                    "lineHeight": "60px",
                                                    "borderWidth": "1px",
                                                    "borderStyle": "dashed",
                                                    "borderRadius": "5px",
                                                    "textAlign": "center",
                                                    "margin": "10px 0"
                                                }
                                            )
                                        ])
                                    ], className="mb-3"),
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Button("Restore Settings", id="restore-settings", color="warning")
                                        ], className="text-end")
                                    ])
                                ])
                            ])
                        ], className="mb-4"),
                        
                        dbc.Card([
                            dbc.CardHeader("Reset to Default"),
                            dbc.CardBody([
                                html.P("This will reset all settings to their default values. This action cannot be undone."),
                                dbc.Button("Reset All Settings", id="reset-settings", color="danger")
                            ])
                        ])
                    ], width=8),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Data Management"),
                            dbc.CardBody([
                                html.H5("Database Statistics"),
                                html.Ul([
                                    html.Li("Trade Records: 128"),
                                    html.Li("Strategy Configurations: 5"),
                                    html.Li("Performance Metrics: 90 days"),
                                    html.Li("Database Size: 2.4 MB")
                                ], className="mb-3"),
                                html.Hr(),
                                html.H5("Data Cleanup"),
                                dbc.Form([
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Label("Delete Data Older Than"),
                                            dbc.Select(
                                                id="data-retention-select",
                                                options=[
                                                    {"label": "1 month", "value": "1m"},
                                                    {"label": "3 months", "value": "3m"},
                                                    {"label": "6 months", "value": "6m"},
                                                    {"label": "1 year", "value": "1y"},
                                                    {"label": "All time", "value": "all"}
                                                ],
                                                value="all"
                                            )
                                        ])
                                    ], className="mb-3"),
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Button("Clean Up Data", id="cleanup-data", color="warning")
                                        ], className="text-end")
                                    ])
                                ])
                            ])
                        ])
                    ], width=4)
                ])
            ], label="Backup & Restore", tab_id="backup-restore"),
            
            # About Tab
            dbc.Tab([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("About ZeroBot"),
                            dbc.CardBody([
                                html.Div([
                                    html.Img(src="/assets/logo.svg", height="100px", className="mb-3"),
                                    html.H3("ZeroBot v1.0.0", className="mb-3"),
                                    html.P("ZeroBot is an automated trading bot for Zerodha that executes intraday trades on NSE and BSE markets."),
                                    html.P([
                                        "Built with ❤️ using ",
                                        html.A("Python", href="https://www.python.org/", target="_blank"),
                                        ", ",
                                        html.A("Dash", href="https://dash.plotly.com/", target="_blank"),
                                        ", and ",
                                        html.A("KiteConnect", href="https://kite.trade/docs/connect/v3/", target="_blank")
                                    ]),
                                    html.Hr(),
                                    html.H5("System Information"),
                                    html.Ul([
                                        html.Li(f"Python Version: 3.10.0"),
                                        html.Li(f"Dash Version: 2.10.0"),
                                        html.Li(f"KiteConnect Version: 4.1.0"),
                                        html.Li(f"Operating System: Windows 10")
                                    ])
                                ], className="text-center")
                            ])
                        ], className="mb-4"),
                        
                        dbc.Card([
                            dbc.CardHeader("Disclaimer"),
                            dbc.CardBody([
                                html.P([
                                    "Trading in financial markets involves risk. This bot is provided for educational and informational purposes only. ",
                                    "Always use proper risk management and never invest money you cannot afford to lose."
                                ], className="mb-3"),
                                html.P([
                                    "ZeroBot is not affiliated with Zerodha. Zerodha and KiteConnect are trademarks of Zerodha Broking Ltd."
                                ])
                            ])
                        ])
                    ], width=8),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("License"),
                            dbc.CardBody([
                                html.P("MIT License"),
                                html.P([
                                    "Copyright (c) 2025",
                                    html.Br(),
                                    html.Br(),
                                    "Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the \"Software\"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:",
                                    html.Br(),
                                    html.Br(),
                                    "The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software."
                                ], style={"fontSize": "0.8rem"})
                            ])
                        ], className="mb-4"),
                        
                        dbc.Card([
                            dbc.CardHeader("Support"),
                            dbc.CardBody([
                                html.P("If you encounter any issues or have questions, please reach out for support:"),
                                html.Ul([
                                    html.Li([
                                        html.I(className="fas fa-envelope me-2"),
                                        "Email: support@zerobot.example.com"
                                    ]),
                                    html.Li([
                                        html.I(className="fab fa-github me-2"),
                                        html.A("GitHub Repository", href="https://github.com/example/zerobot", target="_blank")
                                    ]),
                                    html.Li([
                                        html.I(className="fas fa-book me-2"),
                                        html.A("Documentation", href="#", target="_blank")
                                    ])
                                ])
                            ])
                        ])
                    ], width=4)
                ])
            ], label="About", tab_id="about")
        ], id="settings-tabs", active_tab="general-settings")
    ], fluid=True)
    
    return layout

def register_settings_callbacks(app, trade_bot):
    """Register callbacks for the settings page"""
    
    # Save Trading Parameters
    @app.callback(
        Output("save-trading-params", "children"),
        [Input("save-trading-params", "n_clicks")],
        [State("capital-input", "value"),
         State("min-trades-input", "value"),
         State("max-trades-input", "value"),
         State("risk-input", "value"),
         State("stop-loss-input", "value"),
         State("target-input", "value")]
    )
    def save_trading_parameters(n_clicks, capital, min_trades, max_trades, risk, stop_loss, target):
        if not n_clicks:
            return "Save Trading Parameters"
        
        # In a real app, you would save these to a config file or database
        # For now, we'll just update the trade_bot object
        trade_bot.capital = capital
        trade_bot.min_trades = min_trades
        trade_bot.max_trades = max_trades
        trade_bot.risk_per_trade = risk / 100  # Convert to decimal
        trade_bot.stop_loss_percent = stop_loss / 100  # Convert to decimal
        trade_bot.target_percent = target / 100  # Convert to decimal
        
        # Return a success message that will be shown briefly
        return "✓ Saved!"
    
    # Test API Connection
    @app.callback(
        Output("api-test-result", "children"),
        Input("test-api-connection", "n_clicks")
    )
    def test_api_connection(n_clicks):
        if not n_clicks:
            return ""
        
        # In a real app, you would test the API connection
        # For now, we'll just return a success message
        return html.Div([
            html.I(className="fas fa-check-circle text-success me-2"),
            "Connection successful! (Demo Mode)"
        ], className="mt-2")
    
    # Export Settings
    @app.callback(
        Output("last-backup-time", "children"),
        Input("export-settings", "n_clicks")
    )
    def export_settings(n_clicks):
        if not n_clicks:
            return "Last Backup: Never"
        
        # In a real app, you would export the settings to a file
        # For now, we'll just update the last backup time
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"Last Backup: {now}"
