import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json
import logging
import base64
import io
import plotly.express as px
from dash.exceptions import PreventUpdate
import random

# Set up logging for better error diagnostics
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Helper function for empty graphs - defined early
def create_empty_graph(message="No data available"):
    """Create an empty graph with a message in the center."""
    return {
        "data": [],
        "layout": go.Layout(
            title=message,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            annotations=[
                dict(
                    text=message,
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                    font=dict(size=16)
                )
            ],
            height=300,
            margin=dict(l=20, r=20, t=50, b=20)
        )
    }

# Helper function for empty maps - defined early
def create_empty_map(message="No data available"):
    """Create an empty map with a message."""
    return {
        "data": [],
        "layout": go.Layout(
            title=message,
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=40, lon=-95),  # Centered on US
                zoom=3
            ),
            height=400,
            margin=dict(l=0, r=0, t=50, b=0),
            hovermode=False
        )
    }

# Initialize the Dash app with dark/light theme support
app = dash.Dash(
    __name__,
    title="Logistics Optimization Dashboard",
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    ]
)

logger.info("Dashboard initialized successfully")

# Define CSS but don't use html.Style
app_css = '''
/* General Styles */
body {
    font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background-color: #f8f9fa;
    color: #333;
}
'''

# Add the CSS to the app layout
app.layout = html.Div([
    # Use a simple div for styling instead of html.Style
    html.Div(id='css-styles'),
    
    # Data stores
    dcc.Store(id='uploaded-data-store'),
    dcc.Store(id='analysis-results-store'),
    
    # Toast container for notifications
    html.Div([
        html.Div([
            html.Span(id="notification-icon", className="toast-icon"),
            html.Div([
                html.Div(id="notification-header", className="toast-header"),
                html.Div(id="notification-message", className="toast-message")
            ]),
        ], className="toast-notification", id="notification-container")
    ], id="notification-area", style={"display": "none"}),
    
    # Dark mode toggle
    html.Div([
        html.Button(
            html.I(className="fas fa-sun"),
            id="theme-toggle",
            className="theme-toggle-btn"
        )
    ], className="theme-toggle-container"),
    
    # Sidebar
    html.Div([
        html.Div([
            html.H2("Analytics Hub", className="sidebar-title"),
            html.Div([
                html.Div([
                    html.I(className="fas fa-folder"),
                    html.Span("Data Upload")
                ], id="nav-upload", className="sidebar-item active"),
                html.Div([
                    html.I(className="fas fa-chart-line"),
                    html.Span("Visual Insights")
                ], id="nav-insights", className="sidebar-item"),
                html.Div([
                    html.I(className="fas fa-chart-bar"),
                    html.Span("Predictive Results")
                ], id="nav-predictions", className="sidebar-item"),
                html.Div([
                    html.I(className="fas fa-arrow-trend-up"),
                    html.Span("Prescriptive Suggestions")
                ], id="nav-suggestions", className="sidebar-item"),
                html.Div([
                    html.I(className="fas fa-file-alt"),
                    html.Span("Generate Report")
                ], id="nav-report", className="sidebar-item"),
            ], className="sidebar-nav")
        ], className="sidebar-content")
    ], className="sidebar"),
    
    # Main content
    html.Div([
        # Content sections
        html.Div([
            # Data Upload Section
            html.Div([
                html.H2("Data Upload", className="section-title"),
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        html.I(className="fas fa-cloud-upload-alt", style={"font-size": "48px"}),
                        html.Div("Drag and Drop or Click to Upload Files", className="upload-text")
                    ]),
                    className="upload-container",
                    multiple=False
                ),
                html.Div(id='upload-status', className="upload-status"),
                html.Div(id='data-preview', className="data-preview"),
                html.Div(id='error-message', className="error-message"),
                
                # Add Submit Button and Loading Spinner
                html.Div([
                    html.Button(
                        [
                            html.I(className="fas fa-chart-line"),
                            " Run Analysis"
                        ],
                        id="submit-analysis",
                        className="action-button",
                        style={"display": "none"}
                    ),
                    dcc.Loading(
                        id="analysis-loading",
                        type="circle",
                        children=html.Div(id="analysis-loading-output")
                    )
                ], className="submit-container"),
            ], id="section-upload", className="content-section"),
            
            # Visual Insights Section
            html.Div([
                html.H2("Visual Insights", className="section-title"),
                html.Div([
                    # Filters
                    html.Div([
                        html.H3("Filters", className="filter-title"),
                        dcc.DatePickerRange(
                            id='date-range',
                            className="date-filter"
                        ),
                        dcc.Dropdown(
                            id='warehouse-filter',
                            placeholder="Select Warehouse",
                            className="filter-dropdown"
                        ),
                        dcc.Dropdown(
                            id='transport-filter',
                            placeholder="Select Transport Mode",
                            className="filter-dropdown"
                        )
                    ], className="filters-container"),
                    
                    # Charts
                    html.Div([
                        html.Div([
                            html.H3("Delivery Time Distribution"),
                            dcc.Graph(id="delivery-dist-graph")
                        ], className="chart-container"),
                        html.Div([
                            html.H3("Inventory Heatmap"),
                            dcc.Graph(id="inventory-heatmap")
                        ], className="chart-container")
                    ], className="charts-grid")
                ])
            ], id="section-insights", className="content-section hidden"),
            
            # Predictive Results Section
            html.Div([
                html.H2("Predictive Results", className="section-title"),
                
                # Key metrics cards
                html.Div([
                    html.Div([
                        html.I(className="fas fa-truck", style={"font-size": "32px"}),
                        html.Div([
                            html.H3(id="avg-delay-metric"),
                            html.P("Average Delay")
                        ], className="metric-text")
                    ], className="metric-card"),
                    
                    html.Div([
                        html.I(className="fas fa-box", style={"font-size": "32px"}),
                        html.Div([
                            html.H3(id="avg-demand-metric"),
                            html.P("Average Demand")
                        ], className="metric-text")
                    ], className="metric-card"),
                    
                    html.Div([
                        html.I(className="fas fa-dollar-sign", style={"font-size": "32px"}),
                        html.Div([
                            html.H3(id="logistics-cost-metric"),
                            html.P("Total Logistics Cost")
                        ], className="metric-text")
                    ], className="metric-card"),
                ], className="metrics-container"),
                
                # Prediction charts
                html.Div([
                    html.Div([
                        html.H3("7-Day Delay Forecast"),
                        dcc.Graph(id="delay-forecast-graph")
                    ], className="chart-container"),
                    
                    html.Div([
                        html.H3("7-Day Demand Forecast"),
                        dcc.Graph(id="demand-forecast-graph")
                    ], className="chart-container")
                ], className="charts-grid"),
                
                # Detailed predictions table
                html.Div([
                    html.H3("Detailed Predictions"),
                    html.Div(id="prediction-table", className="table-container")
                ], className="section-container")
                
            ], id="section-predictive", className="content-section hidden"),
            
            # Prescriptive Suggestions Section
            html.Div([
                html.H3('Prescriptive Suggestions', className='section-header'),
                html.Div([
                    # Route optimization section
                    html.Div([
                        html.H4('Optimized Routes', className='subsection-header'),
                        html.Div([
                            # Route map
                            html.Div([
                                dcc.Graph(id='route-map', figure=create_empty_graph("Please run analysis first"))
                            ], className='card-body'),
                        ], className='card'),
                    ], className='prescriptive-column'),
                    
                    # Inventory optimization section
                    html.Div([
                        html.H4('Inventory Optimization', className='subsection-header'),
                        html.Div([
                            # Inventory optimization graph
                            html.Div([
                                dcc.Graph(id='inventory-optimization', figure=create_empty_graph("Please run analysis first"))
                            ], className='card-body'),
                        ], className='card'),
                    ], className='prescriptive-column'),
                ], className='row'),
                
                # Recommendations section
                html.Div([
                    html.H4('Recommended Actions', className='subsection-header mt-4'),
                    html.Div([
                        html.Div(id='recommendations-list', children=[
                            html.Div("Please run analysis to see recommendations", className="empty-message")
                        ], className='card-body')
                    ], className='card')
                ], className='mt-4')
            ], id='section-prescriptive', className='dashboard-section hidden'),
            
            # Report Generation Section
            html.Div([
                html.H2("Generate Report", className="section-title"),
                html.Div([
                    html.Button(
                        [
                            DashIconify(icon="ph:file-pdf", className="button-icon"),
                            "Generate Report"
                        ],
                        id="generate-report-btn",
                        className="action-button"
                    ),
                    dcc.Download(id="download-report")
                ], className="report-container")
            ], id="section-report", className="content-section hidden")
        ], className="content-container")
    ], className="main-content")
], id="app-container", className="app-container")

