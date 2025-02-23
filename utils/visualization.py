import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_cashflow_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create cash flow visualization
    """
    if df.empty:
        # Return empty figure with message if no data
        fig = go.Figure()
        fig.add_annotation(
            text="No transaction data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False
        )
        return fig

    # Calculate daily net cash flow
    df['date'] = pd.to_datetime(df['date'])
    daily_flow = df.groupby(['date', 'type'])['amount'].sum().unstack(fill_value=0)

    # Ensure credit and debit columns exist
    if 'credit' not in daily_flow.columns:
        daily_flow['credit'] = 0
    if 'debit' not in daily_flow.columns:
        daily_flow['debit'] = 0

    daily_flow['net'] = daily_flow['credit'] - daily_flow['debit']

    fig = go.Figure()

    # Add credit line
    fig.add_trace(go.Scatter(
        x=daily_flow.index.tolist(),
        y=daily_flow['credit'].tolist(),
        name='Income',
        line=dict(color='green'),
        fill='none'
    ))

    # Add debit line
    fig.add_trace(go.Scatter(
        x=daily_flow.index.tolist(),
        y=(-daily_flow['debit']).tolist(),
        name='Expenses',
        line=dict(color='red'),
        fill='none'
    ))

    # Add net flow line
    fig.add_trace(go.Scatter(
        x=daily_flow.index.tolist(),
        y=daily_flow['net'].tolist(),
        name='Net Flow',
        line=dict(color='blue', dash='dot'),
        fill='none'
    ))

    fig.update_layout(
        title='Daily Cash Flow',
        xaxis_title='Date',
        yaxis_title='Amount',
        hovermode='x unified',
        showlegend=True
    )

    return fig

def create_investment_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create investment portfolio visualization
    """
    if df.empty:
        # Return empty figure with message if no data
        fig = go.Figure()
        fig.add_annotation(
            text="No investment data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False
        )
        return fig

    # Filter investment transactions
    investments = df[df['category'] == 'Investments'].copy()
    if investments.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No investment transactions found",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False
        )
        return fig

    # Ensure date is datetime
    investments['date'] = pd.to_datetime(investments['date'])

    # Calculate cumulative investments by type
    investments_by_type = investments.groupby(['description', 'date'])['amount'].sum().reset_index()

    fig = px.line(
        investments_by_type,
        x='date',
        y='amount',
        color='description',
        title='Investment Portfolio Growth'
    )

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Amount Invested',
        hovermode='x unified',
        showlegend=True
    )

    return fig