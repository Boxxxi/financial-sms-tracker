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
    monthly_spending = debits.groupby(
        debits['date'].dt.strftime('%Y-%m')
    )['amount'].sum().sort_index().tail(6)

    # Category-wise spending
    category_spending = debits.groupby('category')['amount'].agg([
        'sum', 'count', 'mean'
    ]).round(2)

    # Account-wise analysis
    account_analysis = analyze_account_patterns(df)

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
        'account_insights': account_analysis,
        'day_of_week_pattern': dow_spending.to_dict(),
        'unusual_transactions': unusual_transactions,
        'average_transaction': mean_transaction,
        'spending_volatility': std_transaction
    }

def analyze_account_patterns(df: pd.DataFrame) -> Dict:
    """
    Analyze patterns across different accounts
    """
    # Account-wise spending analysis
    account_spending = df.groupby(['account_type', 'type'])['amount'].agg([
        'sum', 'count', 'mean'
    ]).round(2)

    # Transaction frequency by account
    account_frequency = df.groupby('account_type').agg({
        'amount': ['count', 'mean', 'std'],
        'type': lambda x: (x == 'debit').mean() * 100  # Percentage of debits
    }).round(2)

    # Monthly trends by account
    monthly_by_account = df.groupby([
        'account_type',
        df['date'].dt.strftime('%Y-%m')
    ])['amount'].sum().unstack().fillna(0)

    return {
        'spending_by_account': account_spending.to_dict(),
        'account_metrics': account_frequency.to_dict(),
        'monthly_trends': monthly_by_account.to_dict()
    }

def get_budget_recommendations(df: pd.DataFrame) -> Dict:
    """
    Generate budget recommendations based on historical data
    """
    if df.empty:
        return {}

    # Filter debit transactions
    debits = df[df['type'] == 'debit']

    # Calculate average monthly spending by category and account
    monthly_spending = debits.groupby([
        'category',
        'account_type',
        pd.Grouper(key='date', freq='M')
    ])['amount'].sum().reset_index()

    # Calculate recommendations by category and account
    avg_monthly = monthly_spending.groupby(['category', 'account_type'])['amount'].mean().round(2)

    recommendations = {}
    for (category, account), amount in avg_monthly.items():
        key = f"{category} ({account})"
        recommendations[key] = {
            'recommended_budget': float(amount * 1.1),
            'based_on_average': float(amount),
            'buffer_percentage': 10,
            'account_type': account
        }

    return recommendations

def generate_financial_insights(df: pd.DataFrame) -> List[Dict]:
    """
    Generate key financial insights and recommendations
    """
    if df.empty:
        return []

    insights = []

    # Calculate month-over-month spending change by account
    monthly_by_account = df[df['type'] == 'debit'].groupby([
        'account_type',
        pd.Grouper(key='date', freq='M')
    ])['amount'].sum().unstack()

    for account in monthly_by_account.index:
        spending = monthly_by_account.loc[account]
        if len(spending.dropna()) >= 2:
            current_month = spending.iloc[-1]
            previous_month = spending.iloc[-2]
            change_percentage = ((current_month - previous_month) / previous_month * 100)

            insights.append({
                'type': 'trend',
                'account': account,
                'title': f'{account} Spending Trend',
                'description': f"Your {account} spending has {'increased' if change_percentage > 0 else 'decreased'} "
                             f"by {abs(change_percentage):.1f}% compared to last month.",
                'impact': 'negative' if change_percentage > 0 else 'positive'
            })

    # Identify top spending categories by account
    for account in df['account_type'].unique():
        account_data = df[
            (df['account_type'] == account) & 
            (df['type'] == 'debit')
        ]
        if not account_data.empty:
            top_categories = account_data.groupby('category')['amount'].sum().nlargest(3)

            insights.append({
                'type': 'category',
                'account': account,
                'title': f'Top {account} Spending Categories',
                'description': f"Your highest spending categories for {account} are: "
                             f"{', '.join(top_categories.index.tolist())}",
                'details': {cat: float(amt) for cat, amt in top_categories.items()}
            })

    # Analyze recurring payments by account
    for account in df['account_type'].unique():
        recurring_payments = df[
            (df['account_type'] == account) &
            (df['type'] == 'debit') & 
            (df['transaction_type'].isin(['subscription', 'bill_payment']))
        ]

        if not recurring_payments.empty:
            total_recurring = recurring_payments['amount'].sum()
            insights.append({
                'type': 'savings',
                'account': account,
                'title': f'{account} Recurring Payments',
                'description': f"You spend ₹{total_recurring:.2f} on recurring payments from your {account}. "
                             "Review subscriptions for potential savings.",
                'amount': float(total_recurring)
            })

    return insights