# Update CSS with modern design
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            :root {
                --primary-color: #2563eb;
                --bg-color: #f8fafc;
                --text-color: #1e293b;
                --card-bg: #ffffff;
                --border-color: #e2e8f0;
                --hover-color: #f1f5f9;
            }
            
            [data-theme="dark"] {
                --primary-color: #3b82f6;
                --bg-color: #0f172a;
                --text-color: #e2e8f0;
                --card-bg: #1e293b;
                --border-color: #334155;
                --hover-color: #1e293b;
            }
            
            body {
                font-family: 'Inter', sans-serif;
                margin: 0;
                background-color: var(--bg-color);
                color: var(--text-color);
                transition: background-color 0.3s, color 0.3s;
            }
            
            .app-container {
                display: flex;
                min-height: 100vh;
            }
            
            .sidebar {
                width: 260px;
                background: var(--card-bg);
                border-right: 1px solid var(--border-color);
                position: fixed;
                height: 100vh;
                padding: 1.5rem;
                box-sizing: border-box;
            }
            
            .main-content {
                flex: 1;
                margin-left: 260px;
                padding: 2rem;
            }
            
            .sidebar-title {
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 2rem;
            }
            
            .sidebar-item {
                display: flex;
                align-items: center;
                padding: 0.75rem 1rem;
                border-radius: 0.5rem;
                cursor: pointer;
                margin-bottom: 0.5rem;
                transition: background-color 0.2s;
            }
            
            .sidebar-item:hover {
                background-color: var(--hover-color);
            }
            
            .sidebar-item.active {
                background-color: var(--primary-color);
                color: white;
            }
            
            .sidebar-icon {
                margin-right: 0.75rem;
            }
            
            .content-section {
                background: var(--card-bg);
                border-radius: 1rem;
                padding: 2rem;
                margin-bottom: 2rem;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            }
            
            .upload-container {
                border: 2px dashed var(--border-color);
                border-radius: 1rem;
                padding: 3rem;
                text-align: center;
                cursor: pointer;
                transition: border-color 0.2s;
            }
            
            .upload-container:hover {
                border-color: var(--primary-color);
            }
            
            .upload-icon {
                color: var(--primary-color);
                margin-bottom: 1rem;
            }
            
            .filters-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                margin-bottom: 2rem;
            }
            
            .charts-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 2rem;
            }
            
            .chart-container {
                background: var(--card-bg);
                border-radius: 0.5rem;
                padding: 1.5rem;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            }
            
            .hidden {
                display: none;
            }
            
            .theme-toggle-container {
                position: fixed;
                top: 1rem;
                right: 1rem;
                z-index: 1000;
            }
            
            .theme-toggle-btn {
                background: var(--card-bg);
                border: 1px solid var(--border-color);
                border-radius: 0.5rem;
                padding: 0.5rem;
                cursor: pointer;
                transition: background-color 0.2s;
            }
            
            .theme-toggle-btn:hover {
                background-color: var(--hover-color);
            }
            
            .submit-container {
                margin-top: 2rem;
                display: flex;
                align-items: center;
                gap: 1rem;
            }
            
            .action-button {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                background-color: var(--primary-color);
                color: white;
                border: none;
                padding: 0.75rem 1.5rem;
                border-radius: 0.5rem;
                cursor: pointer;
                font-weight: 500;
                transition: background-color 0.2s;
            }
            
            .action-button:hover {
                background-color: #1d4ed8;
            }
            
            .button-icon {
                width: 20px;
                height: 20px;
            }
            
            /* Loading spinner styles */
            ._dash-loading-callback {
                position: fixed !important;
                top: 50% !important;
                left: 50% !important;
                transform: translate(-50%, -50%) !important;
                background-color: var(--card-bg) !important;
                border-radius: 0.5rem !important;
                padding: 2rem !important;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
            }
            
            .notification-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
            }
            
            .notification {
                padding: 1rem;
                margin-bottom: 1rem;
                border-radius: 0.5rem;
                display: flex;
                align-items: center;
                gap: 0.75rem;
                animation: slideIn 0.3s ease-out;
            }
            
            .notification.success {
                background-color: #10B981;
                color: white;
            }
            
            .notification.error {
                background-color: #EF4444;
                color: white;
            }
            
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            .recommendations-container {
                padding: 1rem;
                background: var(--card-bg);
                border-radius: 0.5rem;
                margin-top: 1rem;
            }
            
            .recommendation-item {
                display: flex;
                align-items: flex-start;
                gap: 0.75rem;
                padding: 0.75rem;
                border-bottom: 1px solid var(--border-color);
            }
            
            .recommendation-item:last-child {
                border-bottom: none;
            }
            
            .recommendation-icon {
                color: var(--primary-color);
            }
            
            .report-container {
                display: flex;
                flex-direction: column;
                gap: 1rem;
                align-items: center;
                padding: 2rem;
            }
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

# Add theme toggle callback
@app.callback(
    Output("body", "data-theme"),
    Input("theme-toggle", "n_clicks"),
    State("body", "data-theme")
)
def toggle_theme(n_clicks, current_theme):
    if n_clicks is None:
        return "light"
    return "dark" if current_theme == "light" else "light"

def parse_contents(contents, filename):
    """Parse uploaded file contents."""
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return None, "Unsupported file type. Please upload a CSV or Excel file."
        
        return df, "File uploaded successfully!"
    except Exception as e:
        return None, f"Error processing file: {str(e)}"

