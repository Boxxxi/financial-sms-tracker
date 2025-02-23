import pandas as pd
import numpy as np
from typing import Dict, List
import re

def process_sms_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process raw SMS data using ML models for classification
    """
    # Detect SMS text column
    text_columns = [col for col in df.columns if any(x in col.lower() for x in ['text', 'sms', 'message', 'body', 'content'])]
    date_columns = [col for col in df.columns if any(x in col.lower() for x in ['date', 'time', 'timestamp'])]
    sender_columns = [col for col in df.columns if any(x in col.lower() for x in ['sender', 'from', 'number', 'source'])]

    if not text_columns:
        raise ValueError("No SMS text column found in the data. Expected columns containing 'text', 'sms', 'message', 'body', or 'content'")

    text_col = text_columns[0]
    date_col = date_columns[0] if date_columns else None
    sender_col = sender_columns[0] if sender_columns else None

    processed_data = []

    for _, row in df.iterrows():
        # Extract transaction details using regex
        message_text = str(row[text_col])
        amount = extract_amount(message_text)
        transaction_type = classify_transaction_type(message_text)

        if amount:
            transaction_data = {
                'amount': amount,
                'type': transaction_type,
                'description': extract_description(message_text),
                'raw_message': message_text
            }

            # Add date if available
            if date_col:
                try:
                    transaction_data['date'] = pd.to_datetime(row[date_col])
                except:
                    transaction_data['date'] = pd.Timestamp.now()
            else:
                transaction_data['date'] = pd.Timestamp.now()

            # Add sender if available
            if sender_col:
                transaction_data['sender'] = row[sender_col]
            else:
                transaction_data['sender'] = 'Unknown'

            processed_data.append(transaction_data)

    if not processed_data:
        return pd.DataFrame(columns=['date', 'amount', 'type', 'description', 'sender', 'raw_message'])

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
    return 0.0  # Return 0.0 instead of None for better DataFrame handling

def classify_transaction_type(message: str) -> str:
    """Classify transaction type using simple rules"""
    message = message.lower()

    if any(word in message for word in ['credited', 'received', 'refund', 'credit']):
        return 'credit'
    elif any(word in message for word in ['debited', 'paid', 'spent', 'debit', 'payment']):
        return 'debit'
    return 'unknown'

def extract_description(message: str) -> str:
    """Extract transaction description from SMS"""
    # Common patterns for transaction descriptions
    patterns = [
        r'at\s+([A-Za-z0-9\s]+)(?=\s+on|$)',
        r'to\s+([A-Za-z0-9\s]+)(?=\s+on|$)',
        r'from\s+([A-Za-z0-9\s]+)(?=\s+on|$)',
        r'for\s+([A-Za-z0-9\s]+)(?=\s+on|$)'
    ]

    for pattern in patterns:
        match = re.search(pattern, message)
        if match:
            return match.group(1).strip()

    return 'Uncategorized'