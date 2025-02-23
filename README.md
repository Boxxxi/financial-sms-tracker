# Financial SMS Tracker

A financial tracking application that processes SMS data for monitoring cash flow, investments, and obligations. The application uses machine learning and regex patterns to analyze SMS messages and provide insights into your financial transactions.

## Features

- SMS Processing with advanced regex pattern matching
- Transaction categorization (SMS type, account type, transaction type, etc.)
- Cash flow visualization
- Investment portfolio tracking
- Upcoming bills and obligations monitoring
- Real-time data processing
- Interactive Streamlit interface

## Requirements

- Python 3.11
- Required packages: pandas, streamlit, plotly, numpy
- SMS data in CSV format

## Usage

1. Run the Streamlit application:
```bash
streamlit run main.py
```

2. Upload your SMS data in CSV format through the web interface
3. View processed transactions, visualizations, and insights
4. Monitor upcoming bills and obligations

## SMS Data Format

The application expects SMS data in CSV format with the following columns:
- Text/message/content column containing the SMS text
- Date/timestamp column (optional)
- Sender information (optional)

## Categories Extracted

The application extracts and categorizes the following information from SMS messages:

1. SMS Type:
   - Debit
   - Credit
   - Advisory
   - Statement

2. Account Type:
   - Bank
   - Credit Card
   - Loan
   - Wallet
   - Investment

3. Transaction Type:
   - Bill Payment
   - Transfer
   - Shopping
   - ATM
   - Subscription
   - Credit Card Bill Payment
   - Investment
   - Salary
   - Refund
   - Tax

4. Transaction Channel:
   - UPI
   - Net Banking
   - Card
   - ATM
   - Auto Debit
   - Mobile Banking
