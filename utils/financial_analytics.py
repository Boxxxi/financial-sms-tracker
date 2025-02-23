import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

def analyze_spending_patterns(df: pd.DataFrame) -> Dict:
    """
    Analyze spending patterns and trends
    """
    if df.empty:
        return {}
    
    # Ensure date is datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Filter debit transactions
    debits = df[df['type'] == 'debit']
    
    # Monthly spending analysis
    monthly_spending = debits.groupby([
        df['date'].dt.year,
        df['date'].dt.month
    ])['amount'].sum().tail(6)
    
    # Category-wise spending
    category_spending = debits.groupby('category')['amount'].agg([
        'sum', 'count', 'mean'
    ]).round(2)
    
    # Day-of-week analysis
    dow_spending = debits.groupby(df['date'].dt.day_name())['amount'].mean().round(2)
    
    # Identify unusual transactions (> 2 std dev from mean)
    mean_transaction = debits['amount'].mean()
    std_transaction = debits['amount'].std()
    unusual_transactions = debits[
        debits['amount'] > (mean_transaction + 2 * std_transaction)
    ][['date', 'amount', 'description', 'category']].to_dict('records')
    
    return {
        'monthly_trend': monthly_spending.to_dict(),
        'category_insights': category_spending.to_dict(),
        'day_of_week_pattern': dow_spending.to_dict(),
        'unusual_transactions': unusual_transactions,
        'average_transaction': mean_transaction,
        'spending_volatility': std_transaction
    }

def get_budget_recommendations(df: pd.DataFrame) -> Dict:
    """
    Generate budget recommendations based on historical data
    """
    if df.empty:
        return {}
    
    # Filter debit transactions
    debits = df[df['type'] == 'debit']
    
    # Calculate average monthly spending by category
    monthly_category = debits.groupby([
        'category',
        pd.Grouper(key='date', freq='M')
    ])['amount'].sum().reset_index()
    
    avg_monthly = monthly_category.groupby('category')['amount'].mean().round(2)
    
    # Calculate recommended budget (adding 10% buffer)
    recommendations = {
        category: {
            'recommended_budget': float(amount * 1.1),
            'based_on_average': float(amount),
            'buffer_percentage': 10
        }
        for category, amount in avg_monthly.items()
    }
    
    return recommendations

def generate_financial_insights(df: pd.DataFrame) -> List[Dict]:
    """
    Generate key financial insights and recommendations
    """
    if df.empty:
        return []
    
    insights = []
    
    # Calculate month-over-month spending change
    monthly_spending = df[df['type'] == 'debit'].groupby(
        pd.Grouper(key='date', freq='M')
    )['amount'].sum()
    
    if len(monthly_spending) >= 2:
        current_month = monthly_spending.iloc[-1]
        previous_month = monthly_spending.iloc[-2]
        change_percentage = ((current_month - previous_month) / previous_month * 100)
        
        insights.append({
            'type': 'trend',
            'title': 'Monthly Spending Trend',
            'description': f"Your spending has {'increased' if change_percentage > 0 else 'decreased'} "
                         f"by {abs(change_percentage):.1f}% compared to last month.",
            'impact': 'negative' if change_percentage > 0 else 'positive'
        })
    
    # Identify top spending categories
    top_categories = df[df['type'] == 'debit'].groupby('category')['amount'].sum().nlargest(3)
    
    insights.append({
        'type': 'category',
        'title': 'Top Spending Categories',
        'description': f"Your highest spending categories are: "
                      f"{', '.join(top_categories.index.tolist())}",
        'details': {cat: float(amt) for cat, amt in top_categories.items()}
    })
    
    # Identify potential savings areas
    recurring_payments = df[
        (df['type'] == 'debit') & 
        (df['transaction_type'].isin(['subscription', 'bill_payment']))
    ]
    
    if not recurring_payments.empty:
        total_recurring = recurring_payments['amount'].sum()
        insights.append({
            'type': 'savings',
            'title': 'Recurring Payment Analysis',
            'description': f"You spend ₹{total_recurring:.2f} on recurring payments. "
                         "Review subscriptions for potential savings.",
            'amount': float(total_recurring)
        })
    
    return insights
