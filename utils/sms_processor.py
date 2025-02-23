import pandas as pd
import numpy as np
from typing import Dict, List
import re
from datetime import datetime
from models.regex_patterns import REGEX_MAP, REGEX_MAP_PRE, REGEX_MAP_POST, TRANSACTION_PATTERNS

def process_sms_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process raw SMS data using ML models for classification
    """
    # Detect SMS text column
    text_columns = [col for col in df.columns if any(x in col.lower() for x in ['text', 'sms', 'message', 'body', 'content'])]
    date_columns = [col for col in df.columns if any(x in col.lower() for x in ['date', 'time', 'timestamp', 'time_in_millis'])]
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
        transaction_details = extract_transaction_details(message_text)

        if transaction_details.get('amount', 0) > 0:  # Only process if amount is found
            transaction_data = {
                'amount': transaction_details['amount'],
                'type': transaction_details['type'],
                'description': transaction_details['description'],
                'raw_message': message_text,
                'transaction_currency': transaction_details.get('currency', 'INR'),
                'upi_id': transaction_details.get('upi_id', ''),
                'reference_number': transaction_details.get('reference', ''),
                'transaction_time': transaction_details.get('time', ''),
                'mode': transaction_details.get('mode', 'unknown')
            }

            # Add date if available
            if date_col:
                try:
                    timestamp = row[date_col]
                    # Convert string to numeric if it's a string
                    if isinstance(timestamp, str):
                        timestamp = float(timestamp)

                    # Check if timestamp is in milliseconds (13 digits) or seconds (10 digits)
                    if timestamp > 1e12:  # Milliseconds
                        transaction_data['date'] = pd.Timestamp(timestamp, unit='ms')
                    else:  # Seconds
                        transaction_data['date'] = pd.Timestamp(timestamp, unit='s')
                except Exception as e:
                    # Fallback to current time if conversion fails
                    print(f"Date conversion error for {row[date_col]}: {str(e)}")
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
        return pd.DataFrame(columns=['date', 'amount', 'type', 'description', 'sender', 'raw_message',
                                   'transaction_currency', 'upi_id', 'reference_number', 'transaction_time', 'mode'])

    return pd.DataFrame(processed_data)

def extract_transaction_details(message: str) -> Dict:
    """
    Extract all transaction details from SMS using enhanced regex patterns
    """
    details = {
        'amount': 0,
        'type': 'unknown',
        'description': 'Uncategorized',
        'currency': 'INR',
        'upi_id': '',
        'reference': '',
        'time': '',
        'mode': 'unknown'
    }

    # Extract amount
    amount_match = re.search(REGEX_MAP_PRE['amount'], message, re.IGNORECASE)
    if amount_match:
        amount_str = amount_match.group(1).replace(',', '')
        try:
            details['amount'] = float(amount_str)
        except ValueError:
            pass

    # Extract transaction type
    if re.search(TRANSACTION_PATTERNS['debit'], message, re.IGNORECASE):
        details['type'] = 'debit'
    elif re.search(TRANSACTION_PATTERNS['credit'], message, re.IGNORECASE):
        details['type'] = 'credit'

    # Extract transaction mode
    if re.search(TRANSACTION_PATTERNS['upi'], message, re.IGNORECASE):
        details['mode'] = 'UPI'
    elif re.search(TRANSACTION_PATTERNS['netbanking'], message, re.IGNORECASE):
        details['mode'] = 'Net Banking'
    elif re.search(TRANSACTION_PATTERNS['creditcard'], message, re.IGNORECASE):
        details['mode'] = 'Credit Card'
    elif re.search(TRANSACTION_PATTERNS['autodebit'], message, re.IGNORECASE):
        details['mode'] = 'Auto Debit'

    # Extract UPI ID
    upi_match = re.search(REGEX_MAP_PRE['upiid'], message)
    if upi_match:
        details['upi_id'] = upi_match.group(1)

    # Extract transaction time
    time_match = re.search(REGEX_MAP_PRE['time'], message)
    if time_match:
        details['time'] = time_match.group(0)

    # Extract currency
    currency_match = re.search(REGEX_MAP_PRE['transactioncurrency'], message, re.IGNORECASE)
    if currency_match:
        details['currency'] = currency_match.group(1).upper()

    # Extract reference number
    ref_match = re.search(REGEX_MAP_POST['utrnumber'], message, re.IGNORECASE)
    if ref_match:
        details['reference'] = ref_match.group(0)

    # Extract description
    description = extract_description(message)
    if description:
        details['description'] = description

    return details

def extract_description(message: str) -> str:
    """Extract transaction description from SMS"""
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