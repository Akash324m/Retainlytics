import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Read CSV file
csv_file_path = r"C:\Users\aakas\Downloads\projects\Business_analytical project\Project-4\Data\online_retail_final.csv"
df = pd.read_csv(csv_file_path)

# Convert InvoiceDate to datetime
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

## Data Preparation for Cohort Analysis
def prepare_cohort_data(df):
    # Create cohort month (month of first purchase) as string
    df['InvoiceMonth'] = df['InvoiceDate'].dt.to_period('M').astype(str)
    
    # Get first purchase month for each customer
    df_cohort = df.groupby('CustomerID')['InvoiceMonth'].min().reset_index()
    df_cohort.columns = ['CustomerID', 'CohortMonth']
    
    # Merge cohort info back to original dataframe
    df = df.merge(df_cohort, on='CustomerID')
    
    # Convert cohort and invoice months to datetime for calculation
    df['CohortMonthDT'] = pd.to_datetime(df['CohortMonth'])
    df['InvoiceMonthDT'] = pd.to_datetime(df['InvoiceMonth'])
    
    # Calculate months difference (alternative method that works)
    df['CohortIndex'] = (
        (df['InvoiceMonthDT'].dt.year - df['CohortMonthDT'].dt.year) * 12 +
        (df['InvoiceMonthDT'].dt.month - df['CohortMonthDT'].dt.month)
    )
    
    return df

# Prepare cohort data
df = prepare_cohort_data(df)

# Create cohort analysis metrics
def create_cohort_metrics(df):
    # Cohort size (number of unique customers per cohort)
    cohort_size = df.groupby('CohortMonth')['CustomerID'].nunique().reset_index()
    cohort_size.columns = ['CohortMonth', 'TotalCustomers']
    
    # Retention analysis
    retention = df.groupby(['CohortMonth', 'CohortIndex'])['CustomerID'].nunique().reset_index()
    retention = retention.merge(cohort_size, on='CohortMonth')
    retention['RetentionRate'] = retention['CustomerID'] / retention['TotalCustomers']
    
    # Revenue analysis
    revenue = df.groupby(['CohortMonth', 'CohortIndex'])['TotalPrice'].sum().reset_index()
    revenue = revenue.merge(cohort_size, on='CohortMonth')
    revenue['AvgRevenuePerCustomer'] = revenue['TotalPrice'] / revenue['TotalCustomers']
    
    return cohort_size, retention, revenue

# Create cohort metrics
cohort_size, retention, revenue = create_cohort_metrics(df)

## Create cohort visualization functions
def create_retention_heatmap(retention):
    retention_pivot = retention.pivot_table(index='CohortMonth', 
                                         columns='CohortIndex', 
                                         values='RetentionRate')
    
    fig = px.imshow(
        retention_pivot,
        labels=dict(x="Months Since First Purchase", 
                   y="Cohort Month", 
                   color="Retention Rate"),
        x=[f"Month {i}" for i in retention_pivot.columns],
        y=retention_pivot.index,
        color_continuous_scale='Blues',
        zmin=0,
        zmax=1,
        aspect="auto"
    )
    
    fig.update_layout(
        title='Customer Retention by Cohort',
        xaxis_title='Months Since First Purchase',
        yaxis_title='Cohort Month',
        height=600
    )
    
    return fig

def create_revenue_heatmap(revenue):
    revenue_pivot = revenue.pivot_table(index='CohortMonth', 
                                      columns='CohortIndex', 
                                      values='AvgRevenuePerCustomer')
    
    fig = px.imshow(
        revenue_pivot,
        labels=dict(x="Months Since First Purchase", 
                   y="Cohort Month", 
                   color="Avg Revenue per Customer"),
        x=[f"Month {i}" for i in revenue_pivot.columns],
        y=revenue_pivot.index,
        color_continuous_scale='Greens',
        aspect="auto"
    )
    
    fig.update_layout(
        title='Average Revenue per Customer by Cohort',
        xaxis_title='Months Since First Purchase',
        yaxis_title='Cohort Month',
        height=600
    )
    
    return fig

def create_cohort_size_chart(cohort_size):
    fig = px.bar(
        cohort_size,
        x='CohortMonth',
        y='TotalCustomers',
        labels={'CohortMonth': 'Cohort Month', 'TotalCustomers': 'Number of Customers'},
        title='New Customer Acquisition by Month'
    )
    
    fig.update_layout(
        xaxis_title='Cohort Month',
        yaxis_title='Number of New Customers',
        height=400
    )
    
    return fig

# Create analysis insights component
def create_analysis_insights():
    insights = [
        "1. The retention drops significantly after Month 0 for all cohorts, indicating many users do not return after their first purchase.",
        "2. Some cohorts (e.g., Jan & Mar 2011) show relatively higher retention in later months, suggesting a few loyal user segments.",
        "3. Later cohorts (Sep, Nov 2011) show much shorter user lifecycles, which could imply issues in customer experience, product satisfaction, or lack of re-engagement.",
        "4. Revenue per customer tends to increase steadily in later months (e.g., Month 9-11), even if fewer users remain—this implies the remaining customers are high-value or repeat buyers.",
        "5. Early cohorts (e.g., Jan 2011) show strong revenue performance, suggesting those acquisition channels or products were more successful.",
        "6. Later cohorts show both lower retention and lower revenue, indicating a decline in either customer targeting, marketing quality, or product relevance over time."
    ]
    
    return dbc.Card(
        dbc.CardBody([
            html.H4("Key Insights from Cohort Analysis", className="card-title"),
            html.Ul([html.Li(insight) for insight in insights])
        ]),
        className="mb-4"
    )

## Update the dashboard layout with cohort analysis tabs
app.layout = dbc.Container([
    html.H1("Retail Analytics Dashboard", className="mb-4 text-center"),
    
    dbc.Tabs([
        dbc.Tab(label="Cohort Analysis", children=[
            dbc.Row([
                dbc.Col([
                    html.H3("Customer Acquisition Over Time"),
                    dcc.Graph(figure=create_cohort_size_chart(cohort_size))
                ], width=12)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    html.H3("Customer Retention Analysis"),
                    dcc.Graph(figure=create_retention_heatmap(retention))
                ], width=12)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    html.H3("Revenue Analysis"),
                    dcc.Graph(figure=create_revenue_heatmap(revenue))
                ], width=12)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    create_analysis_insights()
                ], width=12)
            ])
        ])
    ])
], fluid=True)

if __name__ == '__main__':
    app.run(debug=True)