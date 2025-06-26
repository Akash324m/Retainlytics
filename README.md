# Retainlytics
This project is a comprehensive retail analytics dashboard that performs cohort analysis to track customer retention and revenue patterns over time.

**Features**

        Cohort Analysis:

        Tracks customer groups (cohorts) based on their first purchase month

        Measures retention rates over time

        Analyzes revenue patterns by cohort

        Interactive Visualizations:

        Heatmaps showing retention rates by cohort

        Heatmaps showing average revenue per customer

        Bar charts displaying new customer acquisition

**Key Insights:**

        Automated interpretation of cohort patterns

        Identification of high-performing cohorts

        Detection of potential issues in customer lifecycle

**Installation**
    Clone the repository:

        git clone https://github.com/yourusername/retail-cohort-analysis.git
        cd retail-cohort-analysis

    Create and activate a virtual environment (recommended):

        python -m venv venv
        source venv/bin/activate  # On Windows use `venv\Scripts\activate`

    Install the required packages:

        pip install -r requirements.txt

**Usage**

Prepare your data:

        Place your retail transaction data in CSV format at Data/online_retail_final.csv

        Ensure the CSV contains at least these columns: CustomerID, InvoiceDate, TotalPrice

        Run the dashboard:

            python app.py
            Access the dashboard:

        Open your web browser and navigate to http://127.0.0.1:8050/

**Data Requirements**

    The dashboard expects a CSV file with the following structure:

        Column	Description	Required
        CustomerID	Unique identifier for each customer	Yes
        InvoiceDate	Date of the transaction	Yes
        TotalPrice	Total amount of the transaction	Yes


**Configuration**

    Modify these variables in app.py as needed:

    python
            # Path to your data file
            csv_file_path = r"Data\online_retail_final.csv"

            # Dashboard title
            app.title = "Retail Analytics Dashboard"


**Project Structure**

    retail-cohort-analysis/
    ├── Data/
    │   └── online_retail_final.csv       # Sample transaction data
    ├── app.py                            # Main application file
    ├── requirements.txt                  # Python dependencies
    └── README.md                         # This documentation file


**Dependencies**
    Python 3.7+

    Dash

    Plotly

    Pandas

    NumPy

    dash-bootstrap-components

    All dependencies are listed in requirements.txt.



**Methodology**

    Cohort Analysis Approach

    1. Cohort Identification:

        Customers are grouped by their first purchase month

        Each cohort is tracked over subsequent months

    2. Retention Calculation:

        Percentage of customers from each cohort who make purchases in subsequent months

        Formula: (Customers active in month N / Total cohort customers) × 100

    3. Revenue Analysis:

        Average revenue per customer for each cohort in each month

        Helps identify high-value customer segments


**Screenshots**

(Include screenshots of your dashboard here if available)

**Future Enhancements**

        Add user authentication

        Implement data upload functionality

        Add more granular filtering options

        Include customer segmentation analysis

        Add export functionality for reports