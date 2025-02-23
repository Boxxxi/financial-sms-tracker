import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

from utils.sms_processor import process_sms_data
from utils.transaction_categorizer import categorize_transactions
from utils.data_manager import load_data, save_data
from utils.visualization import create_cashflow_chart, create_investment_chart
from utils.notification import check_upcoming_bills

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
    # Process new SMS data
    df = pd.read_csv(uploaded_file)
    processed_data = process_sms_data(df)
    categorized_data = categorize_transactions(processed_data)
    
    # Update session state
    st.session_state.transactions = pd.concat([st.session_state.transactions, categorized_data])
    save_data(st.session_state.transactions)
    st.sidebar.success("Data processed successfully!")

# Main dashboard
col1, col2 = st.columns(2)

with col1:
    st.subheader("Cash Flow Analysis")
    cashflow_chart = create_cashflow_chart(st.session_state.transactions)
    st.plotly_chart(cashflow_chart, use_container_width=True)

with col2:
    st.subheader("Investment Portfolio")
    investment_chart = create_investment_chart(st.session_state.transactions)
    st.plotly_chart(investment_chart, use_container_width=True)

# Transaction list
st.subheader("Recent Transactions")
st.dataframe(
    st.session_state.transactions.sort_values('date', ascending=False).head(10),
    use_container_width=True
)

# Upcoming bills
st.subheader("Upcoming Bills & Obligations")
upcoming_bills = check_upcoming_bills(st.session_state.transactions)
for bill in upcoming_bills:
    st.warning(f"📅 {bill['description']} - Due on {bill['due_date']} (Amount: ${bill['amount']})")

# Export data
if st.button("Export Data"):
    st.session_state.transactions.to_csv("financial_data_export.csv", index=False)
    st.success("Data exported successfully!")
