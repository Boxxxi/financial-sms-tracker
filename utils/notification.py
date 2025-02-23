import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict

def check_upcoming_bills(df: pd.DataFrame) -> List[Dict]:
    """
    Check for upcoming bills and obligations
    """
    # Filter recurring transactions
    recurring = identify_recurring_transactions(df)
    
    # Predict next due dates
    upcoming = []
    today = datetime.now()
    
    for _, row in recurring.iterrows():
        next_date = predict_next_due_date(row['date'], row['frequency'])
        
        if next_date and (next_date - today).days <= 7:
            upcoming.append({
                'description': row['description'],
                'amount': row['amount'],
                'due_date': next_date.strftime('%Y-%m-%d'),
                'days_left': (next_date - today).days
            })
    
    return sorted(upcoming, key=lambda x: x['days_left'])

def identify_recurring_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify recurring transactions and their frequency
    """
    # Group similar transactions
    recurring = df.groupby('description').agg({
        'date': list,
        'amount': 'mean'
    }).reset_index()
    
    # Calculate frequency for each group
    recurring['frequency'] = recurring['date'].apply(calculate_frequency)
    
    return recurring[recurring['frequency'].notna()]

def calculate_frequency(dates: List) -> str:
    """
    Calculate the frequency of recurring transactions
    """
    if len(dates) < 2:
        return None
    
    dates = sorted(dates)
    intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
    avg_interval = sum(intervals) / len(intervals)
    
    if 25 <= avg_interval <= 35:
        return 'monthly'
    elif 85 <= avg_interval <= 95:
        return 'quarterly'
    elif 350 <= avg_interval <= 380:
        return 'yearly'
    
    return None

def predict_next_due_date(dates: List, frequency: str) -> datetime:
    """
    Predict next due date based on transaction history
    """
    if not dates or not frequency:
        return None
    
    last_date = max(dates)
    
    if frequency == 'monthly':
        return last_date + timedelta(days=30)
    elif frequency == 'quarterly':
        return last_date + timedelta(days=90)
    elif frequency == 'yearly':
        return last_date + timedelta(days=365)
    
    return None
