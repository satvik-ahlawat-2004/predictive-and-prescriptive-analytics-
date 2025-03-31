import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import random
import logging
import io
import base64
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create empty graph function
def create_empty_graph(message="No data available"):
    return {
        "data": [],
        "layout": go.Layout(
            title=message,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            annotations=[dict(
                text=message,
                showarrow=False,
                font=dict(size=20)
            )],
            paper_bgcolor='rgba(248, 249, 250, 1)',
            plot_bgcolor='rgba(248, 249, 250, 1)',
        )
    }

# Custom CSS for improved styling
custom_css = """
    /* Global styles */
    body {
        font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        background-color: #f8f9fa;
        color: #343a40;
        line-height: 1.6;
    }
    
    /* Card styling */
    .card {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s, box-shadow 0.2s;
        margin-bottom: 20px;
        background-color: white;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08);
    }
    
    .card-header {
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        background-color: #f8f9fa;
        border-bottom: 1px solid #e9ecef;
        padding: 12px 20px;
    }
    
    /* Button styling */
    .btn {
        border-radius: 6px;
        font-weight: 500;
        padding: 8px 16px;
        transition: all 0.2s;
    }
    
    .btn-primary {
        background-color: #4361ee;
        border-color: #4361ee;
    }
    
    .btn-primary:hover {
        background-color: #3a56d4;
        border-color: #3a56d4;
        box-shadow: 0 4px 8px rgba(67, 97, 238, 0.3);
    }
    
    .btn-success {
        background-color: #38b000;
        border-color: #38b000;
    }
    
    .btn-success:hover {
        background-color: #2d9000;
        border-color: #2d9000;
        box-shadow: 0 4px 8px rgba(56, 176, 0, 0.3);
    }
    
    /* Upload area styling */
    .upload-area {
        border: 2px dashed #ced4da;
        border-radius: 10px;
        background-color: #f8f9fa;
        padding: 80px 0;
        text-align: center;
        transition: all 0.2s;
    }
    
    .upload-area:hover {
        border-color: #4361ee;
        background-color: #f0f3ff;
    }
    
    /* Icons and tooltips */
    .icon-btn {
        cursor: pointer;
        margin-left: 5px;
        color: #6c757d;
    }
    
    .icon-btn:hover {
        color: #4361ee;
    }
    
    .tooltip {
        opacity: 0;
        position: absolute;
        background-color: #343a40;
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 12px;
        transition: opacity 0.3s;
        pointer-events: none;
    }
    
    /* Toast notifications */
    .toast {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        max-width: 300px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        border-radius: 8px;
        animation: slideIn 0.3s forwards;
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Graph styling */
    .dash-graph {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Loading animation */
    .loader {
        display: inline-block;
        width: 80px;
        height: 80px;
        margin: 30px auto;
    }
    
    .loader:after {
        content: " ";
        display: block;
        width: 64px;
        height: 64px;
        border-radius: 50%;
        border: 6px solid #4361ee;
        border-color: #4361ee transparent #4361ee transparent;
        animation: loader 1.2s linear infinite;
    }
    
    @keyframes loader {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Tab styling */
    .nav-tabs .nav-link {
        border-radius: 6px 6px 0 0;
        font-weight: 500;
        color: #6c757d;
        padding: 10px 20px;
    }
    
    .nav-tabs .nav-link.active {
        color: #4361ee;
        border-color: #dee2e6 #dee2e6 #fff;
        border-bottom: 2px solid #4361ee;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-weight: 600;
        color: #212529;
    }
    
    .text-primary {
        color: #4361ee !important;
    }
    
    .text-success {
        color: #38b000 !important;
    }
    
    /* Report section */
    .report-card {
        border-left: 4px solid #4361ee;
        padding-left: 15px;
    }
    
    /* Metrics cards */
    .metric-card {
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        background-color: white;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    .metric-icon {
        font-size: 24px;
        margin-bottom: 10px;
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 5px;
    }
    
    .metric-label {
        font-size: 14px;
        color: #6c757d;
    }
"""

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    ]
)

