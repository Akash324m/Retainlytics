import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import re
from datetime import datetime

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Read CSV file (changed from Excel to CSV based on your file path)
csv_file_path = r"C:\Users\aakas\Downloads\projects\Business_analytical project\Project-4\Data\online_retail_final.csv"  # Change this to your file path
df = pd.read_csv(csv_file_path)

# Data quality checks function for retail data
def run_data_quality_checks(df):
    # Make a copy to avoid SettingWithCopyWarning
    df = df.copy()
    
    # 1. Invoice Date validation
    df['invoice_date_valid'] = pd.to_datetime(df['InvoiceDate'], errors='coerce').notna()
    
    # 2. Customer ID validation (should be numeric)
    df['customer_id_valid'] = pd.to_numeric(df['CustomerID'], errors='coerce').notna()
    
    # 3. Quantity validation (should be positive)
    df['quantity_valid'] = (df['Quantity'] > 0)
    
    # 4. Unit Price validation (should be positive)
    df['unit_price_valid'] = (df['UnitPrice'] > 0)
    
    # 5. Description validation (should not be empty)
    df['description_valid'] = (~df['Description'].isna()) & (df['Description'].str.strip() != '')
    
    # 6. Total Price validation (should match Quantity * UnitPrice)
    df['calculated_total'] = df['Quantity'] * df['UnitPrice']
    df['total_price_valid'] = (abs(df['TotalPrice'] - df['calculated_total']) < 0.01)  # Allow small rounding differences
    
    return df

# Calculate data quality metrics for retail data
def calculate_quality_metrics(df):
    metrics = {
        'total_records': len(df),
        'date_issues': (~df['invoice_date_valid']).sum(),
        'customer_id_issues': (~df['customer_id_valid']).sum(),
        'quantity_issues': (~df['quantity_valid']).sum(),
        'unit_price_issues': (~df['unit_price_valid']).sum(),
        'description_issues': (~df['description_valid']).sum(),
        'total_price_issues': (~df['total_price_valid']).sum(),
    }
    
    # Define critical issues (pricing and quantity related)
    metrics['critical_issues'] = metrics['quantity_issues'] + metrics['unit_price_issues'] + metrics['total_price_issues']
    
    # Define normal issues (descriptive and customer info)
    metrics['normal_issues'] = metrics['date_issues'] + metrics['customer_id_issues'] + metrics['description_issues']
    
    total_issues = metrics['critical_issues'] + metrics['normal_issues']
    
    metrics['quality_score'] = 100 - (total_issues / metrics['total_records'] * 100) if metrics['total_records'] > 0 else 100
    
    return metrics

# Run quality checks and calculate metrics
df = run_data_quality_checks(df)
metrics = calculate_quality_metrics(df)

