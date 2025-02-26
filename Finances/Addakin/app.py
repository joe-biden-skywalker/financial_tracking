import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
@st.cache_data
def load_data():
    finances = pd.read_csv("finances.csv")
    spending_categories = pd.read_csv("spending_categories.csv")
    
    # Exclude "CC Payments" and "Venmo"
    finances = finances[~finances['Category'].isin(["CC Payments", "Venmo"])]
    
    return finances, spending_categories

finances, spending_categories = load_data()

# Page layout
st.set_page_config(page_title="Personal Finance Dashboard", layout="wide")
st.title("💰 Personal Finance Dashboard")

# Create tabs
tabs = ["Spending Overview", "Income Overview", "Savings Overview", "Non-Categorized Transactions"]
selected_tab = st.sidebar.radio("Select a Tab", tabs)

# Spending Overview Tab
if selected_tab == "Spending Overview":
    st.header("📊 Spending Overview")
    
    # Filter spending transactions
    spending_df = finances[finances['Action'] == "Spend"]
    
    # Spending summary table
    st.dataframe(spending_df)
    
    # Spending breakdown by category
    category_spending = spending_df.groupby("Category")["Amount"].sum().reset_index()
    fig = px.pie(category_spending, names='Category', values='Amount', title='Spending by Category')
    st.plotly_chart(fig)
    
    # Spending trends over time
    spending_trends = spending_df.groupby("Month & Day")["Amount"].sum().reset_index()
    fig2 = px.line(spending_trends, x='Month & Day', y='Amount', title='Spending Trends Over Time')
    st.plotly_chart(fig2)

# Income Overview Tab
elif selected_tab == "Income Overview":
    st.header("📈 Income Overview")
    
    # Filter income transactions
    income_df = finances[finances['Action'] == "Income"]
    
    # Income summary table
    st.dataframe(income_df)
    
    # Income breakdown
    income_summary = income_df.groupby("Category")["Amount"].sum().reset_index()
    fig = px.bar(income_summary, x='Category', y='Amount', title='Income by Category')
    st.plotly_chart(fig)

# Savings Overview Tab
elif selected_tab == "Savings Overview":
    st.header("💾 Savings Overview")
    
    # Filter savings transactions (assuming savings have specific categories)
    savings_categories = ["Savings", "Investment", "Retirement"]
    savings_df = finances[finances['Category'].isin(savings_categories)]
    
    st.dataframe(savings_df)
    
    # Savings trends
    savings_trends = savings_df.groupby("Month & Day")["Amount"].sum().reset_index()
    fig = px.line(savings_trends, x='Month & Day', y='Amount', title='Savings Trends Over Time')
    st.plotly_chart(fig)

# Non-Categorized Transactions Tab
elif selected_tab == "Non-Categorized Transactions":
    st.header("🛠 Non-Categorized Transactions")
    
    # Filter non-categorized transactions
    uncategorized_df = finances[finances['Category'].isna() | (finances['Category'] == "")]
    
    st.dataframe(uncategorized_df)
