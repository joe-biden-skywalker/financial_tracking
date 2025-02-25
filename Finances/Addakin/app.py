import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

# Define file path dynamically
csv_file = "/Users/addakinthomas/Desktop/Finances/Addakin/streamlit/finances.csv"
feedback_folder = "feedback"
feedback_file = os.path.join(feedback_folder, "feedback.txt")

# Load CSV data safely
def load_data():
    try:
        df = pd.read_csv(csv_file)
        df.columns = df.columns.str.lower().str.strip()  # Normalize column names to lowercase and remove spaces
        return df
    except FileNotFoundError:
        return None

# Create feedback directory if not exists
if not os.path.exists(feedback_folder):
    os.makedirs(feedback_folder)

# Streamlit UI
st.set_page_config(layout="wide")
st.title("📊 Addakin's Financial Overview")

df = load_data()

if df is None:
    st.error(f"❌ CSV file not found at: {csv_file}")
else:
    months_ordered = ["January", "February", "March", "April", "May", "June", "July", 
                      "August", "September", "October", "November", "December"]

    # Standardize 'month' column
    df['month'] = df['month'].str.capitalize()

    # Sidebar Filters (Remove "All" option)
    st.sidebar.header("📅 Filter by Month")
    selected_month = st.sidebar.radio("Select a month", months_ordered)

    # **Create a filtered copy for transactions (but NOT for YTD Chart)**
    filtered_df = df[df['month'] == selected_month]

    # Categorize "Other"
    df.loc[df['category'].str.lower() == 'other', 'category'] = 'Other'
    uncategorized_df = df[df['category'] == 'Other']
    df = df[df['category'] != 'Other']

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💸 Spending", "💰 Saving", "📈 Income", "❓ Uncategorized Transactions"])

    with tab1:
        st.subheader(f"📊 Spending Analysis - {selected_month}")

        spending_df = filtered_df[filtered_df['action'].str.lower() == 'spend']
        
        if not spending_df.empty:
            # **Spending Breakdown Analysis**
            category_spending = spending_df.groupby('category')['amount'].sum().sort_values(ascending=False)

            # **Create two columns for side-by-side charts**
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("💰 Spending per Category")

                # Improve readability by increasing figure size
                fig, ax = plt.subplots(figsize=(10, 5))

                # Sort categories by spending (descending order)
                category_spending = category_spending.sort_values(ascending=True)

                # Use a better color palette
                colors = plt.cm.Paired.colors  

                # Create bar plot
                category_spending.plot(
                    kind="barh",
                    ax=ax,
                    color=colors,
                    alpha=0.8  # Slight transparency for aesthetic appeal
                )

                ax.set_xlabel("Total Spent ($)")
                ax.set_ylabel("Category")
                ax.set_title(f"Total Spending by Category ({selected_month})")

                # Add data labels
                for i, value in enumerate(category_spending):
                    ax.text(value + 50, i, f"${value:,.0f}", va="center", fontsize=10, fontweight="bold")

                # Improve layout
                plt.grid(axis="x", linestyle="--", alpha=0.5)
                plt.tight_layout()
                st.pyplot(fig)


            with col2:
                st.subheader("📊 Spending Distribution")

                # Improve readability by increasing figure size and adjusting labels
                fig, ax = plt.subplots(figsize=(8, 6))  # Larger figure
                colors = plt.cm.Paired.colors  # Distinct color palette
                explode = [0.1 if pct > 10 else 0 for pct in category_spending / category_spending.sum() * 100]  # Explode big slices

                category_spending.plot(
                    kind="pie",
                    ax=ax,
                    autopct='%1.1f%%',  # Show percentages
                    startangle=140,
                    cmap="coolwarm",
                    pctdistance=0.85,  # Moves % labels closer to center
                    colors=colors,
                    explode=explode
                )

                ax.set_ylabel("")  # Hide y-axis label
                ax.set_title(f"Spending Breakdown by Category ({selected_month})")

                # Improve label placement
                plt.tight_layout()
                st.pyplot(fig)


            # **Full-Width YTD Line Chart**
            st.subheader("📈 Year-To-Date (YTD) Spending Trends")

            # Aggregate spending per category per month (full year)
            ytd_spending = df[df['action'].str.lower() == 'spend'].groupby(['month', 'category'])['amount'].sum().unstack()

            # Reorder months based on the defined sequence
            ytd_spending = ytd_spending.reindex(months_ordered)

            # **Line Chart (YTD)**
            fig, ax = plt.subplots(figsize=(12, 6))
            ytd_spending.plot(kind='line', marker='o', ax=ax)
            ax.set_ylabel("Total Spent ($)")
            ax.set_xlabel("Month")
            ax.set_title("YTD Spending Trends by Category")
            plt.xticks(rotation=45)
            plt.legend(title="Category", bbox_to_anchor=(1.05, 1), loc='upper left')
            st.pyplot(fig)

            # **Spending Transactions Table (Bottom)**
            st.subheader(f"📑 Spending Transactions - {selected_month}")
            st.dataframe(spending_df)

        else:
            st.warning(f"⚠️ No spending transactions found for {selected_month}.")

    with tab2:
        st.subheader(f"💰 Saving Transactions - {selected_month}")
        saving_df = filtered_df[filtered_df['action'].str.lower() == 'save']
        if not saving_df.empty:
            st.dataframe(saving_df)
        else:
            st.warning(f"⚠️ No saving transactions found for {selected_month}.")

    with tab3:
        st.subheader(f"📈 Income Transactions - {selected_month}")
        income_df = filtered_df[filtered_df['action'].str.lower() == 'income']
        if not income_df.empty:
            st.dataframe(income_df)
        else:
            st.warning(f"⚠️ No income transactions found for {selected_month}.")

    with tab4:
        st.subheader(f"❓ Uncategorized Transactions - {selected_month}")
        if not uncategorized_df.empty:
            st.dataframe(uncategorized_df)
        else:
            st.warning(f"⚠️ No uncategorized transactions found for {selected_month}.")

    # Feedback Section
    st.sidebar.subheader("💡 Feedback & Suggestions")
    feedback_text = st.sidebar.text_area("How can we improve this dashboard?")
    if st.sidebar.button("Submit Feedback"):
        with open(feedback_file, "a") as f:
            f.write(feedback_text + "\n")
        st.sidebar.success("✅ Thank you for your feedback!")