# Update the file upload callback to show/hide submit button
@app.callback(
    [Output('upload-status', 'children'),
     Output('data-preview', 'children'),
     Output('error-message', 'children'),
     Output('submit-analysis', 'style'),
     Output('uploaded-data-store', 'data')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_output(contents, filename):
    """Handle file upload and update dashboard."""
    try:
        if contents is None:
            return "No file uploaded.", None, "", {"display": "none"}, None
        
        df, message = parse_contents(contents, filename)
        if df is None:
            return message, None, "Error: Invalid file format or content", {"display": "none"}, None
        
        # Create data preview
        preview = html.Div([
            html.H4("Data Preview"),
            dash_table.DataTable(
                data=df.head().to_dict('records'),
                columns=[{"name": i, "id": i} for i in df.columns],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '10px'}
            )
        ])
        
        # Store the data
        stored_data = {
            'data': df.to_dict('records'),
            'columns': df.columns.tolist()
        }
        
        return message, preview, "", {"display": "block"}, stored_data
    except Exception as e:
        return f"Error: {str(e)}", None, str(e), {"display": "none"}, None

# Update callback for submit button
@app.callback(
    [Output('analysis-loading-output', 'children'),
     Output('notification-area', 'style'),
     Output('notification-container', 'className'),
     Output('notification-header', 'children'),
     Output('notification-message', 'children'),
     Output('notification-icon', 'children'),
     Output('analysis-results-store', 'data'),
     Output('section-upload', 'className', allow_duplicate=True),
     Output('section-insights', 'className', allow_duplicate=True),
     Output('section-prescriptive', 'className', allow_duplicate=True),
     Output('section-report', 'className', allow_duplicate=True),
     Output('nav-upload', 'className', allow_duplicate=True),
     Output('nav-insights', 'className', allow_duplicate=True),
     Output('nav-suggestions', 'className', allow_duplicate=True),
     Output('nav-report', 'className', allow_duplicate=True)],
    [Input('submit-analysis', 'n_clicks')],
    [State('uploaded-data-store', 'data')],
    prevent_initial_call=True
)
def run_analysis(n_clicks, stored_data):
    """Run the analysis pipeline on the uploaded data."""
    if n_clicks is None or not stored_data:
        raise PreventUpdate
    
    logger.info("Running analysis on uploaded data")
    
    try:
        # Make calls to the API for predictions, optimization, and insights
        predictions_response = None
        optimization_response = None
        insights_response = None
        
        try:
            # Call prediction API
            logger.info("Calling prediction API")
            predictions_response = requests.post(
                "http://127.0.0.1:8075/predict/", 
                json={"data": stored_data},
                timeout=10  # Increased timeout from 5 to 10 seconds
            )
            predictions = predictions_response.json()
            logger.info("Prediction API call successful")
        except Exception as e:
            logger.error(f"Prediction API request failed: {str(e)}")
            predictions = {"error": str(e)}
        
        try:
            # Call optimization API
            logger.info("Calling optimization API")
            optimization_response = requests.post(
                "http://127.0.0.1:8075/optimize-routes/", 
                json={"data": stored_data},
                timeout=10  # Increased timeout
            )
            optimizations = optimization_response.json()
            logger.info("Optimization API call successful")
        except Exception as e:
            logger.error(f"Optimization API request failed: {str(e)}")
            optimization = {"routes": [], "inventory": [], "error": str(e)}
        
        # Get insights with proper error handling
        try:
            logger.info("Calling insights API...")
            response = requests.get(
                f"{api_base_url}/insights/",
                timeout=10  # Increased timeout
            )
            if response.status_code != 200:
                logger.error(f"Insights API error: {response.text}")
                insights = {}
            else:
                insights = response.json()
                logger.info("Insights API call successful")
        except Exception as e:
            logger.error(f"Insights API request failed: {str(e)}")
            insights = {"error": str(e)}
        
        # Store results
        results = {
            "predictions": predictions,
            "optimization": optimization,
            "insights": insights,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "analyzed": True
        }
        
        logger.info("Analysis completed successfully. Storing results and navigating to insights.")
        
        # Return success state - navigate to insights tab
        return (
            None,  # Clear loading output
            True,  # Show toast
            "Success",  # Toast header
            "Analysis complete! Navigating to results",  # Toast message
            "success",  # Toast icon
            results,  # Store analysis results
            "content-section hidden",  # Hide upload section
            "content-section",  # Show insights section
            "content-section hidden",  # Hide prescriptive section
            "content-section hidden",  # Hide report section
            "sidebar-item",  # Update navigation classes
            "sidebar-item active",  # Activate insights tab
            "sidebar-item",  # Deactivate suggestions tab
            "sidebar-item"   # Deactivate report tab
        )
    
    except Exception as e:
        logger.error(f"Error in run_analysis: {str(e)}")
        # Return error state
        return (
            None,  # Clear loading output
            True,  # Show toast
            "Error",  # Toast header
            f"Analysis failed: {str(e)}",  # Toast message with error details
            "danger",  # Toast icon
            None,  # No results to store
            "content-section",  # Keep upload section visible
            "content-section hidden",  # Hide other sections
            "content-section hidden",
            "content-section hidden",
            "sidebar-item active",
            "sidebar-item",
            "sidebar-item",
            "sidebar-item"
        )

# Add callback for prescriptive suggestions and optimization graphs
@app.callback(
    [Output('route-optimization-graph', 'figure', allow_duplicate=True),
     Output('inventory-optimization-graph', 'figure', allow_duplicate=True),
     Output('optimization-recommendations', 'children')],
    [Input('nav-suggestions', 'n_clicks')],
    [State('analysis-results-store', 'data')],
    prevent_initial_call=True
)
def update_optimization_graphs(suggestions_clicks, results):
    """Update optimization graphs when suggestions tab is clicked."""
    if suggestions_clicks is None:
        raise PreventUpdate
    
    try:
        # Handle missing or empty results
        if results is None:
            empty_graphs = generate_empty_graphs("No data available. Please run analysis first.")
            empty_recommendations = html.Div([
                html.Div([
                    DashIconify(icon="ph:info", className="recommendation-icon"),
                    html.Div([
                        html.H4("No Data"),
                        html.P("Please upload a file and run analysis first.")
                    ])
                ], className="recommendation-item")
            ])
            return empty_graphs[0], empty_graphs[1], empty_recommendations
        
        optimization_data = results.get('optimization', {})
        if not optimization_data:
            empty_graphs = generate_empty_graphs("No optimization data available.")
            empty_recommendations = html.Div([
                html.Div([
                    DashIconify(icon="ph:info", className="recommendation-icon"),
                    html.Div([
                        html.H4("No Optimization Data"),
                        html.P("The analysis did not produce any optimization data.")
                    ])
                ], className="recommendation-item")
            ])
            return empty_graphs[0], empty_graphs[1], empty_recommendations
        
        routes = optimization_data.get('routes', [])
        inventory = optimization_data.get('inventory', [])
        suggestions = optimization_data.get('suggestions', [])
        
        # Create route optimization figure
        if routes:
            # Group by warehouse for better visualization
            warehouses = {}
            for route in routes:
                warehouse = route.get('warehouse', f"Warehouse at ({route.get('depot_x', 0)}, {route.get('depot_y', 0)})")
                if warehouse not in warehouses:
                    warehouses[warehouse] = {
                        'depot_x': route.get('depot_x', 0),
                        'depot_y': route.get('depot_y', 0),
                        'delivery_x': [],
                        'delivery_y': [],
                        'delivery_ids': []
                    }
                warehouses[warehouse]['delivery_x'].append(route.get('delivery_x', 0))
                warehouses[warehouse]['delivery_y'].append(route.get('delivery_y', 0))
                warehouses[warehouse]['delivery_ids'].append(route.get('delivery_id', f"D{len(warehouses[warehouse]['delivery_ids'])+1}"))
            
            route_data = []
            
            # Add warehouse locations
            depot_scatter = go.Scatter(
                x=[w['depot_x'] for w in warehouses.values()],
                y=[w['depot_y'] for w in warehouses.values()],
                mode="markers",
                name="Warehouses",
                marker=dict(
                    size=15, 
                    color="red",
                    symbol="square"
                ),
                text=list(warehouses.keys()),
                hoverinfo="text"
            )
            route_data.append(depot_scatter)
            
            # Add routes for each warehouse with different colors
            colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
            for i, (name, warehouse) in enumerate(warehouses.items()):
                color = colors[i % len(colors)]
                
                # Add lines from warehouse to each delivery
                for j in range(len(warehouse['delivery_x'])):
                    route_data.append(
                        go.Scatter(
                            x=[warehouse['depot_x'], warehouse['delivery_x'][j]],
                            y=[warehouse['depot_y'], warehouse['delivery_y'][j]],
                            mode="lines",
                            line=dict(color=color, width=1.5),
                            showlegend=False,
                            hoverinfo="none"
                        )
                    )
                
                # Add delivery points
                route_data.append(
                    go.Scatter(
                        x=warehouse['delivery_x'],
                        y=warehouse['delivery_y'],
                        mode="markers",
                        name=f"Deliveries from {name}",
                        marker=dict(size=8, color=color),
                        text=warehouse['delivery_ids'],
                        hoverinfo="text"
                    )
                )
            
            route_fig = {
                "data": route_data,
                "layout": go.Layout(
                    title="Optimized Delivery Routes",
                    showlegend=True,
                    hovermode="closest",
                    xaxis=dict(title="X Coordinate"),
                    yaxis=dict(title="Y Coordinate"),
                    height=500
                )
            }
        else:
            route_fig = create_empty_graph("No route data available")
        
        # Create inventory optimization figure
        if inventory:
            inventory_dates = [i.get('date', '') for i in inventory]
            inventory_levels = [i.get('level', 0) for i in inventory]
            reorder_points = [i.get('reorder_point', 0) for i in inventory]
            safety_stocks = [i.get('safety_stock', 0) for i in inventory]
            
            inventory_fig = {
                "data": [
                    go.Scatter(
                        x=inventory_dates,
                        y=inventory_levels,
                        mode="lines+markers",
                        name="Inventory Level",
                        line=dict(color="#007bff", width=2)
                    ),
                    go.Scatter(
                        x=inventory_dates,
                        y=reorder_points,
                        mode="lines",
                        name="Reorder Point",
                        line=dict(color="#dc3545", dash="dash", width=1.5)
                    ),
                    go.Scatter(
                        x=inventory_dates,
                        y=safety_stocks,
                        mode="lines",
                        name="Safety Stock",
                        line=dict(color="#ffc107", dash="dot", width=1.5)
                    )
                ],
                "layout": go.Layout(
                    title="Inventory Optimization",
                    xaxis=dict(title="Date"),
                    yaxis=dict(title="Units"),
                    showlegend=True,
                    height=500
                )
            }
        else:
            inventory_fig = create_empty_graph("No inventory data available")
        
        # Create recommendations
        recommendations = []
        
        # Route optimization recommendations
        if 'route_savings' in optimization_data:
            route_savings = optimization_data.get('route_savings', 0)
            recommendations.append(
                html.Div([
                    DashIconify(icon="ph:truck", className="recommendation-icon"),
                    html.Div([
                        html.H4("Route Optimization"),
                        html.P(f"Optimized routes can save approximately {route_savings:.1f}% in transportation costs.")
                    ])
                ], className="recommendation-item")
            )
        
        # Add suggestions from API
        if suggestions:
            for i, suggestion in enumerate(suggestions):
                icons = ["ph:lightbulb", "ph:chart-line-up", "ph:currency-circle-dollar"]
                recommendations.append(
                    html.Div([
                        DashIconify(icon=icons[i % len(icons)], className="recommendation-icon"),
                        html.Div([
                            html.H4(f"Suggestion {i+1}"),
                            html.P(suggestion)
                        ])
                    ], className="recommendation-item")
                )
        
        # Inventory recommendations
        if 'inventory' in optimization_data:
            inventory_data = optimization_data['inventory']
            if any(i.get('level', 500) < i.get('reorder_point', 400) for i in inventory_data):
                recommendations.append(
                    html.Div([
                        DashIconify(icon="ph:package", className="recommendation-icon"),
                        html.Div([
                            html.H4("Inventory Alert"),
                            html.P("Some items are below reorder point. Consider restocking soon.")
                        ])
                    ], className="recommendation-item")
                )
        
        # If no recommendations
        if not recommendations:
            recommendations.append(
                html.Div([
                    DashIconify(icon="ph:check-circle", className="recommendation-icon"),
                    html.Div([
                        html.H4("No Issues Detected"),
                        html.P("Current operations are running optimally.")
                    ])
                ], className="recommendation-item")
            )
        
        return route_fig, inventory_fig, html.Div(recommendations)
    
    except Exception as e:
        logger.error(f"Error updating optimization graphs: {str(e)}")
        empty_graphs = generate_empty_graphs(f"Error: {str(e)}")
        error_recommendation = html.Div([
            html.Div([
                DashIconify(icon="ph:warning", className="recommendation-icon error"),
                html.Div([
                    html.H4("Error"),
                    html.P(f"Could not generate recommendations: {str(e)}")
                ])
            ], className="recommendation-item error")
        ])
        return empty_graphs[0], empty_graphs[1], error_recommendation

def generate_empty_graphs(message):
    """Generate empty graphs for both route and inventory."""
    empty_graph = create_empty_graph(message)
    return empty_graph, empty_graph

# Add callback for report generation
@app.callback(
    Output('download-report', 'data'),
    [Input('generate-report-btn', 'n_clicks')],
    [State('analysis-results-store', 'data')]
)
def generate_report(n_clicks, results):
    """Generate and download analysis report."""
    if n_clicks is None or results is None:
        raise PreventUpdate
    
    try:
        # Create report content
        report_content = {
            'predictions': results.get('predictions', {}),
            'optimization': results.get('optimization', {}),
            'insights': results.get('insights', {})
        }
        
        # Convert to DataFrame for Excel export
        df = pd.DataFrame(report_content)
        
        # Save to Excel buffer
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Analysis Report', index=False)
        
        # Return file for download
        return dcc.send_bytes(
            buffer.getvalue(),
            'logistics_analysis_report.xlsx',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    except Exception as e:
        # Show error notification
        return None

# Add navigation callbacks
@app.callback(
    [Output("section-upload", "className", allow_duplicate=True),
     Output("section-insights", "className", allow_duplicate=True),
     Output("section-prescriptive", "className", allow_duplicate=True),
     Output("section-report", "className", allow_duplicate=True),
     Output("nav-upload", "className", allow_duplicate=True),
     Output("nav-insights", "className", allow_duplicate=True),
     Output("nav-suggestions", "className", allow_duplicate=True),
     Output("nav-report", "className", allow_duplicate=True)],
    [Input("nav-upload", "n_clicks"),
     Input("nav-insights", "n_clicks"),
     Input("nav-suggestions", "n_clicks"),
     Input("nav-report", "n_clicks")],
    prevent_initial_call=True
)
def toggle_sections(upload_clicks, insights_clicks, suggestions_clicks, report_clicks):
    """Toggle active sections and navigation items based on clicks."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return "content-section", "content-section hidden", "content-section hidden", "content-section hidden", "sidebar-item active", "sidebar-item", "sidebar-item", "sidebar-item"
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    logger.info(f"Navigation clicked: {button_id}")
    
    if button_id == "nav-upload":
        return "content-section", "content-section hidden", "content-section hidden", "content-section hidden", "sidebar-item active", "sidebar-item", "sidebar-item", "sidebar-item"
    elif button_id == "nav-insights":
        return "content-section hidden", "content-section", "content-section hidden", "content-section hidden", "sidebar-item", "sidebar-item active", "sidebar-item", "sidebar-item"
    elif button_id == "nav-suggestions":
        return "content-section hidden", "content-section hidden", "content-section", "content-section hidden", "sidebar-item", "sidebar-item", "sidebar-item active", "sidebar-item"
    elif button_id == "nav-report":
        return "content-section hidden", "content-section hidden", "content-section hidden", "content-section", "sidebar-item", "sidebar-item", "sidebar-item", "sidebar-item active"
    else:
        # Default case
        return "content-section", "content-section hidden", "content-section hidden", "content-section hidden", "sidebar-item active", "sidebar-item", "sidebar-item", "sidebar-item"

# Add theme toggle callback
@app.callback(
    Output("app-container", "className"),
    Input("theme-toggle", "n_clicks")
)
def toggle_theme(n_clicks):
    if n_clicks is None or n_clicks % 2 == 0:
        return "app-container"
    return "app-container dark-theme"

# Callbacks for updating graphs
@app.callback(
    Output("delay-forecast-graph", "figure"),
    Input("update-delay-btn", "n_clicks")
)
def update_delay_forecast(n_clicks):
    """Update the delay forecast graph."""
    if n_clicks is None:
        n_clicks = 0
    
    # Generate sample data (replace with actual API calls)
    dates = pd.date_range(start=datetime.now(), periods=7, freq="D")
    delays = np.random.normal(15, 5, 7)  # Sample delays in minutes
    
    return {
        "data": [
            go.Scatter(
                x=dates,
                y=delays,
                mode="lines+markers",
                name="Predicted Delays",
                line=dict(color="#007bff")
            )
        ],
        "layout": go.Layout(
            title="7-Day Delay Forecast",
            xaxis=dict(title="Date"),
            yaxis=dict(title="Predicted Delay (minutes)"),
            hovermode="x unified",
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
    }

@app.callback(
    Output("demand-forecast-graph", "figure"),
    Input("update-demand-btn", "n_clicks")
)
def update_demand_forecast(n_clicks):
    """Update the demand forecast graph."""
    if n_clicks is None:
        n_clicks = 0
    
    # Generate sample data (replace with actual API calls)
    dates = pd.date_range(start=datetime.now(), periods=7, freq="D")
    demand = np.random.normal(100, 20, 7)  # Sample demand
    
    return {
        "data": [
            go.Bar(
                x=dates,
                y=demand,
                name="Predicted Demand",
                marker_color="#28a745"
            )
        ],
        "layout": go.Layout(
            title="7-Day Demand Forecast",
            xaxis=dict(title="Date"),
            yaxis=dict(title="Predicted Demand (units)"),
            hovermode="x unified",
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
    }

# Add callback for updating insights visualizations
@app.callback(
    [Output('delivery-dist-graph', 'figure'),
     Output('inventory-heatmap', 'figure')],
    [Input('section-insights', 'className'),
     Input('analysis-results-store', 'data')]
)
def update_insights_visualizations(section_class, results):
    """Update insights visualizations when section is displayed or data changes."""
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    # Check if insights section is visible and results exist
    if 'hidden' in section_class or results is None or not results.get('analyzed', False):
        logger.info("Insights section not visible or no analysis results available")
        return create_empty_graph("Please run analysis first"), create_empty_graph("Please run analysis first")
    
    try:
        logger.info("Updating insights visualizations with analysis results")
        insights = results.get('insights', {})
        predictions = results.get('predictions', {})
        
        # Create delivery time distribution graph
        delivery_perf = insights.get('delivery_performance', {})
        on_time_rate = delivery_perf.get('on_time_delivery_rate', 0.85)
        avg_delay = delivery_perf.get('average_delay', 15)
        
        # Generate sample distribution data
        delays = predictions.get('delays', [])
        if not delays:
            # Generate mock data if no real data
            delays = np.random.normal(avg_delay, avg_delay/3, 100).tolist()
        
        delivery_fig = {
            "data": [
                go.Histogram(
                    x=delays,
                    marker_color='#007bff',
                    opacity=0.7,
                    name="Delivery Delays",
                    nbinsx=20
                ),
                go.Scatter(
                    x=[avg_delay, avg_delay],
                    y=[0, 25],
                    mode="lines",
                    line=dict(color="red", width=2, dash="dash"),
                    name=f"Avg Delay: {avg_delay:.1f} min"
                )
            ],
            "layout": go.Layout(
                title=f"Delivery Time Distribution (On-time rate: {on_time_rate*100:.1f}%)",
                xaxis=dict(title="Delay (minutes)"),
                yaxis=dict(title="Frequency"),
                showlegend=True,
                height=400
            )
        }
        
        # Create inventory heatmap
        inventory_perf = insights.get('inventory_performance', {})
        avg_inventory = inventory_perf.get('average_inventory_level', 500)
        
        # Generate sample warehouse-product inventory data
        warehouses = ["Warehouse A", "Warehouse B", "Warehouse C"]
        products = ["Product 1", "Product 2", "Product 3", "Product 4"]
        
        # Create inventory levels matrix
        inventory_matrix = []
        for _ in warehouses:
            row = []
            for _ in products:
                row.append(max(0, np.random.normal(avg_inventory, avg_inventory/4)))
            inventory_matrix.append(row)
        
        inventory_fig = {
            "data": [
                go.Heatmap(
                    z=inventory_matrix,
                    x=products,
                    y=warehouses,
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Units"),
                    hovertemplate="Warehouse: %{y}<br>Product: %{x}<br>Stock: %{z:.0f} units<extra></extra>"
                )
            ],
            "layout": go.Layout(
                title="Inventory Levels by Warehouse and Product",
                height=400,
                margin=dict(l=70, r=20, t=50, b=50)
            )
        }
        
        return delivery_fig, inventory_fig
    
    except Exception as e:
        logger.error(f"Error updating insights visualizations: {str(e)}")
        return (
            create_empty_graph(f"Error creating delivery graph: {str(e)}"),
            create_empty_graph(f"Error creating inventory graph: {str(e)}")
        )

# Add callback for updating predictive metrics
@app.callback(
    [Output('avg-delay-metric', 'children'),
     Output('avg-demand-metric', 'children'),
     Output('logistics-cost-metric', 'children'),
     Output('delay-forecast-graph', 'figure'),
     Output('demand-forecast-graph', 'figure'),
     Output('prediction-table', 'children')],
    [Input('section-predictive', 'className'),
     Input('analysis-results-store', 'data')]
)
def update_predictive_results(section_class, results):
    """Update predictive results when section is displayed or data changes."""
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    # Check if predictive section is visible and results exist
    if 'hidden' in section_class or results is None or not results.get('analyzed', False):
        logger.info("Predictive section not visible or no analysis results available")
        empty_fig = create_empty_graph("Please run analysis first")
        empty_table = html.Div("Please run analysis first", className="empty-message")
        return "N/A", "N/A", "N/A", empty_fig, empty_fig, empty_table
    
    try:
        logger.info("Updating predictive results with analysis results")
        insights = results.get('insights', {})
        predictions = results.get('predictions', {})
        
        # Extract metrics
        delivery_perf = insights.get('delivery_performance', {})
        inventory_perf = insights.get('inventory_performance', {})
        cost_analysis = insights.get('cost_analysis', {})
        
        avg_delay = delivery_perf.get('average_delay', 15)
        avg_demand = inventory_perf.get('average_inventory_level', 500)
        total_cost = cost_analysis.get('total_logistics_cost', 15000)
        
        # Format metrics
        avg_delay_str = f"{avg_delay:.1f} min"
        avg_demand_str = f"{avg_demand:.0f} units"
        total_cost_str = f"${total_cost:,.0f}"
        
        # Generate delay forecast graph
        dates = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        
        # Generate delay forecast data
        delay_forecast = []
        delay_trend = delivery_perf.get('delay_trend', 'Stable')
        
        base_delay = avg_delay
        for i in range(7):
            if delay_trend == 'Increasing':
                factor = 1 + (i * 0.05)
            elif delay_trend == 'Decreasing':
                factor = 1 - (i * 0.03)
            else:  # Stable
                factor = 1 + (np.random.normal(0, 0.05))
            
            delay = max(1, base_delay * factor)
            uncertainty = delay * 0.15
            
            delay_forecast.append({
                'date': dates[i],
                'delay': delay,
                'lower': max(0, delay - uncertainty),
                'upper': delay + uncertainty
            })
        
        delay_fig = {
            "data": [
                # Confidence interval
                go.Scatter(
                    x=dates + dates[::-1],
                    y=[d['upper'] for d in delay_forecast] + [d['lower'] for d in delay_forecast][::-1],
                    fill='toself',
                    fillcolor='rgba(0, 123, 255, 0.2)',
                    line=dict(color='rgba(255, 255, 255, 0)'),
                    hoverinfo='skip',
                    showlegend=False
                ),
                # Main line
                go.Scatter(
                    x=dates,
                    y=[d['delay'] for d in delay_forecast],
                    mode='lines+markers',
                    line=dict(color='#007bff', width=2),
                    marker=dict(size=8, color='#007bff'),
                    name='Predicted Delay',
                    hovertemplate='%{x}: %{y:.1f} minutes<extra></extra>'
                )
            ],
            "layout": go.Layout(
                title=f"7-Day Delay Forecast (Trend: {delay_trend})",
                xaxis=dict(title="Date"),
                yaxis=dict(title="Delay (minutes)"),
                height=400,
                margin=dict(l=50, r=20, t=50, b=50),
                hovermode="x unified"
            )
        }
        
        # Generate demand forecast graph
        demand_forecast = []
        inventory_trend = inventory_perf.get('inventory_trend', 'Stable')
        
        base_demand = avg_demand
        for i in range(7):
            if inventory_trend == 'Increasing':
                factor = 1 + (i * 0.03)
            elif inventory_trend == 'Decreasing':
                factor = 1 - (i * 0.02)
            else:  # Stable
                factor = 1 + (np.random.normal(0, 0.03))
            
            demand = max(10, base_demand * factor)
            uncertainty = demand * 0.1
            
            demand_forecast.append({
                'date': dates[i],
                'demand': demand,
                'lower': max(0, demand - uncertainty),
                'upper': demand + uncertainty
            })
        
        demand_fig = {
            "data": [
                # Confidence interval
                go.Scatter(
                    x=dates + dates[::-1],
                    y=[d['upper'] for d in demand_forecast] + [d['lower'] for d in demand_forecast][::-1],
                    fill='toself',
                    fillcolor='rgba(40, 167, 69, 0.2)',
                    line=dict(color='rgba(255, 255, 255, 0)'),
                    hoverinfo='skip',
                    showlegend=False
                ),
                # Main bars
                go.Bar(
                    x=dates,
                    y=[d['demand'] for d in demand_forecast],
                    marker_color='#28a745',
                    name='Predicted Demand',
                    hovertemplate='%{x}: %{y:.0f} units<extra></extra>'
                )
            ],
            "layout": go.Layout(
                title=f"7-Day Demand Forecast (Trend: {inventory_trend})",
                xaxis=dict(title="Date"),
                yaxis=dict(title="Demand (units)"),
                height=400,
                margin=dict(l=50, r=20, t=50, b=50),
                hovermode="x unified"
            )
        }
        
        # Create prediction table
        predictions_data = []
        for i, date in enumerate(dates):
            predictions_data.append({
                "Date": date,
                "Predicted Delay": f"{delay_forecast[i]['delay']:.1f} min",
                "Delay Range": f"{delay_forecast[i]['lower']:.1f} - {delay_forecast[i]['upper']:.1f} min",
                "Predicted Demand": f"{demand_forecast[i]['demand']:.0f} units",
                "Demand Range": f"{demand_forecast[i]['lower']:.0f} - {demand_forecast[i]['upper']:.0f} units"
            })
        
        prediction_table = dash_table.DataTable(
            id='prediction-table-dt',
            columns=[{"name": k, "id": k} for k in predictions_data[0].keys()],
            data=predictions_data,
            style_table={'overflowX': 'auto'},
            style_header={
                'backgroundColor': 'rgb(240, 240, 240)',
                'fontWeight': 'bold',
                'borderBottom': '1px solid black'
            },
            style_cell={
                'padding': '10px',
                'textAlign': 'center'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ]
        )
        
        return avg_delay_str, avg_demand_str, total_cost_str, delay_fig, demand_fig, prediction_table
        
    except Exception as e:
        logger.error(f"Error updating predictive results: {str(e)}")
        empty_fig = create_empty_graph(f"Error: {str(e)}")
        empty_table = html.Div(f"Error loading predictions: {str(e)}", className="error-message")
        return "Error", "Error", "Error", empty_fig, empty_fig, empty_table

# Add callback for updating prescriptive suggestions
@app.callback(
    [Output('route-map', 'figure'),
     Output('inventory-optimization', 'figure'),
     Output('recommendations-list', 'children')],
    [Input('section-prescriptive', 'className'),
     Input('analysis-results-store', 'data')]
)
def update_prescriptive_suggestions(section_class, results):
    """Update prescriptive suggestions when section is displayed or data changes."""
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    # Check if prescriptive section is visible and results exist
    if 'hidden' in section_class or results is None or not results.get('analyzed', False):
        logger.info("Prescriptive section not visible or no analysis results available")
        empty_map = create_empty_map("Please run analysis first")
        empty_fig = create_empty_graph("Please run analysis first")
        empty_rec = html.Div("Please run analysis to see recommendations", className="empty-message")
        return empty_map, empty_fig, empty_rec
    
    try:
        logger.info("Updating prescriptive suggestions with analysis results")
        optimizations = results.get('optimizations', {})
        insights = results.get('insights', {})
        
        # Generate optimized routes map
        routes = optimizations.get('optimized_routes', {})
        warehouses = routes.get('warehouses', [])
        deliveries = routes.get('deliveries', [])
        
        if not warehouses or not deliveries:
            logger.warning("No route data available for map")
            empty_map = create_empty_map("No route data available")
            return empty_map, create_empty_graph("No data"), html.Div("No recommendations available", className="empty-message")
        
        # Create route map
        map_data = []
        
        # Calculate center of map
        all_lats = [loc['lat'] for loc in warehouses + deliveries]
        all_lons = [loc['lon'] for loc in warehouses + deliveries]
        center_lat = sum(all_lats) / len(all_lats) if all_lats else 40
        center_lon = sum(all_lons) / len(all_lons) if all_lons else -95
        
        # Add warehouse markers
        map_data.append(go.Scattermapbox(
            lat=[w['lat'] for w in warehouses],
            lon=[w['lon'] for w in warehouses],
            mode='markers',
            marker=dict(
                size=15,
                color='red',
                symbol='warehouse'
            ),
            text=[w['name'] for w in warehouses],
            name='Warehouses',
            hovertemplate='<b>%{text}</b><br>Warehouse<extra></extra>'
        ))
        
        # Add delivery markers
        map_data.append(go.Scattermapbox(
            lat=[d['lat'] for d in deliveries],
            lon=[d['lon'] for d in deliveries],
            mode='markers',
            marker=dict(
                size=10,
                color='blue',
                symbol='circle'
            ),
            text=[d['name'] for d in deliveries],
            name='Delivery Points',
            hovertemplate='<b>%{text}</b><br>Delivery Point<extra></extra>'
        ))
        
        # Add route lines
        routes_data = routes.get('routes', [])
        
        for i, route in enumerate(routes_data):
            route_color = f'hsl({(i * 30) % 360}, 70%, 50%)'
            
            # Extract locations in route
            route_points = []
            if 'warehouse' in route and 'deliveries' in route:
                warehouse_idx = route['warehouse']
                warehouse = warehouses[warehouse_idx] if warehouse_idx < len(warehouses) else None
                
                if warehouse:
                    route_points.append(warehouse)
                    
                    # Add each delivery point in the route
                    for delivery_idx in route['deliveries']:
                        if delivery_idx < len(deliveries):
                            route_points.append(deliveries[delivery_idx])
                    
                    # Return to warehouse at the end
                    route_points.append(warehouse)
                    
                    # Create route line
                    map_data.append(go.Scattermapbox(
                        lat=[p['lat'] for p in route_points],
                        lon=[p['lon'] for p in route_points],
                        mode='lines',
                        line=dict(width=2, color=route_color),
                        name=f'Route {i+1}',
                        hoverinfo='none'
                    ))
        
        route_map = {
            "data": map_data,
            "layout": go.Layout(
                title="Optimized Delivery Routes",
                mapbox=dict(
                    style="open-street-map",
                    center=dict(lat=center_lat, lon=center_lon),
                    zoom=5
                ),
                height=500,
                margin=dict(l=0, r=0, t=50, b=0),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
        }
        
        # Generate inventory optimization chart
        inventory_opts = optimizations.get('inventory_optimization', {})
        products = inventory_opts.get('products', [])
        warehouses_names = [w['name'] for w in warehouses]
        
        if not products or not warehouses_names:
            inventory_fig = create_empty_graph("No inventory data available")
        else:
            # Create sample data if none provided
            if len(products) < 3:
                products = [
                    {"name": "Product A", "optimized_levels": [120, 80, 150]},
                    {"name": "Product B", "optimized_levels": [90, 110, 70]},
                    {"name": "Product C", "optimized_levels": [60, 130, 100]}
                ]
            
            if len(warehouses_names) < 3:
                warehouses_names = ["Warehouse 1", "Warehouse 2", "Warehouse 3"]
            
            # Limit to max 5 products and 5 warehouses for readability
            products = products[:5]
            warehouses_names = warehouses_names[:5]
            
            # Create inventory optimization graph
            inventory_data = []
            
            # Current vs Optimized inventory comparison
            for i, product in enumerate(products):
                product_name = product.get('name', f'Product {i+1}')
                current_levels = product.get('current_levels', [])
                if not current_levels or len(current_levels) != len(warehouses_names):
                    # Generate sample current levels if not provided or wrong length
                    current_levels = [random.randint(50, 200) for _ in range(len(warehouses_names))]
                
                optimized_levels = product.get('optimized_levels', [])
                if not optimized_levels or len(optimized_levels) != len(warehouses_names):
                    # Generate sample optimized levels if not provided or wrong length
                    optimized_levels = [max(30, cl * random.uniform(0.7, 0.9)) for cl in current_levels]
                
                # Current inventory bars
                inventory_data.append(go.Bar(
                    name=f'Current {product_name}',
                    x=warehouses_names,
                    y=current_levels,
                    marker_color=f'hsl({(i * 60) % 360}, 70%, 50%)',
                    opacity=0.7,
                    hovertemplate='<b>%{x}</b><br>Current: %{y} units<extra>'+product_name+'</extra>'
                ))
                
                # Optimized inventory bars
                inventory_data.append(go.Bar(
                    name=f'Optimized {product_name}',
                    x=warehouses_names,
                    y=optimized_levels,
                    marker_color=f'hsl({(i * 60) % 360}, 70%, 30%)',
                    marker_pattern_shape='/',
                    hovertemplate='<b>%{x}</b><br>Optimized: %{y} units<extra>'+product_name+'</extra>'
                ))
            
            inventory_fig = {
                "data": inventory_data,
                "layout": go.Layout(
                    title="Inventory Level Optimization",
                    xaxis=dict(title="Warehouse"),
                    yaxis=dict(title="Inventory Level (units)"),
                    barmode='group',
                    height=500,
                    margin=dict(l=50, r=20, t=50, b=100),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    hovermode="x unified"
                )
            }
        
        # Generate recommendations
        route_recs = optimizations.get('route_recommendations', [])
        inventory_recs = optimizations.get('inventory_recommendations', [])
        cost_insights = insights.get('cost_analysis', {})
        
        recommendations = []
        
        # Create sample recommendations if none provided
        if not route_recs:
            route_recs = [
                "Consolidate deliveries to southern region to reduce total distance by 15%",
                "Schedule deliveries during off-peak hours to reduce transit times",
                "Prioritize high-value customers for expedited shipping"
            ]
        
        if not inventory_recs:
            inventory_recs = [
                "Reduce safety stock of Product A at Warehouse 2 by 20% to optimize carrying costs",
                "Increase inventory levels of Product C at Warehouse 1 to meet growing demand",
                "Implement just-in-time delivery for Product B to minimize storage costs"
            ]
        
        savings = cost_insights.get('potential_savings', 12000)
        cost_efficiency = cost_insights.get('cost_efficiency', 85)
        
        # Create recommendation cards
        recommendations.append(html.Div([
            html.H5("Summary", className="recommendation-header"),
            html.P([
                f"Implementing these optimizations could save an estimated ",
                html.Strong(f"${savings:,.0f}"),
                f" annually and improve cost efficiency to ",
                html.Strong(f"{cost_efficiency}%"),
                "."
            ], className="recommendation-summary")
        ], className="recommendation-card summary-card"))
        
        # Route recommendations
        recommendations.append(html.Div([
            html.H5("Route Optimization", className="recommendation-header"),
            html.Ul([
                html.Li(rec, className="recommendation-item") for rec in route_recs
            ])
        ], className="recommendation-card"))
        
        # Inventory recommendations
        recommendations.append(html.Div([
            html.H5("Inventory Management", className="recommendation-header"),
            html.Ul([
                html.Li(rec, className="recommendation-item") for rec in inventory_recs
            ])
        ], className="recommendation-card"))
        
        # Add custom recommendation
        demand_forecast = results.get('predictions', {}).get('demand_forecast', {})
        demand_trend = insights.get('inventory_performance', {}).get('inventory_trend', 'Stable')
        
        custom_rec = ""
        if demand_trend == "Increasing":
            custom_rec = "Based on increasing demand forecast, consider expanding warehouse capacity in the northern region."
        elif demand_trend == "Decreasing":
            custom_rec = "With forecasted demand decrease, consider temporarily reducing procurement to optimize working capital."
        else:
            custom_rec = "Maintain current inventory levels with regular review as demand appears stable."
        
        recommendations.append(html.Div([
            html.H5("Strategic Suggestions", className="recommendation-header"),
            html.P(custom_rec, className="recommendation-item")
        ], className="recommendation-card"))
        
        return route_map, inventory_fig, recommendations
        
    except Exception as e:
        logger.error(f"Error updating prescriptive suggestions: {str(e)}")
        empty_map = create_empty_map(f"Error: {str(e)}")
        empty_fig = create_empty_graph(f"Error: {str(e)}")
        error_rec = html.Div(f"Error loading recommendations: {str(e)}", className="error-message")
        return empty_map, empty_fig, error_rec

# Add callback for updating the report generation section
@app.callback(
    Output('report-preview', 'children'),
    [Input('section-report', 'className'),
     Input('analysis-results-store', 'data')]
)
def update_report_preview(section_class, results):
    """Update report preview when section is displayed or data changes."""
    if 'hidden' in section_class or results is None or not results.get('analyzed', False):
        logger.info("Report section not visible or no analysis results available")
        return html.Div("Please run analysis first to generate a report", className="empty-message")
    
    try:
        logger.info("Updating report preview with analysis results")
        insights = results.get('insights', {})
        predictions = results.get('predictions', {})
        optimizations = results.get('optimizations', {})
        timestamp = results.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Extract metrics for the report
        delivery_perf = insights.get('delivery_performance', {})
        inventory_perf = insights.get('inventory_performance', {})
        cost_analysis = insights.get('cost_analysis', {})
        
        avg_delay = delivery_perf.get('average_delay', 15)
        on_time_rate = delivery_perf.get('on_time_rate', 82)
        avg_demand = inventory_perf.get('average_inventory_level', 500)
        total_cost = cost_analysis.get('total_logistics_cost', 15000)
        potential_savings = cost_analysis.get('potential_savings', 12000)
        
        # Get recommendations
        route_recs = optimizations.get('route_recommendations', [])
        inventory_recs = optimizations.get('inventory_recommendations', [])
        
        if not route_recs:
            route_recs = [
                "Consolidate deliveries to southern region to reduce total distance by 15%",
                "Schedule deliveries during off-peak hours to reduce transit times"
            ]
        
        if not inventory_recs:
            inventory_recs = [
                "Reduce safety stock of Product A at Warehouse 2 by 20% to optimize carrying costs",
                "Increase inventory levels of Product C at Warehouse 1 to meet growing demand"
            ]
        
        # Generate sample report
        report = html.Div([
            html.Div([
                html.H4("Logistics Optimization Report", className="report-title"),
                html.P(f"Generated on: {timestamp}", className="report-date")
            ], className="report-header"),
            
            html.Div([
                html.H5("Executive Summary", className="report-section-title"),
                html.P([
                    "Based on our analysis, your logistics operations are performing at ",
                    html.Strong(f"{cost_analysis.get('cost_efficiency', 85)}%"),
                    " efficiency. Implementing the recommended optimizations could save an estimated ",
                    html.Strong(f"${potential_savings:,.0f}"),
                    " annually."
                ]),
                html.Hr()
            ], className="report-section"),
            
            html.Div([
                html.H5("Performance Metrics", className="report-section-title"),
                html.Div([
                    html.Div([
                        html.P("Delivery Performance:", className="metric-label"),
                        html.Ul([
                            html.Li(f"Average Delay: {avg_delay:.1f} minutes"),
                            html.Li(f"On-Time Delivery Rate: {on_time_rate}%")
                        ])
                    ], className="report-metric"),
                    html.Div([
                        html.P("Inventory Management:", className="metric-label"),
                        html.Ul([
                            html.Li(f"Average Inventory Level: {avg_demand:.0f} units"),
                            html.Li(f"Inventory Trend: {inventory_perf.get('inventory_trend', 'Stable')}")
                        ])
                    ], className="report-metric"),
                    html.Div([
                        html.P("Cost Analysis:", className="metric-label"),
                        html.Ul([
                            html.Li(f"Total Logistics Cost: ${total_cost:,.0f}"),
                            html.Li(f"Potential Annual Savings: ${potential_savings:,.0f}")
                        ])
                    ], className="report-metric")
                ], className="report-metrics-grid"),
                html.Hr()
            ], className="report-section"),
            
            html.Div([
                html.H5("Key Recommendations", className="report-section-title"),
                html.Div([
                    html.Div([
                        html.P("Route Optimization:", className="rec-label"),
                        html.Ul([html.Li(rec) for rec in route_recs[:3]])
                    ], className="report-rec"),
                    html.Div([
                        html.P("Inventory Management:", className="rec-label"),
                        html.Ul([html.Li(rec) for rec in inventory_recs[:3]])
                    ], className="report-rec")
                ], className="report-recs-grid"),
                html.Hr()
            ], className="report-section"),
            
            html.Div([
                html.H5("Next Steps", className="report-section-title"),
                html.P([
                    "We recommend implementing these optimizations in phases, starting with the route consolidation and inventory adjustments. ",
                    "This approach will minimize disruption while maximizing early benefits. A follow-up analysis is recommended in 3 months to measure impact."
                ]),
                html.Div([
                    html.Button("Download Full Report (PDF)", id="download-report-btn", className="btn btn-primary mr-2"),
                    html.Button("Email Report", id="email-report-btn", className="btn btn-secondary")
                ], className="report-actions mt-4")
            ], className="report-section")
        ], className="report-preview-container")
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating report preview: {str(e)}")
        return html.Div(f"Error generating report: {str(e)}", className="error-message")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8065))
    app.run(debug=True, host="127.0.0.1", port=port) 