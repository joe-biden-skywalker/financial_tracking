

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
with spending_tab:
    spending_df = filtered_df[filtered_df["Action"] == "Spend"]
    spending_df = spending_df[spending_df["Category"] != "Other"]

    if spending_df.empty:
        st.warning("No spending data available for the selected month.")
    else:
        st.subheader(f"Spending Breakdown - {selected_month}")

        # Aggregate and sort in descending order
        category_spending = spending_df.groupby("Category")["Amount"].sum().reset_index()
        category_spending = category_spending.sort_values(by="Amount", ascending=False)

        # Create bar chart
        fig = px.bar(
            category_spending,
            x="Category",
            y="Amount",
            title="Spending by Category",
            text=category_spending["Amount"].apply(lambda x: f"${x:,.2f}")  # Format as dollars
        )

        fig.update_traces(
            marker_color="lightblue",
            textposition="outside",
            textfont_size=12
        )

        fig.update_layout(
            xaxis_title="Category",
            yaxis_title="Total Spending ($)",
            xaxis_tickangle=-30,
            title_font_size=16,
            margin=dict(l=40, r=40, t=40, b=100)  # Prevent labels from getting cut off
        )

        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(spending_df)




# Income Overview
with income_tab:
    income_df = filtered_df[filtered_df["Action"] == "Income"]

    if income_df.empty:
        st.warning("No income data available for the selected month.")
    else:
        st.subheader(f"Income Breakdown - {selected_month}")

        # Aggregate income, make values absolute, and sort from highest to lowest
        income_sources = income_df.groupby("Description")["Amount"].sum().reset_index()
        income_sources["Amount"] = income_sources["Amount"].abs()
        income_sources = income_sources.sort_values(by="Amount", ascending=False)

        # Create bar chart
        fig = px.bar(
            income_sources, 
            x="Description", 
            y="Amount", 
            title="Income Sources",
            text=income_sources["Amount"].apply(lambda x: f"${x:,.2f}")  # Format labels as dollars
        )

        fig.update_traces(
            marker_color="green",
            textposition="outside",
            textfont_size=12
        )

        fig.update_layout(
            xaxis_title="Source",
            yaxis_title="Total Income ($)",
            xaxis_tickangle=-30,
            title_font_size=16,
            margin=dict(l=40, r=40, t=40, b=100)  # Prevent cut-off
        )

        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(income_sources)



# Savings Overview
with savings_tab:
    savings_df = filtered_df[filtered_df["Action"] == "Savings"]

    if savings_df.empty:
        st.warning("No savings data available for the selected month.")
    else:
        st.subheader(f"Savings Overview - {selected_month}")

        # Aggregate savings trend
        savings_trend = savings_df.groupby("Day")["Amount"].sum().reset_index()

        # Create line chart
        fig = px.line(
            savings_trend, 
            x="Day", 
            y="Amount", 
            title="Savings Over Time",
            markers=True  # Add data points
        )

        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=8)
        )

        fig.update_layout(
            xaxis_title="Day",
            yaxis_title="Total Savings ($)",
            title_font_size=16,
            margin=dict(l=40, r=40, t=40, b=40)  # Prevent cut-off
        )

        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(savings_df)


# Non-Categorized Transactions
with other_tab:
    other_df = filtered_df[filtered_df["Category"] == "Other"]
    
    if other_df.empty:
        st.warning("No non-categorized transactions available for the selected month.")
    else:
        st.subheader(f"Non-Categorized Transactions - {selected_month}")
        st.dataframe(other_df)
