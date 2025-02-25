import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

# Define file path dynamically
desktop_folder = os.path.expanduser("~/Desktop/Finances/Data")
csv_file = os.path.join(desktop_folder, "curated_finances.csv")

# Load CSV data safely
def load_data():
    try:
        df = pd.read_csv(csv_file)
        return df
    except FileNotFoundError:
        return None

# Streamlit UI
st.set_page_config(layout="wide")
st.title("📊 Addakin's Financial Overview")

# Load data
df = load_data()

if df is None:
    st.error(f"❌ CSV file not found at: `{csv_file}`")
else:
    # Normalize column names to lowercase for consistency
    df.columns = df.columns.str.lower()
    
    # Sidebar with non-collapsable checkboxes ordered by December, January, February
    st.sidebar.header("📅 Filter by Month")
    months_ordered = ["December", "January", "February"]
    available_months = [month for month in months_ordered if month.lower() in df['month'].dropna().str.lower().unique()]
    selected_month = st.sidebar.radio("Select a month", available_months)
    
    if selected_month:
        df = df[df['month'].str.lower() == selected_month.lower()]
    
    # Move Peer-to-Peer Payments and Other - Miscellaneous to 'Other' category
    if 'category' in df.columns:
        df.loc[df['category'].str.lower().isin(['peer-to-peer payment', 'other - miscellaneous']), 'category'] = 'Other'
    
    # Separate Uncategorized Transactions
    if 'category' in df.columns:
        uncategorized_df = df[df['category'].str.lower() == 'other']
        df = df[df['category'].str.lower() != 'other']
    else:
        uncategorized_df = pd.DataFrame()
    
    # Create Tabs
    tab1, tab2, tab3 = st.tabs(["💸 Spending", "💰 Saving", "❓ Uncategorized Transactions"])
    
    with tab1:
        st.subheader("📊 Spending by Category")
        if 'category' in df.columns and 'amount' in df.columns:
            category_spending = df.groupby('category')['amount'].sum().sort_values()
            fig, ax = plt.subplots()
            bars = ax.barh(category_spending.index, category_spending.values)
            ax.set_xlabel("Total Spending ($)")
            ax.set_ylabel("Category")
            ax.set_title("Spending by Category")
            
            # Add labels to bars
            for bar in bars:
                ax.text(bar.get_width(), bar.get_y() + bar.get_height()/2, f"${bar.get_width():,.2f}", va='center')
            
            st.pyplot(fig)
        else:
            st.warning("⚠️ Missing 'Category' or 'Amount' column in data.")
        
        st.subheader("💰 Top 10 Purchases Overview")
        if 'description' in df.columns and 'amount' in df.columns:
            top_purchases = df[df['amount'] < 0][['description', 'amount']].copy()
            top_purchases = top_purchases.nsmallest(10, 'amount')
            
            fig, ax = plt.subplots()
            bars = ax.barh(top_purchases['description'], abs(top_purchases['amount']))
            ax.set_xlabel("Amount ($)")
            ax.set_ylabel("Description")
            ax.set_title("Top 10 Purchases")
            
            for bar in bars:
                ax.text(bar.get_width(), bar.get_y() + bar.get_height()/2, f"${bar.get_width():,.2f}", va='center')
            
            st.pyplot(fig)
        else:
            st.warning("⚠️ Missing 'Description' or 'Amount' column in data.")
    
    with tab2:
        st.subheader("💰 Savings Overview")
        if 'savings_category' in df.columns and 'savings_amount' in df.columns:
            savings_summary = df.groupby('savings_category')['savings_amount'].sum().sort_values()
            fig, ax = plt.subplots()
            bars = ax.barh(savings_summary.index, savings_summary.values)
            ax.set_xlabel("Total Savings ($")
            ax.set_ylabel("Category")
            ax.set_title("Savings by Category")
            
            for bar in bars:
                ax.text(bar.get_width(), bar.get_y() + bar.get_height()/2, f"${bar.get_width():,.2f}", va='center')
            
            st.pyplot(fig)
        else:
            st.warning("⚠️ No savings data found in the dataset.")
    
    with tab3:
        st.subheader("❓ Uncategorized Transactions")
        if not uncategorized_df.empty:
            st.dataframe(uncategorized_df)
        else:
            st.warning("⚠️ No uncategorized transactions found.")
    
    # Feedback Section
    st.subheader("💡 Feedback & Suggestions")
    feedback_text = st.text_area("How can we improve this dashboard?")
    if st.button("Submit Feedback"):
        with open("feedback.txt", "a") as f:
            f.write(feedback_text + "\n")
        st.success("✅ Thank you for your feedback!")