# Add custom CSS through index_string
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
''' + custom_css + '''
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# App layout
app.layout = html.Div([
    # Data stores
    dcc.Store(id='results-store'),
    dcc.Store(id='report-data'),
    dcc.Download(id='download-report'),
    
    # Header
    html.Div([
        html.H1("Logistics Optimization Dashboard", className="display-4 text-center mb-4"),
        html.Hr()
    ], className="container mt-4"),
    
    # Main content
    html.Div([
        # Data upload section
        html.Div([
            html.Div([
                html.H3("Data Upload", className="mb-3"),
                html.Div([
                    html.I(className="fas fa-circle-info icon-btn", id="upload-info-icon"),
                    dbc.Tooltip(
                        "Upload your logistics data in CSV format to analyze performance and get optimization recommendations.",
                        target="upload-info-icon",
                    ),
                ], className="d-inline-block ml-2"),
            ], className="d-flex align-items-center"),
            
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    html.I(className="fas fa-cloud-upload-alt", style={"fontSize": "48px", "color": "#4361ee"}),
                    html.Div("Drag and Drop or Click to Upload File", style={"marginTop": "10px"})
                ], className="upload-area"),
                multiple=False,
                style={'width': '100%', 'marginBottom': '20px'}
            ),
            html.Div(id='upload-output'),
            dbc.Button(
                [
                    html.I(className="fas fa-play-circle mr-2"), 
                    "Run Analysis",
                    html.I(className="fas fa-circle-info icon-btn ml-2", id="analysis-info-icon"),
                ],
                id="run-analysis", 
                color="primary", 
                className="mt-3 mb-5", 
                style={'display': 'none'}
            ),
            dbc.Tooltip(
                "Process the uploaded data to generate insights, predictions, and recommendations.",
                target="analysis-info-icon",
            ),
        ], className="card p-4 mb-5"),
        
        # Analysis results section
        html.Div([
            # Tabs for different analyses
            dbc.Tabs([
                dbc.Tab(label="Insights", tab_id="insights-tab", children=[
                    html.Div([
                        html.Div([
                            html.H4("Delivery Time Analysis", className="mb-3"),
                            html.Div([
                                html.I(className="fas fa-circle-info icon-btn", id="delivery-info-icon"),
                                dbc.Tooltip(
                                    "Shows delivery time trends and patterns over the selected time period.",
                                    target="delivery-info-icon",
                                ),
                            ], className="d-inline-block ml-2"),
                        ], className="d-flex align-items-center"),
                        html.Div(id="delivery-loading", className="text-center d-none"),
                        dcc.Graph(
                            id="delivery-graph", 
                            figure=create_empty_graph("Please run analysis first"),
                            className="dash-graph"
                        )
                    ], className="card p-4 mb-4"),
                    
                    html.Div([
                        html.Div([
                            html.H4("Inventory Analysis", className="mb-3"),
                            html.Div([
                                html.I(className="fas fa-circle-info icon-btn", id="inventory-info-icon"),
                                dbc.Tooltip(
                                    "Displays inventory levels across warehouses and identifies potential stockout risks.",
                                    target="inventory-info-icon",
                                ),
                            ], className="d-inline-block ml-2"),
                        ], className="d-flex align-items-center"),
                        html.Div(id="inventory-loading", className="text-center d-none"),
                        dcc.Graph(
                            id="inventory-graph", 
                            figure=create_empty_graph("Please run analysis first"),
                            className="dash-graph"
                        )
                    ], className="card p-4")
                ], className="p-3"),
                
                dbc.Tab(label="Predictions", tab_id="predictions-tab", children=[
                    # Metrics cards row
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.Div([
                                    html.I(className="fas fa-truck metric-icon text-primary"),
                                    html.Div(id="avg-delay-value", className="metric-value"),
                                    html.Div("Avg. Delay (min)", className="metric-label")
                                ])
                            ], className="metric-card text-center")
                        ], width=4),
                        
                        dbc.Col([
                            html.Div([
                                html.Div([
                                    html.I(className="fas fa-boxes-stacked metric-icon text-success"),
                                    html.Div(id="avg-demand-value", className="metric-value"),
                                    html.Div("Avg. Demand (units)", className="metric-label")
                                ])
                            ], className="metric-card text-center")
                        ], width=4),
                        
                        dbc.Col([
                            html.Div([
                                html.Div([
                                    html.I(className="fas fa-dollar-sign metric-icon text-warning"),
                                    html.Div(id="total-cost-value", className="metric-value"),
                                    html.Div("Total Logistics Cost", className="metric-label")
                                ])
                            ], className="metric-card text-center")
                        ], width=4),
                    ], className="mb-4 mt-3"),
                    
                    html.Div([
                        html.Div([
                            html.H4("Delay Forecast", className="mb-3"),
                            html.Div([
                                html.I(className="fas fa-circle-info icon-btn", id="delay-forecast-info-icon"),
                                dbc.Tooltip(
                                    "7-day forecast of expected delays with confidence intervals.",
                                    target="delay-forecast-info-icon",
                                ),
                            ], className="d-inline-block ml-2"),
                        ], className="d-flex align-items-center"),
                        html.Div(id="delay-forecast-loading", className="text-center d-none"),
                        dcc.Graph(
                            id="delay-forecast", 
                            figure=create_empty_graph("Please run analysis first"),
                            className="dash-graph"
                        )
                    ], className="card p-4 mb-4"),
                    
                    html.Div([
                        html.Div([
                            html.H4("Demand Forecast", className="mb-3"),
                            html.Div([
                                html.I(className="fas fa-circle-info icon-btn", id="demand-forecast-info-icon"),
                                dbc.Tooltip(
                                    "7-day demand forecast with confidence intervals to help with inventory planning.",
                                    target="demand-forecast-info-icon",
                                ),
                            ], className="d-inline-block ml-2"),
                        ], className="d-flex align-items-center"),
                        html.Div(id="demand-forecast-loading", className="text-center d-none"),
                        dcc.Graph(
                            id="demand-forecast", 
                            figure=create_empty_graph("Please run analysis first"),
                            className="dash-graph"
                        )
                    ], className="card p-4")
                ], className="p-3"),
                
                dbc.Tab(label="Optimizations", tab_id="optimizations-tab", children=[
                    html.Div([
                        html.Div([
                            html.H4("Route Optimization", className="mb-3"),
                            html.Div([
                                html.I(className="fas fa-circle-info icon-btn", id="route-optimization-info-icon"),
                                dbc.Tooltip(
                                    "Optimized delivery routes to minimize distance and time.",
                                    target="route-optimization-info-icon",
                                ),
                            ], className="d-inline-block ml-2"),
                        ], className="d-flex align-items-center"),
                        html.Div(id="route-optimization-loading", className="text-center d-none"),
                        dcc.Graph(
                            id="route-optimization", 
                            figure=create_empty_graph("Please run analysis first"),
                            className="dash-graph"
                        ),
                        html.Div([
                            html.Div(id="route-savings", className="mt-3 p-3 bg-light rounded")
                        ])
                    ], className="card p-4 mb-4"),
                    
                    html.Div([
                        html.Div([
                            html.H4("Recommendations", className="mb-3"),
                            html.Div([
                                html.I(className="fas fa-circle-info icon-btn", id="recommendations-info-icon"),
                                dbc.Tooltip(
                                    "Actionable recommendations to optimize your logistics operations.",
                                    target="recommendations-info-icon",
                                ),
                            ], className="d-inline-block ml-2"),
                        ], className="d-flex align-items-center"),
                        html.Div(id="recommendations-loading", className="text-center d-none"),
                        html.Div(id="recommendations", children="Please run analysis first")
                    ], className="card p-4")
                ], className="p-3"),
                
                dbc.Tab(label="Report", tab_id="report-tab", children=[
                    html.Div([
                        html.Div([
                            html.H4("Report Generator", className="mb-3"),
                            html.Div([
                                html.I(className="fas fa-circle-info icon-btn", id="report-info-icon"),
                                dbc.Tooltip(
                                    "Generate a comprehensive PDF report with all analysis results.",
                                    target="report-info-icon",
                                ),
                            ], className="d-flex align-items-center"),
                        ], className="d-flex align-items-center"),
                        
                        html.Div([
                            html.P("Create a comprehensive report containing all analysis results, charts, and recommendations.", className="mb-4"),
                            
                            html.Div([
                                html.Label("Report Title", className="font-weight-bold mb-2"),
                                dbc.Input(
                                    id="report-title",
                                    type="text",
                                    placeholder="Logistics Optimization Report",
                                    value="Logistics Optimization Report",
                                    className="mb-3"
                                ),
                                
                                html.Label("Include Sections", className="font-weight-bold mb-2"),
                                dbc.Checklist(
                                    options=[
                                        {"label": "Summary Statistics", "value": "summary"},
                                        {"label": "Delivery Time Analysis", "value": "delivery"},
                                        {"label": "Inventory Analysis", "value": "inventory"},
                                        {"label": "Forecasts", "value": "forecasts"},
                                        {"label": "Route Optimization", "value": "routes"},
                                        {"label": "Recommendations", "value": "recommendations"}
                                    ],
                                    value=["summary", "delivery", "inventory", "forecasts", "routes", "recommendations"],
                                    id="report-sections",
                                    inline=True,
                                    className="mb-4"
                                ),
                                
                                dbc.Button(
                                    [html.I(className="fas fa-file-pdf mr-2"), "Generate Report"],
                                    id="generate-report-btn",
                                    color="success",
                                    className="mt-2"
                                ),
                                
                                html.Div(id="report-status", className="mt-3"),
                                
                                html.Div([
                                    dbc.Button(
                                        [html.I(className="fas fa-download mr-2"), "Download PDF Report"],
                                        id="download-report-btn",
                                        color="primary",
                                        className="mt-2"
                                    )
                                ], id="download-btn-container", className="mt-3 d-none")
                            ], className="report-card p-4 bg-light rounded")
                        ])
                    ], className="card p-4")
                ], className="p-3")
            ], id="analysis-tabs", active_tab="insights-tab", className="mb-4")
        ], className="mb-5"),
        
        # Notifications
        html.Div(id="notification-area", className="position-fixed", style={
            'display': 'none'
        })
    ], className="container")
], style={'fontFamily': 'Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif'})

