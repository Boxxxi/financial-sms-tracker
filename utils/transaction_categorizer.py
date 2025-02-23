import pandas as pd
from typing import Dict
import re
from models.category_patterns import CATEGORY_PATTERNS

def categorize_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Categorize transactions based on description and patterns
    """
    df = df.copy()
    df['category'] = df['description'].apply(categorize_transaction)
    return df

def categorize_transaction(description: str) -> str:
    """
    Categorize a single transaction based on its description
    """
    description = description.lower()
    
    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, description, re.IGNORECASE):
                return category
    
    return "Others"

def get_category_summary(df: pd.DataFrame) -> Dict:
    """
    Generate summary statistics by category
    """
    summary = df.groupby('category').agg({
        'amount': ['sum', 'count'],
        'type': lambda x: (x == 'debit').sum()
    }).round(2)
    
    return summary.to_dict()
