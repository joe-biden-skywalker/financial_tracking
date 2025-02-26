import streamlit as st
import pandas as pd
import plotly.express as px

# Load data (Assuming data is in a CSV file named 'transactions.csv')
@st.cache_data
def load_data():
    df = pd.read_csv("Finances/Addakin/streamlit/finances.csv")  # Adjust filename if needed
    df["Date"] = pd.to_datetime(df["Date"])  # Convert to datetime
    df = df[df["Category"].isin(["CC Payment", "Venmo", "Other"]) == False]  # Exclude specified categories
    return df

df = load_data()

# Sidebar filter for month selection
df["Month"] = df["Date"].dt.strftime("%B")
month_order = ["December", "January", "February"]
selected_month = st.sidebar.selectbox("Select Month", month_order)
df = df[df["Month"] == selected_month]

# Main screen with tabs
tabs = st.tabs(["Spending Overview", "Income Overview", "Savings Overview", "Non-Categorized Transactions"])

# Spending Overview Tab
with tabs[0]:
    st.header("Spending Overview")
    spending_df = df[df["Type"] == "Expense"]
    fig = px.pie(spending_df, names="Category", values="Amount", title="Spending Breakdown")
    st.plotly_chart(fig)

# Income Overview Tab
with tabs[1]:
    st.header("Income Overview")
    income_df = df[df["Type"] == "Income"]
    fig = px.bar(income_df, x="Date", y="Amount", color="Category", title="Income Breakdown")
    st.plotly_chart(fig)

# Savings Overview Tab
with tabs[2]:
    st.header("Savings Overview")
    savings_df = df[df["Type"] == "Savings"]
    fig = px.line(savings_df, x="Date", y="Amount", title="Savings Trend")
    st.plotly_chart(fig)

# Non-Categorized Transactions Tab
with tabs[3]:
    st.header("Non-Categorized Transactions")
    other_df = pd.read_csv("Finances/Addakin/streamlit/finances.csv")  # Load original data again
    other_df = other_df[other_df["Category"] == "Other"]  # Only "Other" category
    other_df = other_df[other_df["Month"] == selected_month]  # Apply month filter
    st.dataframe(other_df)
