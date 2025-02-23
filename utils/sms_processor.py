import pandas as pd
import numpy as np
from typing import Dict, List
import re

def process_sms_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process raw SMS data using ML models for classification
    """
    # Assuming df has columns: 'message', 'date', 'sender'
    processed_data = []
    
    for _, row in df.iterrows():
        # Extract transaction details using regex
        amount = extract_amount(row['message'])
        transaction_type = classify_transaction_type(row['message'])
        
        if amount:
            processed_data.append({
                'date': pd.to_datetime(row['date']),
                'amount': amount,
                'type': transaction_type,
                'description': extract_description(row['message']),
                'sender': row['sender'],
                'raw_message': row['message']
            })
    
    return pd.DataFrame(processed_data)

def extract_amount(message: str) -> float:
    """Extract transaction amount from SMS message"""
    # Common patterns for Indian/US/UK currency formats
    amount_pattern = r'(?:RS|INR|₹|\$|£)\s*(\d+(?:,\d+)*(?:\.\d{2})?)'
    match = re.search(amount_pattern, message, re.IGNORECASE)
    
    if match:
        # Remove commas and convert to float
        amount_str = match.group(1).replace(',', '')
        return float(amount_str)
    return None

def classify_transaction_type(message: str) -> str:
    """Classify transaction type using simple rules"""
    message = message.lower()
    
    if any(word in message for word in ['credited', 'received', 'refund']):
        return 'credit'
    elif any(word in message for word in ['debited', 'paid', 'spent']):
        return 'debit'
    return 'unknown'

def extract_description(message: str) -> str:
    """Extract transaction description from SMS"""
    # Common patterns for transaction descriptions
    patterns = [
        r'at\s+([A-Za-z0-9\s]+)(?=\s+on|$)',
        r'to\s+([A-Za-z0-9\s]+)(?=\s+on|$)',
        r'from\s+([A-Za-z0-9\s]+)(?=\s+on|$)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message)
        if match:
            return match.group(1).strip()
    
    return 'Uncategorized'
