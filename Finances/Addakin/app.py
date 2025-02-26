

import streamlit as st
import pandas as pd
import plotly.express as px

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("Finances/Addakin/streamlit/finances.csv")
    df = df.dropna(subset=["Category"])  # Drop rows where Category is missing
    df = df[~df["Category"].isin(["CC Payment", "Venmo"])]  # Exclude CC Payments & Venmo
    return df

df = load_data()

# Set up Streamlit Layout
st.set_page_config(page_title="Personal Finance Dashboard", layout="wide")
st.title("💰 Personal Finance Dashboard")

# Sidebar: Filter by Month
months = ["December", "January", "February"]
selected_month = st.sidebar.selectbox("Select Month:", months, index=months.index("February"))

# Filter Data by Month
filtered_df = df[df["Month"] == selected_month]

# Create Tabs
spending_tab, income_tab, savings_tab, other_tab = st.tabs([
    "Spending Overview", "Income Overview", "Savings Overview", "Non-Categorized Transactions"
])

# Spending Overview
# Spending Overview
with spending_tab:
    spending_df = filtered_df[filtered_df["Action"] == "Spend"]
    spending_df = spending_df[spending_df["Category"] != "Other"]
    
    if spending_df.empty:
        st.warning("No spending data available for the selected month.")
    else:
        st.subheader(f"Spending Breakdown - {selected_month}")
        
        # Aggregate spending by category and sort in descending order
        category_spending = spending_df.groupby("Category")["Amount"].sum().reset_index()
        category_spending = category_spending.sort_values(by="Amount", ascending=False)  # Sort greatest to least

        # Create bar chart with dollar sign labels
        fig = px.bar(
            category_spending, 
            x="Category", 
            y="Amount", 
            title="Spending by Category",
            text=category_spending["Amount"].apply(lambda x: f"${x:,.2f}")  # Format labels as dollars
        )
        
        fig.update_traces(
            marker_color="steelblue",  # Consistent color
            textposition="outside",  # Move labels above bars
            textfont_size=12
        )

        fig.update_layout(
            xaxis_title="Category",
            yaxis_title="Total Amount ($)",
            xaxis_tickangle=-30,  # Rotate labels for readability
            title_font_size=16
        )

        st.plotly_chart(fig)
        st.dataframe(spending_df)



# Income Overview
with income_tab:
    income_df = filtered_df[filtered_df["Action"] == "Income"]
    
    if income_df.empty:
        st.warning("No income data available for the selected month.")
    else:
        st.subheader(f"Income Breakdown - {selected_month}")
        income_sources = income_df.groupby("Description")["Amount"].sum().reset_index()
        fig = px.bar(income_sources, x="Description", y="Amount", title="Income Sources")
        st.plotly_chart(fig)
        st.dataframe(income_df)

# Savings Overview
with savings_tab:
    savings_df = filtered_df[filtered_df["Action"] == "Savings"]
    
    if savings_df.empty:
        st.warning("No savings data available for the selected month.")
    else:
        st.subheader(f"Savings Overview - {selected_month}")
        savings_trend = savings_df.groupby("Day")["Amount"].sum().reset_index()
        fig = px.line(savings_trend, x="Day", y="Amount", title="Savings Over Time")
        st.plotly_chart(fig)
        st.dataframe(savings_df)

# Non-Categorized Transactions
with other_tab:
    other_df = filtered_df[filtered_df["Category"] == "Other"]
    
    if other_df.empty:
        st.warning("No non-categorized transactions available for the selected month.")
    else:
        st.subheader(f"Non-Categorized Transactions - {selected_month}")
        st.dataframe(other_df)