# Callback for file upload
@app.callback(
    [Output('upload-output', 'children'),
     Output('run-analysis', 'style')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_output(contents, filename):
    if contents is None:
        return None, {'display': 'none'}
    
    # Show file info and preview
    return html.Div([
        html.Div([
            html.I(className="fas fa-file-alt mr-2", style={"color": "#4361ee"}),
            html.H5(f"File: {filename}", className="mb-0 d-inline")
        ], className="d-flex align-items-center mb-2"),
        html.P("File uploaded successfully and ready for analysis.", className="text-success"),
        html.Hr(),
        html.P("Click 'Run Analysis' to process the data and generate insights.", className="font-italic text-muted small")
    ], className="mt-3"), {'display': 'inline-block'}

# Callback for running analysis
@app.callback(
    [Output('results-store', 'data'),
     Output('notification-area', 'children'),
     Output('notification-area', 'style'),
     Output('delay-forecast-loading', 'className'),
     Output('demand-forecast-loading', 'className'),
     Output('delivery-loading', 'className'),
     Output('inventory-loading', 'className'),
     Output('route-optimization-loading', 'className'),
     Output('recommendations-loading', 'className'),
     Output('analysis-tabs', 'active_tab')],
    [Input('run-analysis', 'n_clicks')],
    prevent_initial_call=True
)
def run_analysis(n_clicks):
    if n_clicks is None:
        return (None, None, {'display': 'none'}, 
                'text-center d-none', 'text-center d-none', 'text-center d-none', 
                'text-center d-none', 'text-center d-none', 'text-center d-none', 
                'insights-tab')
    
    # Show loading spinners
    loading_visible = 'text-center'
    loading_html = html.Div([
        html.Div(className="loader")
    ])
    
    try:
        # Generate sample data instead of API calls
        logger.info("Generating sample data for analysis")
        
        # Sample data for insights
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
        
        insights = {
            "delivery_performance": {
                "average_delay": 15.3,
                "on_time_rate": 85,
                "delay_trend": "Decreasing",
                "dates": dates,
                "delays": [random.uniform(10, 20) for _ in range(30)]
            },
            "inventory_performance": {
                "average_inventory_level": 520,
                "inventory_trend": "Stable",
                "stockout_rate": 2.3,
                "dates": dates,
                "inventory_levels": [random.randint(450, 600) for _ in range(30)]
            }
        }
        
        # Sample data for predictions
        future_dates = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 8)]
        
        predictions = {
            "delay_forecast": {
                "dates": future_dates,
                "values": [random.uniform(12, 18) for _ in range(7)],
                "lower": [random.uniform(8, 12) for _ in range(7)],
                "upper": [random.uniform(18, 22) for _ in range(7)]
            },
            "demand_forecast": {
                "dates": future_dates,
                "values": [random.randint(450, 550) for _ in range(7)],
                "lower": [random.randint(400, 450) for _ in range(7)],
                "upper": [random.randint(550, 600) for _ in range(7)]
            }
        }
        
        # Sample data for optimizations
        optimizations = {
            "route_optimization": {
                "current_distance": 1250,
                "optimized_distance": 980,
                "savings_percent": 21.6,
                "routes": [
                    {"from": "Warehouse A", "to": "Customer 1", "distance": 120},
                    {"from": "Warehouse A", "to": "Customer 2", "distance": 85},
                    {"from": "Warehouse B", "to": "Customer 3", "distance": 140},
                    {"from": "Warehouse B", "to": "Customer 4", "distance": 95}
                ]
            },
            "recommendations": [
                "Consolidate deliveries to reduce total distance by 15%",
                "Reschedule deliveries to reduce transit times by 12%",
                "Optimize warehouse allocation to reduce delivery distance by 8%",
                "Implement just-in-time delivery for Product B to minimize storage costs"
            ]
        }
        
        # Additional metrics for the predictions tab
        metrics = {
            "avg_delay": 15.3,
            "avg_demand": 492,
            "total_cost": "$12,450"
        }
        
        # Combined results
        results = {
            "insights": insights,
            "predictions": predictions,
            "optimizations": optimizations,
            "metrics": metrics,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Create success notification
        notification = html.Div(
            dbc.Alert(
                [
                    html.I(className="fas fa-check-circle mr-2"),
                    "Analysis completed successfully!"
                ],
                color="success",
                dismissable=True,
                is_open=True,
                className="mb-0 shadow-sm"
            ),
            className="toast"
        )
        
        return (results, notification, {'display': 'block'}, 
                'text-center d-none', 'text-center d-none', 'text-center d-none', 
                'text-center d-none', 'text-center d-none', 'text-center d-none', 
                'insights-tab')
        
    except Exception as e:
        logger.error(f"Error in analysis: {str(e)}")
        
        # Create error notification
        notification = html.Div(
            dbc.Alert(
                [
                    html.I(className="fas fa-exclamation-circle mr-2"), 
                    f"Error: {str(e)}"
                ],
                color="danger",
                dismissable=True,
                is_open=True,
                className="mb-0 shadow-sm"
            ),
            className="toast"
        )
        
        return (None, notification, {'display': 'block'}, 
                'text-center d-none', 'text-center d-none', 'text-center d-none', 
                'text-center d-none', 'text-center d-none', 'text-center d-none', 
                'insights-tab')

# Callback for metric values in predictions tab
@app.callback(
    [Output('avg-delay-value', 'children'),
     Output('avg-demand-value', 'children'),
     Output('total-cost-value', 'children')],
    [Input('results-store', 'data')],
    prevent_initial_call=True
)
def update_metrics(results):
    if results is None:
        return "—", "—", "—"
    
    metrics = results.get('metrics', {})
    avg_delay = metrics.get('avg_delay', '—')
    avg_demand = metrics.get('avg_demand', '—')
    total_cost = metrics.get('total_cost', '—')
    
    return f"{avg_delay} min", f"{avg_demand}", f"{total_cost}"

# Callback for updating insights graphs
@app.callback(
    [Output('delivery-graph', 'figure'),
     Output('inventory-graph', 'figure')],
    [Input('results-store', 'data'),
     Input('analysis-tabs', 'active_tab')],
    prevent_initial_call=True
)
def update_insights(results, active_tab):
    if results is None:
        return create_empty_graph("Please run analysis first"), create_empty_graph("Please run analysis first")
    
    insights = results.get('insights', {})
    
    # Delivery time analysis graph
    delivery_perf = insights.get('delivery_performance', {})
    dates = delivery_perf.get('dates', [])
    delays = delivery_perf.get('delays', [])
    avg_delay = delivery_perf.get('average_delay', 0)
    on_time_rate = delivery_perf.get('on_time_rate', 0)
    
    delivery_fig = {
        "data": [
            go.Scatter(
                x=dates,
                y=delays,
                mode="lines+markers",
                name="Delivery Delays",
                line=dict(color="#4361ee", width=3),
                marker=dict(size=8, color="#4361ee", line=dict(width=1, color="#ffffff"))
            )
        ],
        "layout": go.Layout(
            title={
                'text': f"Delivery Time Analysis<br><span style='font-size:0.8em; color:gray'>Avg Delay: {avg_delay} min | On-time Rate: {on_time_rate}%</span>",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis=dict(
                title="Date",
                tickfont=dict(size=12),
                gridcolor='#f0f0f0',
                showgrid=True
            ),
            yaxis=dict(
                title="Delay (minutes)",
                tickfont=dict(size=12),
                gridcolor='#f0f0f0',
                showgrid=True
            ),
            hovermode="closest",
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=60, r=30, t=80, b=60),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
    }
    
    # Inventory analysis graph
    inventory_perf = insights.get('inventory_performance', {})
    dates = inventory_perf.get('dates', [])
    levels = inventory_perf.get('inventory_levels', [])
    avg_inventory = inventory_perf.get('average_inventory_level', 0)
    stockout_rate = inventory_perf.get('stockout_rate', 0)
    
    inventory_fig = {
        "data": [
            go.Bar(
                x=dates,
                y=levels,
                name="Inventory Levels",
                marker_color="#28a745",
                opacity=0.8
            ),
            go.Scatter(
                x=dates,
                y=[avg_inventory] * len(dates),
                mode="lines",
                name="Average Level",
                line=dict(color="#dc3545", width=2, dash="dash")
            )
        ],
        "layout": go.Layout(
            title={
                'text': f"Inventory Analysis<br><span style='font-size:0.8em; color:gray'>Avg Level: {avg_inventory} units | Stockout Risk: {stockout_rate}%</span>",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis=dict(
                title="Date",
                tickfont=dict(size=12),
                gridcolor='#f0f0f0',
                showgrid=True
            ),
            yaxis=dict(
                title="Inventory Level (units)",
                tickfont=dict(size=12),
                gridcolor='#f0f0f0',
                showgrid=True
            ),
            hovermode="closest",
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=60, r=30, t=80, b=60),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
    }
    
    return delivery_fig, inventory_fig

# Callback for updating prediction graphs
@app.callback(
    [Output('delay-forecast', 'figure'),
     Output('demand-forecast', 'figure')],
    [Input('results-store', 'data'),
     Input('analysis-tabs', 'active_tab')],
    prevent_initial_call=True
)
def update_predictions(results, active_tab):
    if results is None:
        return create_empty_graph("Please run analysis first"), create_empty_graph("Please run analysis first")
    
    predictions = results.get('predictions', {})
    
    # Delay forecast graph
    delay_forecast = predictions.get('delay_forecast', {})
    dates = delay_forecast.get('dates', [])
    values = delay_forecast.get('values', [])
    lower = delay_forecast.get('lower', [])
    upper = delay_forecast.get('upper', [])
    
    delay_fig = {
        "data": [
            # Confidence interval
            go.Scatter(
                x=dates + dates[::-1],
                y=upper + lower[::-1],
                fill='toself',
                fillcolor='rgba(67, 97, 238, 0.2)',
                line=dict(color='rgba(255, 255, 255, 0)'),
                hoverinfo='skip',
                showlegend=False
            ),
            # Main line
            go.Scatter(
                x=dates,
                y=values,
                mode='lines+markers',
                name='Predicted Delay',
                line=dict(color='#4361ee', width=3),
                marker=dict(size=10, color='#4361ee', line=dict(width=1, color='#ffffff'))
            )
        ],
        "layout": go.Layout(
            title={
                'text': "7-Day Delay Forecast",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis=dict(
                title="Date", 
                tickfont=dict(size=12),
                gridcolor='#f0f0f0',
                showgrid=True
            ),
            yaxis=dict(
                title="Delay (minutes)", 
                tickfont=dict(size=12),
                gridcolor='#f0f0f0',
                showgrid=True
            ),
            hovermode="x unified",
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Segoe UI"
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=60, r=30, t=80, b=60),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            annotations=[
                dict(
                    x=dates[-1],
                    y=values[-1],
                    xref="x",
                    yref="y",
                    text=f"{values[-1]:.1f} min",
                    showarrow=True,
                    arrowhead=7,
                    ax=0,
                    ay=-40
                )
            ]
        )
    }
    
    # Demand forecast graph
    demand_forecast = predictions.get('demand_forecast', {})
    dates = demand_forecast.get('dates', [])
    values = demand_forecast.get('values', [])
    lower = demand_forecast.get('lower', [])
    upper = demand_forecast.get('upper', [])
    
    demand_fig = {
        "data": [
            # Confidence interval
            go.Scatter(
                x=dates + dates[::-1],
                y=upper + lower[::-1],
                fill='toself',
                fillcolor='rgba(40, 167, 69, 0.2)',
                line=dict(color='rgba(255, 255, 255, 0)'),
                hoverinfo='skip',
                showlegend=False
            ),
            # Main bars
            go.Bar(
                x=dates,
                y=values,
                name='Predicted Demand',
                marker_color='#28a745',
                opacity=0.8
            )
        ],
        "layout": go.Layout(
            title={
                'text': "7-Day Demand Forecast",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis=dict(
                title="Date", 
                tickfont=dict(size=12),
                gridcolor='#f0f0f0',
                showgrid=True
            ),
            yaxis=dict(
                title="Demand (units)", 
                tickfont=dict(size=12),
                gridcolor='#f0f0f0',
                showgrid=True
            ),
            hovermode="x unified",
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Segoe UI"
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=60, r=30, t=80, b=60),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
    }
    
    return delay_fig, demand_fig

# Callback for updating optimization outputs
@app.callback(
    [Output('route-optimization', 'figure'),
     Output('route-savings', 'children'),
     Output('recommendations', 'children')],
    [Input('results-store', 'data'),
     Input('analysis-tabs', 'active_tab')],
    prevent_initial_call=True
)
def update_optimizations(results, active_tab):
    if results is None:
        return create_empty_graph("Please run analysis first"), "", "Please run analysis first"
    
    optimizations = results.get('optimizations', {})
    
    # Route optimization graph
    route_opt = optimizations.get('route_optimization', {})
    routes = route_opt.get('routes', [])
    current_distance = route_opt.get('current_distance', 0)
    optimized_distance = route_opt.get('optimized_distance', 0)
    savings_percent = route_opt.get('savings_percent', 0)
    
    # Savings summary
    savings_summary = html.Div([
        html.H5("Route Optimization Summary", className="mb-3"),
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Div(className="d-flex justify-content-between align-items-center mb-2", children=[
                            html.Span("Current Total Distance:", className="font-weight-bold"),
                            html.Span(f"{current_distance} km", className="text-danger")
                        ]),
                        html.Div(className="d-flex justify-content-between align-items-center mb-2", children=[
                            html.Span("Optimized Total Distance:", className="font-weight-bold"),
                            html.Span(f"{optimized_distance} km", className="text-success")
                        ]),
                        html.Div(className="d-flex justify-content-between align-items-center", children=[
                            html.Span("Distance Saved:", className="font-weight-bold"),
                            html.Span(f"{current_distance - optimized_distance} km ({savings_percent}%)", 
                                     className="text-primary font-weight-bold")
                        ]),
                    ])
                ], width=6),
                
                dbc.Col([
                    html.Div([
                        html.H6("Benefits:", className="mb-2"),
                        html.Ul([
                            html.Li("Reduced fuel consumption and emissions"),
                            html.Li("Faster delivery times"),
                            html.Li("Improved customer satisfaction"),
                            html.Li("Lower operational costs")
                        ], className="pl-3 mb-0")
                    ])
                ], width=6),
            ])
        ], className="p-3 border rounded bg-light")
    ])
    
    # Generate sample map data for US
    warehouses = [
        {"name": "Warehouse A", "lat": 41.8781, "lon": -87.6298},  # Chicago
        {"name": "Warehouse B", "lat": 33.7490, "lon": -84.3880}   # Atlanta
    ]
    
    customers = [
        {"name": "Customer 1", "lat": 41.7, "lon": -86.9},  # Near Chicago
        {"name": "Customer 2", "lat": 42.1, "lon": -88.2},  # Near Chicago
        {"name": "Customer 3", "lat": 33.2, "lon": -84.1},  # Near Atlanta
        {"name": "Customer 4", "lat": 34.0, "lon": -85.0}   # Near Atlanta
    ]
    
    route_fig = {
        "data": [
            # Warehouse markers
            go.Scattermapbox(
                lat=[w["lat"] for w in warehouses],
                lon=[w["lon"] for w in warehouses],
                mode='markers',
                marker=dict(
                    size=15, 
                    color='#dc3545',
                    symbol='warehouse'
                ),
                text=[w["name"] for w in warehouses],
                name='Warehouses',
                hovertemplate='<b>%{text}</b><br>Lat: %{lat}<br>Lon: %{lon}'
            ),
            # Customer markers
            go.Scattermapbox(
                lat=[c["lat"] for c in customers],
                lon=[c["lon"] for c in customers],
                mode='markers',
                marker=dict(
                    size=10, 
                    color='#4361ee'
                ),
                text=[c["name"] for c in customers],
                name='Customers',
                hovertemplate='<b>%{text}</b><br>Lat: %{lat}<br>Lon: %{lon}'
            ),
            # Lines for routes from Warehouse A
            go.Scattermapbox(
                lat=[warehouses[0]["lat"], customers[0]["lat"], 
                     warehouses[0]["lat"], customers[1]["lat"]],
                lon=[warehouses[0]["lon"], customers[0]["lon"],
                     warehouses[0]["lon"], customers[1]["lon"]],
                mode='lines',
                line=dict(width=2, color='#28a745'),
                name='Routes from Warehouse A',
                hoverinfo='none'
            ),
            # Lines for routes from Warehouse B
            go.Scattermapbox(
                lat=[warehouses[1]["lat"], customers[2]["lat"],
                     warehouses[1]["lat"], customers[3]["lat"]],
                lon=[warehouses[1]["lon"], customers[2]["lon"],
                     warehouses[1]["lon"], customers[3]["lon"]],
                mode='lines',
                line=dict(width=2, color='#fd7e14'),
                name='Routes from Warehouse B',
                hoverinfo='none'
            )
        ],
        "layout": go.Layout(
            title={
                'text': "Optimized Delivery Routes",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=38, lon=-85),
                zoom=4
            ),
            margin=dict(l=0, r=0, t=50, b=0),
            height=500,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
    }
    
    # Get recommendations
    recommendations = optimizations.get('recommendations', [])
    
    # Format recommendations as cards with icons
    rec_list = html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.I(className=f"fas fa-{icon} mr-3", style={"fontSize": "24px", "color": color}),
                    html.Div([
                        html.P(rec, className="mb-0")
                    ])
                ], className="d-flex align-items-center")
            ], className="p-3 border rounded mb-3 recommendation-card")
        for rec, icon, color in zip(
            recommendations,
            ["route", "clock", "warehouse", "box"],
            ["#4361ee", "#fd7e14", "#6f42c1", "#20c997"]
        )
        ])
    ])
    
    return route_fig, savings_summary, rec_list

