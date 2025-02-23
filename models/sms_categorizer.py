from typing import Dict
import re

# SMS Type Patterns
SMS_TYPE_PATTERNS = {
    'debit': r"debited|debit|paid|withdrawn|spent",
    'credit': r"credited|credit|received|deposited|refund",
    'advisory': r"reminder|alert|notice|advice",
    'statement': r"statement|summary|monthly|quarterly"
}

# Account Type Patterns
ACCOUNT_TYPE_PATTERNS = {
    'bank': r"savings|current|account|acct|a/c|bank",
    'credit_card': r"credit\s*card|cc|creditcard|card\s*ending|card\s*no",
    'loan': r"loan|emi|mortgage|housing",
    'wallet': r"wallet|upi|paytm|phonepe",
    'investment': r"mutual\s*fund|stock|demat|trading|investment"
}

# SMS Subtype Patterns
SMS_SUBTYPE_PATTERNS = {
    'regular': r"transaction|payment|transfer",
    'alert': r"alert|warning|notify|reminder",
    'statement': r"statement|summary|balance",
    'promotional': r"offer|discount|cashback"
}

# Transaction Type Patterns
TRANSACTION_TYPE_PATTERNS = {
    'bill_payment': r"bill\s*payment|utility|electricity|water|gas|phone|mobile|recharge",
    'transfer': r"transfer|sent|neft|rtgs|imps",
    'shopping': r"purchase|shopping|store|mart|shop",
    'atm': r"atm|cash\s*withdrawal|cwdr",
    'subscription': r"subscription|recurring|membership",
    'cc_bill_payment': r"credit\s*card\s*bill|cc\s*bill|card\s*bill",
    'investment': r"investment|mutual\s*fund|stock|trading",
    'salary': r"salary|payroll|wage",
    'refund': r"refund|reversal|cashback",
    'tax': r"tax|gst|tds"
}

# Transaction Channel Patterns
TRANSACTION_CHANNEL_PATTERNS = {
    'upi': r"upi|@|vpa|phonepe|gpay",
    'netbanking': r"net\s*banking|online|web|internet\s*banking",
    'card': r"card|pos|swipe",
    'atm': r"atm|cash\s*withdrawal",
    'auto_debit': r"auto\s*debit|standing\s*instruction|mandate|ach|nach",
    'mobile_banking': r"mobile\s*banking|app"
}

def categorize_sms(message: str) -> Dict[str, str]:
    """
    Categorize SMS based on various patterns
    """
    message = message.lower()
    categories = {
        'sms_type': 'unknown',
        'account_type': 'unknown',
        'sms_subtype': 'unknown',
        'transaction_type': 'unknown',
        'transaction_channel': 'unknown'
    }
    
    # Categorize SMS Type
    for sms_type, pattern in SMS_TYPE_PATTERNS.items():
        if re.search(pattern, message, re.IGNORECASE):
            categories['sms_type'] = sms_type
            break
    
    # Categorize Account Type
    for acc_type, pattern in ACCOUNT_TYPE_PATTERNS.items():
        if re.search(pattern, message, re.IGNORECASE):
            categories['account_type'] = acc_type
            break
    
    # Categorize SMS Subtype
    for subtype, pattern in SMS_SUBTYPE_PATTERNS.items():
        if re.search(pattern, message, re.IGNORECASE):
            categories['sms_subtype'] = subtype
            break
    
    # Categorize Transaction Type
    for trans_type, pattern in TRANSACTION_TYPE_PATTERNS.items():
        if re.search(pattern, message, re.IGNORECASE):
            categories['transaction_type'] = trans_type
            break
    
    # Categorize Transaction Channel
    for channel, pattern in TRANSACTION_CHANNEL_PATTERNS.items():
        if re.search(pattern, message, re.IGNORECASE):
            categories['transaction_channel'] = channel
            break
    
    return categories
