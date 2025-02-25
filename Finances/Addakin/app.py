import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

# Authentication Details
CORRECT_USERNAME = "addakin"
CORRECT_PASSWORD = "3Clacrosse#1"

# Initialize session state for login
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Login Page
def login():
    st.title("🔐 Login to Access Dashboard")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login", key="login_button_unique")

    if login_button:
        if username == CORRECT_USERNAME and password == CORRECT_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Incorrect username or password. Try again.")

# If not authenticated, show login page
if not st.session_state.authenticated:
    login()
    st.stop()

# File paths
csv_file = "Finances/Addakin/streamlit/finances.csv"
category_mapping_file = "Finances/Addakin/spending_categories.csv"
feedback_folder = "Finances/Addakin/data"

# Load CSV data safely
def load_data():
    try:
        df = pd.read_csv(csv_file)
        df.columns = df.columns.str.lower().str.strip()  # Normalize column names
        return df
    except FileNotFoundError:
        st.error(f"❌ CSV file not found at: {csv_file}")
        return None

# Load category mapping
def load_category_mapping():
    try:
        return pd.read_csv(category_mapping_file)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Keyword", "Category"])  # Return empty DataFrame if missing

# Save new category mapping
def save_category_mapping(df):
    df.to_csv(category_mapping_file, index=False)

# Load data
df = load_data()

# Stop execution if CSV is missing
if df is None:
    st.stop()

# Standardize 'month' column
df['month'] = df['month'].str.capitalize()

# Sidebar Logout Button
if st.sidebar.button("🚪 Logout", key="logout_button_unique"):
    st.session_state.authenticated = False
    st.rerun()

# Sidebar Filters
st.sidebar.header("📅 Filter by Month")
months_ordered = ["January", "February", "March", "April", "May", "June", "July", 
                  "August", "September", "October", "November", "December"]
selected_month = st.sidebar.radio("Select a month", months_ordered)

# Filter transactions for selected month
filtered_df = df[df['month'] == selected_month]

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["💸 Spending", "💰 Saving", "📈 Income", "❓ Uncategorized Transactions"])

# UNCATEGORIZED TRANSACTIONS TAB
with tab4:
    st.subheader("❓ Uncategorized Transactions")

    # Filter transactions marked as "Other"
    uncategorized_df = df[df['category'] == "Other"]

    # Display uncategorized transactions
    if not uncategorized_df.empty:
        st.write("### 🚨 Transactions Without a Category")
        st.dataframe(uncategorized_df)
    else:
        st.success("✅ No uncategorized transactions found!")

    # Load and display category mapping file
    category_mapping_df = load_category_mapping()
    st.write("### 🔍 Current Category Mappings")
    st.dataframe(category_mapping_df)

    # Form for adding new category mappings
    st.write("### ➕ Add New Category Mapping")

    with st.form("add_category_mapping"):
        keyword = st.text_input("Enter Keyword (e.g., 'Uber', 'Starbucks')").strip()
        category = st.text_input("Enter Category (e.g., 'Transport', 'Dining')").strip()
        submit_button = st.form_submit_button("Add Mapping")

    if submit_button:
        if keyword and category:
            # Add to DataFrame and save
            new_row = pd.DataFrame([[keyword, category]], columns=["Keyword", "Category"])
            category_mapping_df = pd.concat([category_mapping_df, new_row], ignore_index=True)
            save_category_mapping(category_mapping_df)
            st.success(f"✅ Mapping added: '{keyword}' → '{category}'")
            st.rerun()
        else:
            st.error("❌ Both Keyword and Category are required!")
