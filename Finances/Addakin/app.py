import streamlit as st
import pandas as pd
import plotly.express as px

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("Finances/Addakin/streamlit/finances.csv")
    
    # Ensure Date column is present and converted
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
    else:
        raise KeyError("No 'Date' column found in the CSV file.")
    
    # Extract Month as a separate column
    df["Month"] = df["Date"].dt.strftime("%B")

    # Exclude unwanted categories
    df = df[~df["Category"].isin(["CC Payment", "Venmo"])]

    return df

# Load data
df = load_data()

# Sidebar: Month filter
selected_month = st.sidebar.selectbox(
    "Filter by Month",
    options=["December", "January", "February"],
    index=0
)

# Apply month filter
df_filtered = df[df["Month"] == selected_month]

# Set page layout
st.set_page_config(page_title="Personal Finance Dashboard", layout="wide")
st.title("💰 Personal Finance Dashboard")

# Set up tabs
tab1, tab2, tab3, tab4 = st.tabs(["Spending Overview", "Income Overview", "Savings Overview", "Non-Categorized Transactions"])

### 🚀 SPENDING OVERVIEW
with tab1:
    st.header("💸 Spending Overview")
    spending_df = df_filtered[df_filtered["Category"] == "Spending"]

    # Spending Summary
    if not spending_df.empty:
        st.dataframe(spending_df)

        # Spending Trends Over Time
        spending_trends = spending_df.groupby(spending_df["Date"].dt.strftime("%b %d"))["Amount"].sum().reset_index()
        fig = px.line(spending_trends, x="Date", y="Amount", title="Spending Trends Over Time", markers=True)
        st.plotly_chart(fig)
    else:
        st.warning("No spending data available for the selected month.")

### 💰 INCOME OVERVIEW
with tab2:
    st.header("💰 Income Overview")
    income_df = df_filtered[df_filtered["Category"] == "Income"]

    # Income Summary
    if not income_df.empty:
        st.dataframe(income_df)

        # Income Trends
        income_trends = income_df.groupby(income_df["Date"].dt.strftime("%b %d"))["Amount"].sum().reset_index()
        fig = px.line(income_trends, x="Date", y="Amount", title="Income Trends Over Time", markers=True)
        st.plotly_chart(fig)
    else:
        st.warning("No income data available for the selected month.")

### 💾 SAVINGS OVERVIEW
with tab3:
    st.header("💾 Savings Overview")
    savings_df = df_filtered[df_filtered["Category"] == "Savings"]

    # Savings Summary
    if not savings_df.empty:
        st.dataframe(savings_df)

        # Savings Trends
        savings_trends = savings_df.groupby(savings_df["Date"].dt.strftime("%b %d"))["Amount"].sum().reset_index()
        fig = px.line(savings_trends, x="Date", y="Amount", title="Savings Trends Over Time", markers=True)
        st.plotly_chart(fig)
    else:
        st.warning("No savings data available for the selected month.")

### ❓ NON-CATEGORIZED TRANSACTIONS
with tab4:
    st.header("❓ Non-Categorized Transactions")
    uncategorized_df = df[df["Category"] == "Other"]

    if not uncategorized_df.empty:
        st.dataframe(uncategorized_df)
    else:
        st.warning("No non-categorized transactions found.")
