import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

from utils.sms_processor import process_sms_data
from utils.transaction_categorizer import categorize_transactions
from utils.data_manager import load_data, save_data
from utils.visualization import create_cashflow_chart, create_investment_chart
from utils.notification import check_upcoming_bills
from utils.financial_analytics import (
    analyze_spending_patterns,
    get_budget_recommendations,
    generate_financial_insights
)

# Page configuration
st.set_page_config(
    page_title="Financial SMS Tracker",
    page_icon="💰",
    layout="wide"
)

# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = load_data()

# Main title
st.title("Financial SMS Tracker")

# Sidebar
st.sidebar.header("Data Import")
uploaded_file = st.sidebar.file_uploader("Upload SMS Data (CSV)", type=['csv'])

if uploaded_file is not None:
    # Load and display raw data structure
    df = pd.read_csv(uploaded_file)
    st.sidebar.write("CSV Columns:", df.columns.tolist())

    # Display sample data
    with st.expander("Preview Raw Data"):
        st.write("First few rows of uploaded data:", df.head())

    try:
        # Process new SMS data
        processed_data = process_sms_data(df)
        categorized_data = categorize_transactions(processed_data)

        # Update session state
        st.session_state.transactions = pd.concat([st.session_state.transactions, categorized_data])
        save_data(st.session_state.transactions)
        st.sidebar.success("Data processed successfully!")
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")

# Main dashboard
col1, col2 = st.columns(2)

with col1:
    st.subheader("Cash Flow Analysis")
    if not st.session_state.transactions.empty:
        cashflow_chart = create_cashflow_chart(st.session_state.transactions)
        st.plotly_chart(cashflow_chart, use_container_width=True)
    else:
        st.info("Upload SMS data to view cash flow analysis")

with col2:
    st.subheader("Investment Portfolio")
    if not st.session_state.transactions.empty:
        investment_chart = create_investment_chart(st.session_state.transactions)
        st.plotly_chart(investment_chart, use_container_width=True)
    else:
        st.info("Upload SMS data to view investment analysis")

# Transaction list
st.subheader("Recent Transactions")
if not st.session_state.transactions.empty:
    st.dataframe(
        st.session_state.transactions.sort_values('date', ascending=False).head(10),
        use_container_width=True
    )
else:
    st.info("No transactions to display")

# Financial Analytics Section
st.header("Financial Analytics & Insights")

if not st.session_state.transactions.empty:
    # Create tabs for different analytics views
    analytics_tab, insights_tab, budget_tab = st.tabs([
        "Spending Analytics", "Financial Insights", "Budget Recommendations"
    ])

    with analytics_tab:
        patterns = analyze_spending_patterns(st.session_state.transactions)

        if patterns:
            # Account Overview
            st.subheader("Account Overview")
            if 'account_insights' in patterns:
                account_metrics = patterns['account_insights'].get('account_metrics', {})
                cols = st.columns(len(account_metrics))
                for i, (account, metrics) in enumerate(account_metrics.items()):
                    with cols[i]:
                        st.metric(
                            f"{account} Activity",
                            f"₹{metrics['mean']:.2f} avg",
                            f"{metrics['debit_ratio']:.1f}% debits"
                        )

            # Monthly Trends
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Monthly Spending Trend")
                monthly_data = pd.Series(patterns['monthly_trend'])
                fig = px.line(
                    x=monthly_data.index,
                    y=monthly_data.values,
                    title="Monthly Spending"
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Category Distribution")
                if 'category_insights' in patterns:
                    category_sums = {
                        k: v['sum']
                        for k, v in patterns['category_insights'].items()
                    }
                    fig = px.bar(
                        x=list(category_sums.keys()),
                        y=list(category_sums.values()),
                        title="Spending by Category"
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # Account-wise Analysis
            st.subheader("Account-wise Analysis")
            if 'account_insights' in patterns:
                monthly_account = patterns['account_insights'].get('monthly_trends', {})
                if monthly_account:
                    df_account = pd.DataFrame(monthly_account)
                    fig = px.line(
                        df_account,
                        title="Monthly Trends by Account"
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # Unusual Transactions
            if patterns.get('unusual_transactions'):
                st.subheader("Unusual Transactions")
                for tx in patterns['unusual_transactions']:
                    st.warning(
                        f"Unusual amount (₹{tx['amount']:.2f}) on {tx['date']} "
                        f"for {tx['description']}"
                    )

    with insights_tab:
        insights = generate_financial_insights(st.session_state.transactions)

        # Group insights by account
        for account in st.session_state.transactions['account_type'].unique():
            st.subheader(f"📊 {account} Insights")
            account_insights = [i for i in insights if i.get('account') == account]

            for insight in account_insights:
                if insight['type'] == 'trend':
                    icon = "📈" if insight['impact'] == 'positive' else "📉"
                elif insight['type'] == 'category':
                    icon = "🎯"
                else:
                    icon = "💡"

                st.write(f"{icon} {insight['title']}")
                st.write(insight['description'])

                if 'details' in insight:
                    cols = st.columns(len(insight['details']))
                    for i, (cat, amount) in enumerate(insight['details'].items()):
                        with cols[i]:
                            st.metric(cat, f"₹{amount:.2f}")

    with budget_tab:
        recommendations = get_budget_recommendations(st.session_state.transactions)

        st.subheader("📊 Recommended Monthly Budgets")
        st.write("Based on your historical spending patterns")

        # Group recommendations by account type
        for account in set(data['account_type'] for data in recommendations.values()):
            st.subheader(f"{account} Budgets")
            account_recommendations = {
                k: v for k, v in recommendations.items()
                if v['account_type'] == account
            }

            for category, data in account_recommendations.items():
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.metric(
                        category,
                        f"₹{data['recommended_budget']:.2f}",
                        f"+{data['buffer_percentage']}%"
                    )
                with col2:
                    st.caption(f"Based on avg: ₹{data['based_on_average']:.2f}")
else:
    st.info("Upload transaction data to view analytics and insights")

# Upcoming bills
st.subheader("Upcoming Bills & Obligations")
if not st.session_state.transactions.empty:
    upcoming_bills = check_upcoming_bills(st.session_state.transactions)
    if upcoming_bills:
        for bill in upcoming_bills:
            st.warning(
                f"📅 {bill['description']} - Due on {bill['due_date']} "
                f"(Amount: ₹{bill['amount']})"
            )
    else:
        st.info("No upcoming bills detected")
else:
    st.info("Upload SMS data to view upcoming bills")

# Export data
if st.button("Export Data") and not st.session_state.transactions.empty:
    st.session_state.transactions.to_csv("financial_data_export.csv", index=False)
    st.success("Data exported successfully!")