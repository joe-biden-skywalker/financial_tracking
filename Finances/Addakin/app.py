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
        st.subheader(f"💸 Spending Breakdown - {selected_month}")

        # 📌 Aggregate spending by category
        category_spending = spending_df.groupby("Category")["Amount"].sum().reset_index()
        category_spending = category_spending.sort_values(by="Amount", ascending=False)  # Sort descending

        # 📊 Layout: Bar Chart & Pie Chart side by side
        col1, col2 = st.columns(2)

        # 📊 Bar Chart: Spending by Category
        with col1:
            fig_bar = px.bar(
                category_spending,
                x="Category",
                y="Amount",
                title="Spending by Category",
                text=category_spending["Amount"].apply(lambda x: f"${x:,.2f}"),
            )
            fig_bar.update_traces(textposition="outside")
            fig_bar.update_layout(
                xaxis_title="Category",
                yaxis_title="Total Amount ($)",
                title_font_size=16,
                margin=dict(l=40, r=40, t=40, b=100),
                xaxis=dict(categoryorder="total descending"),  # Ensure sorting from highest to lowest
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # 🥧 Pie Chart: Monthly Spending Breakdown
        with col2:
            fig_pie = px.pie(
                category_spending,
                names="Category",
                values="Amount",
                title="Monthly Spending Breakdown",
                hole=0.4,  # Donut-style
            )
            fig_pie.update_traces(
                textinfo="percent+label",
                hoverinfo="label+percent+value",
            )
            fig_pie.update_layout(
                title_font_size=16,
                margin=dict(l=40, r=40, t=40, b=100),
                showlegend=True,
            )
            st.plotly_chart(fig_pie, use_container_width=True)

# 📌 Top 5 Transactions Per Category
st.subheader("🏆 Top 5 Transactions Per Category")

# Create a horizontal selection for categories
categories = df["Category"].unique().tolist()
selected_category = st.radio("Select a Category:", categories, horizontal=True)

# Filter data for the selected category
top_transactions = df[df["Category"] == selected_category].nlargest(5, "Amount")

# Display the table
st.dataframe(top_transactions, use_container_width=True)

# 📌 YTD Spending Line Chart (NOT Impacted by Filter)
st.subheader("📊 Year-to-Date (YTD) Spending Trends (January & February)")

# Filter dataset to only include January & February spending
ytd_spending_df = df[(df["Action"] == "Spend") & (df["Month"].isin(["January", "February"]))]

if ytd_spending_df.empty:
    st.warning("No YTD spending data available.")
else:
    # Aggregate spending per category per month
    ytd_spending = ytd_spending_df.groupby(["Month", "Category"])["Amount"].sum().reset_index()

    # Sort months correctly
    ytd_spending["Month"] = pd.Categorical(ytd_spending["Month"], categories=["January", "February"], ordered=True)

    # Create line chart
    fig_ytd = px.line(
        ytd_spending,
        x="Month",
        y="Amount",
        color="Category",  # Different lines for each category
        title="YTD Spending Trends by Category (Jan & Feb)",
        markers=True,  # Add markers at data points
    )

    fig_ytd.update_traces(
        text=ytd_spending["Amount"].apply(lambda x: f"${x:,.2f}"),  # Format as dollars
        textposition="top center"
    )

    fig_ytd.update_layout(
        xaxis_title="Month",
        yaxis_title="Total Spending ($)",
        title_font_size=16,
        margin=dict(l=40, r=40, t=40, b=100),  # Prevent labels from getting cut off
        legend_title="Category",
        xaxis=dict(tickmode="array", tickvals=["January", "February"]),  # Ensure proper month labels
    )

    st.plotly_chart(fig_ytd, use_container_width=True)  # Removed st.dataframe(ytd_spending)

    # 📌 Interactive Transactions Table at the Bottom
    st.subheader("📜 Explore All Transactions")
    st.dataframe(df, use_container_width=True)

    
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