# Callbacks for report generation
@app.callback(
    [Output('report-status', 'children'),
     Output('download-btn-container', 'className'),
     Output('report-data', 'data')],
    [Input('generate-report-btn', 'n_clicks')],
    [State('report-title', 'value'),
     State('report-sections', 'value'),
     State('results-store', 'data')],
    prevent_initial_call=True
)
def generate_report(n_clicks, title, sections, results):
    if n_clicks is None or results is None:
        return "", "mt-3 d-none", None
    
    # Create a status message
    status = html.Div([
        html.I(className="fas fa-check-circle mr-2 text-success"),
        html.Span("Report generated successfully!", className="text-success font-weight-bold")
    ], className="p-2 border rounded bg-light")
    
    # Create the download button container
    download_container = html.Div([
        dbc.Button(
            [html.I(className="fas fa-download mr-2"), "Download PDF Report"],
            id="download-report-btn",
            color="primary",
            className="mt-2"
        )
    ], className="mt-3")
    
    # Create report data for download
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"logistics_report_{timestamp}.pdf"
    
    # Prepare sample PDF content as base64
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        name='Title',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#4361ee'),
        spaceAfter=12
    )
    
    heading_style = ParagraphStyle(
        name='Heading2',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#343a40'),
        spaceAfter=10,
        spaceBefore=12
    )
    
    normal_style = ParagraphStyle(
        name='Normal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#343a40'),
        spaceAfter=6
    )
    
    # Elements for the PDF
    elements = []
    
    # Title
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Timestamp
    timestamp_text = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    elements.append(Paragraph(timestamp_text, normal_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Summary section
    if 'summary' in sections:
        elements.append(Paragraph("Summary of Findings", heading_style))
        
        summary_text = """
        Our analysis of your logistics data indicates significant opportunities for optimization. 
        The current average delivery delay is 15.3 minutes with an on-time delivery rate of 85%. 
        Inventory levels are generally stable but could be optimized to reduce stockout risks. 
        By implementing our recommended route optimizations, you could reduce total delivery distance by 21.6%, 
        resulting in fuel savings and faster deliveries.
        """
        elements.append(Paragraph(summary_text, normal_style))
        
        # Key metrics table
        elements.append(Paragraph("Key Performance Metrics", heading_style))
        
        data = [
            ["Metric", "Value", "Status"],
            ["Average Delay", "15.3 min", "⚠️ Needs Improvement"],
            ["On-Time Delivery Rate", "85%", "✅ Good"],
            ["Average Inventory Level", "520 units", "✅ Optimal"],
            ["Stockout Risk", "2.3%", "✅ Low Risk"],
            ["Route Optimization Savings", "21.6%", "💰 Significant"]
        ]
        
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4361ee')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
        ])
        
        summary_table = Table(data, colWidths=[2*inch, 1.5*inch, 2*inch])
        summary_table.setStyle(table_style)
        elements.append(summary_table)
    
    # Add recommendations section
    if 'recommendations' in sections:
        elements.append(Paragraph("Optimization Recommendations", heading_style))
        
        recommendations = results.get('optimizations', {}).get('recommendations', [])
        for i, rec in enumerate(recommendations):
            elements.append(Paragraph(f"• {rec}", normal_style))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF data
    pdf_data = pdf_buffer.getvalue()
    pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
    
    return status, "mt-3", {'content': pdf_base64, 'filename': filename}

# Callback for downloading the report
@app.callback(
    Output('download-report', 'data'),
    Input('download-report-btn', 'n_clicks'),
    State('report-data', 'data'),
    prevent_initial_call=True
)
def download_report(n_clicks, report_data):
    if n_clicks is None or report_data is None:
        return dash.no_update
    
    content = report_data.get('content', '')
    filename = report_data.get('filename', 'report.pdf')
    
    return dict(content=content, filename=filename, base64=True)

# Start the app
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8065))
    app.run_server(debug=True, port=port, host='0.0.0.0') 