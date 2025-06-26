import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 1. Load your existing data
df = pd.read_excel("Business_analytical project\Data Cleaning and Validating\indian_users_dataset_3.xlsx")

# 2. Add synthetic activity data (if you don't have real data)
def add_activity_data(row):
    signup_date = row['signup_date']
    days_since_signup = (datetime.now() - signup_date).days
    
    # Simulate user activity patterns
    active_days = min(days_since_signup, np.random.poisson(lam=0.3*days_since_signup))
    
    return {
        'last_active_date': signup_date + timedelta(days=np.random.randint(0, days_since_signup)),
        'total_sessions': max(1, np.random.poisson(lam=active_days*0.7)),
        'active_30day': np.random.random() > 0.6 if days_since_signup>30 else True
    }

activity_data = df.apply(add_activity_data, axis=1, result_type='expand')
df = pd.concat([df, activity_data], axis=1)

# 3. Retention Rate Calculation
def calculate_retention(df):
    # Convert dates to datetime if not already
    df['signup_date'] = pd.to_datetime(df['signup_date'])
    df['last_active_date'] = pd.to_datetime(df['last_active_date'])
    
    # Create cohorts by signup month
    df['cohort'] = df['signup_date'].dt.to_period('M')
    
    # Calculate current date (for 30-day active status)
    current_date = datetime.now()
    
    # Calculate months since signup
    df['months_since_signup'] = ((current_date - df['signup_date']).dt.days // 30).clip(upper=6)
    
    # Create retention matrix
    cohort_counts = df.groupby('cohort')['user_id'].nunique().rename('total_users')
    
    retention_data = []
    for cohort_month in df['cohort'].unique():
        for month_num in range(0, 7):  # 0-6 months tracking
            cohort_mask = (df['cohort'] == cohort_month)
            active_mask = ((current_date - df['last_active_date']).dt.days <= 30)
            
            retained_users = df[cohort_mask & active_mask & 
                              (df['months_since_signup'] >= month_num)].shape[0]
            
            retention_data.append({
                'cohort': cohort_month,
                'month_number': month_num,
                'retained_users': retained_users
            })
    
    retention_df = pd.DataFrame(retention_data)
    retention_pivot = retention_df.pivot(index='cohort', columns='month_number', values='retained_users')
    
    # Convert counts to percentages
    for i in range(1, 7):
        retention_pivot[i] = (retention_pivot[i] / retention_pivot[0]).round(3)
    
    return retention_pivot  # Return DataFrame instead of Styler

# 4. Generate and display retention matrix
retention_matrix = calculate_retention(df)
print("Retention Cohort Matrix (Monthly)")
print(retention_matrix)

# 5. Save enhanced data
df.to_excel("Business_analytical project\Cohort Analysis\enhanced_user_data_with_retention.xlsx", index=False)