# Generate dashboard layout
app.layout = dbc.Container([
    html.H1("Retail Data Quality Dashboard", className="mb-4 text-center"),
    
    # Summary Cards
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Total Records"),
            dbc.CardBody([
                html.H4(f"{metrics['total_records']:,}", className="card-title")
            ])
        ], color="light", outline=True), md=3),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("Data Quality Score"),
            dbc.CardBody([
                html.H4(f"{metrics['quality_score']:.1f}%", className="card-title"),
                dcc.Graph(
                    figure=px.bar(
                        x=[metrics['quality_score']],
                        orientation='h',
                        range_x=[0, 100],
                        text_auto=True
                    ).update_layout(
                        showlegend=False,
                        margin=dict(l=0, r=0, t=0, b=0),
                        xaxis=dict(showgrid=False, visible=False),
                        yaxis=dict(visible=False),
                        height=50
                    ),
                    config={'staticPlot': True},
                    style={'height': '50px'}
                )
            ])
        ], color="primary", outline=True), md=3),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("Critical Issues"),
            dbc.CardBody([
                html.H4(f"{metrics['critical_issues']}", 
                        className="card-title text-danger")
            ])
        ], color="danger", outline=True), md=3),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("Last Updated"),
            dbc.CardBody([
                html.H4(datetime.now().strftime("%Y-%m-%d %H:%M"), 
                className="card-title")
            ])
        ], color="info", outline=True), md=3),
    ], className="mb-4"),
    
    # Issue Breakdown
    dbc.Row([
        dbc.Col([
            html.H4("Data Quality Issues Breakdown"),
            dcc.Graph(
                figure=px.bar(
                    x=['Dates', 'Customer ID', 'Quantity', 'Unit Price', 'Description', 'Total Price'],
                    y=[
                        metrics['date_issues'],
                        metrics['customer_id_issues'],
                        metrics['quantity_issues'],
                        metrics['unit_price_issues'],
                        metrics['description_issues'],
                        metrics['total_price_issues']
                    ],
                    labels={'x': 'Issue Type', 'y': 'Count'},
                    color=['Normal', 'Normal', 'Critical', 'Critical', 'Normal', 'Critical'],
                    color_discrete_map={'Normal': '#1f77b4', 'Critical': '#ff7f0e'}
                ).update_layout(
                    xaxis_title="Issue Type",
                    yaxis_title="Number of Records Affected",
                    legend_title="Issue Severity"
                )
            )
        ], md=6),
        
        dbc.Col([
            html.H4("Data Quality Distribution"),
            dcc.Graph(
                figure=px.pie(
                    names=['Invalid Data', 'Valid Data'],
                    values=[100 - metrics['quality_score'], metrics['quality_score']],
                    hole=0.6,
                    color_discrete_sequence=['#2ca02c','#d62728']
                )
            )
        ], md=6)
    ], className="mb-4"),
    
    # Issue Type Filter and Detailed Issues Table
    dbc.Row([
        dbc.Col([
            html.H4("Detailed Issue Records"),
            dbc.Row([
                dbc.Col([
                    html.Label("Filter by Issue Type:"),
                    dcc.Dropdown(
                        id='issue-type-filter',
                        options=[
                            {'label': 'All Issues', 'value': 'all'},
                            {'label': 'Critical Issues (Quantity, Pricing)', 'value': 'critical'},
                            {'label': 'Normal Issues (Dates, Descriptions)', 'value': 'normal'}
                        ],
                        value='all',
                        clearable=False,
                        style={'width': '300px'}
                    )
                ], width=6)
            ], className="mb-3"),
            
            dash_table.DataTable(
                id='issues-table',
                columns=[
                    {"name": "Invoice No", "id": "invoice_no"},
                    {"name": "Stock Code", "id": "stock_code"},
                    {"name": "Issue Type", "id": "issue_type"},
                    {"name": "Field Value", "id": "field_value"},
                    {"name": "Description", "id": "description"},
                    {"name": "Severity", "id": "severity"}
                ],
                data=[
                    {
                        "invoice_no": row['InvoiceNo'],
                        "stock_code": row['StockCode'],
                        "issue_type": "Date Format",
                        "field_value": row['InvoiceDate'],
                        "description": "Invalid date format",
                        "severity": "Normal"
                    } for _, row in df[~df['invoice_date_valid']].iterrows()
                ] + [
                    {
                        "invoice_no": row['InvoiceNo'],
                        "stock_code": row['StockCode'],
                        "issue_type": "Customer ID",
                        "field_value": row['CustomerID'],
                        "description": "Invalid customer ID",
                        "severity": "Normal"
                    } for _, row in df[~df['customer_id_valid']].iterrows()
                ] + [
                    {
                        "invoice_no": row['InvoiceNo'],
                        "stock_code": row['StockCode'],
                        "issue_type": "Quantity",
                        "field_value": row['Quantity'],
                        "description": "Invalid quantity (not positive)",
                        "severity": "Critical"
                    } for _, row in df[~df['quantity_valid']].iterrows()
                ] + [
                    {
                        "invoice_no": row['InvoiceNo'],
                        "stock_code": row['StockCode'],
                        "issue_type": "Unit Price",
                        "field_value": row['UnitPrice'],
                        "description": "Invalid unit price (not positive)",
                        "severity": "Critical"
                    } for _, row in df[~df['unit_price_valid']].iterrows()
                ] + [
                    {
                        "invoice_no": row['InvoiceNo'],
                        "stock_code": row['StockCode'],
                        "issue_type": "Description",
                        "field_value": row['Description'],
                        "description": "Missing or empty description",
                        "severity": "Normal"
                    } for _, row in df[~df['description_valid']].iterrows()
                ] + [
                    {
                        "invoice_no": row['InvoiceNo'],
                        "stock_code": row['StockCode'],
                        "issue_type": "Total Price",
                        "field_value": f"Actual: {row['TotalPrice']}, Calculated: {row['calculated_total']}",
                        "description": "Total doesn't match quantity × unit price",
                        "severity": "Critical"
                    } for _, row in df[~df['total_price_valid']].iterrows()
                ],
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'whiteSpace': 'normal',
                    'height': 'auto'
                },
                filter_action="native",
                sort_action="native"
            )
        ])
    ])
], fluid=True)

# Callback to filter table based on issue type
@app.callback(
    dash.dependencies.Output('issues-table', 'data'),
    [dash.dependencies.Input('issue-type-filter', 'value')]
)
def update_table(selected_type):
    all_data = [
        {
            "invoice_no": row['InvoiceNo'],
            "stock_code": row['StockCode'],
            "issue_type": "Date Format",
            "field_value": row['InvoiceDate'],
            "description": "Invalid date format",
            "severity": "Normal"
        } for _, row in df[~df['invoice_date_valid']].iterrows()
    ] + [
        {
            "invoice_no": row['InvoiceNo'],
            "stock_code": row['StockCode'],
            "issue_type": "Customer ID",
            "field_value": row['CustomerID'],
            "description": "Invalid customer ID",
            "severity": "Normal"
        } for _, row in df[~df['customer_id_valid']].iterrows()
    ] + [
        {
            "invoice_no": row['InvoiceNo'],
            "stock_code": row['StockCode'],
            "issue_type": "Quantity",
            "field_value": row['Quantity'],
            "description": "Invalid quantity (not positive)",
            "severity": "Critical"
        } for _, row in df[~df['quantity_valid']].iterrows()
    ] + [
        {
            "invoice_no": row['InvoiceNo'],
            "stock_code": row['StockCode'],
            "issue_type": "Unit Price",
            "field_value": row['UnitPrice'],
            "description": "Invalid unit price (not positive)",
            "severity": "Critical"
        } for _, row in df[~df['unit_price_valid']].iterrows()
    ] + [
        {
            "invoice_no": row['InvoiceNo'],
            "stock_code": row['StockCode'],
            "issue_type": "Description",
            "field_value": row['Description'],
            "description": "Missing or empty description",
            "severity": "Normal"
        } for _, row in df[~df['description_valid']].iterrows()
    ] + [
        {
            "invoice_no": row['InvoiceNo'],
            "stock_code": row['StockCode'],
            "issue_type": "Total Price",
            "field_value": f"Actual: {row['TotalPrice']}, Calculated: {row['calculated_total']}",
            "description": "Total doesn't match quantity × unit price",
            "severity": "Critical"
        } for _, row in df[~df['total_price_valid']].iterrows()
    ]
    
    if selected_type == 'all':
        return all_data
    elif selected_type == 'critical':
        return [x for x in all_data if x['severity'] == 'Critical']
    elif selected_type == 'normal':
        return [x for x in all_data if x['severity'] == 'Normal']
    return all_data

if __name__ == '__main__':
    app.run(debug=True)