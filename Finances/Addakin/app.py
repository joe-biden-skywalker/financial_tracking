import streamlit as st
import pandas as pd
import plotly.express as px

# ✅ Move this to the top
st.set_page_config(page_title="Personal Finance Dashboard", layout="wide")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("Finances/Addakin/streamlit/finances.csv")

    # Exclude unwanted categories
    df = df[~df["Category"].isin(["CC Payment", "Venmo"])]

    return df

# Load data
df = load_data()

# Sidebar: Month filter (December, January, February)
selected_month = st.sidebar.selectbox(
    "Filter by Month",
    options=["December", "January", "February"],
    index=0
)

# Apply month filter
df_filtered = df[df["Month"] == selected_month]

st.title("💰 Personal Finance Dashboard")

# Set up tabs
tab1, tab2, tab3, tab4 = st.tabs(["Spending Overview", "Income Overview", "Savings Overview", "Non-Categorized Transactions"])

### 🚀 SPENDING OVERVIEW
with tab1:
    st.header("💸 Spending Overview")
    # spending_df = df[df["Category"] == "Spend"]
    spending_df = df_filtered[df_filtered["Category"] == "Spend"]

    if not spending_df.empty:
        st.dataframe(spending_df)

        # Spending Summary by Category
        fig = px.bar(spending_df, x="Category", y="Amount", title="Spending Breakdown", color="Category")
        st.plotly_chart(fig)
    else:
        st.warning("No spending data available for the selected month.")

### 💰 INCOME OVERVIEW
with tab2:
    st.header("💰 Income Overview")
    income_df = df_filtered[df_filtered["Category"] == "Income"]

    if not income_df.empty:
        st.dataframe(income_df)

        # Income Summary
        fig = px.pie(income_df, names="Category", values="Amount", title="Income Distribution")
        st.plotly_chart(fig)
    else:
        st.warning("No income data available for the selected month.")

### 💾 SAVINGS OVERVIEW
with tab3:
    st.header("💾 Savings Overview")
    savings_df = df_filtered[df_filtered["Category"] == "Savings"]

    if not savings_df.empty:
        st.dataframe(savings_df)

        # Savings Breakdown
        fig = px.line(savings_df, x="Month", y="Amount", title="Savings Trend", markers=True)
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
