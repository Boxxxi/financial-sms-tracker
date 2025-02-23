import pandas as pd
import json
from datetime import datetime
import os

def load_data() -> pd.DataFrame:
    """
    Load transaction data from storage
    """
    try:
        if os.path.exists('data/transactions.csv'):
            df = pd.read_csv('data/transactions.csv')
            df['date'] = pd.to_datetime(df['date'])
            return df
    except Exception as e:
        print(f"Error loading data: {e}")
    
    # Return empty DataFrame if no data exists
    return pd.DataFrame(columns=[
        'date', 'amount', 'type', 'description', 
        'category', 'sender', 'raw_message'
    ])

def save_data(df: pd.DataFrame) -> None:
    """
    Save transaction data to storage
    """
    try:
        os.makedirs('data', exist_ok=True)
        df.to_csv('data/transactions.csv', index=False)
    except Exception as e:
        print(f"Error saving data: {e}")

def export_data(df: pd.DataFrame, format: str = 'csv') -> str:
    """
    Export data in specified format
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format == 'csv':
        filename = f'financial_export_{timestamp}.csv'
        df.to_csv(filename, index=False)
    elif format == 'json':
        filename = f'financial_export_{timestamp}.json'
        df.to_json(filename, orient='records')
    
    return filename
