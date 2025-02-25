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

# Load CSV data safely
def load_data():
    try:
        df = pd.read_csv(csv_file)
        df.columns = df.columns.str.lower().str.strip()
        return df
    except FileNotFoundError:
        st.error(f"❌ CSV file not found at: {csv_file}")
        return None

# Load category mapping
def load_category_mapping():
    try:
        return pd.read_csv(category_mapping_file)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Keyword", "Category"])

# Save new category mapping
def save_category_mapping(keyword, category):
    df = load_category_mapping()
    if not df.empty and ((df['Keyword'] == keyword) & (df['Category'] == category)).any():
        return False  # Mapping already exists
    
    new_mapping = pd.DataFrame([[keyword, category]], columns=["Keyword", "Category"])
    new_mapping.to_csv(category_mapping_file, mode='a', header=False, index=False)
    return True

# Delete category mapping
def delete_category_mapping(keyword):
    df = load_category_mapping()
    df = df[df["Keyword"] != keyword]  # Remove row
    df.to_csv(category_mapping_file, index=False)

# Apply category mappings to transactions
def apply_category_mappings(df):
    mapping_df = load_category_mapping()
    
    if not df.empty and not mapping_df.empty:
        for _, row in mapping_df.iterrows():
            keyword = row["Keyword"].lower()
            category = row["Category"]
            df.loc[df['description'].str.contains(keyword, case=False, na=False), 'category'] = category
    
    return df

# Load data
df = load_data()
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

# Apply category mappings to update "Other" transactions
df = apply_category_mappings(df)

# Filter transactions for selected month
filtered_df = df[df['month'] == selected_month]

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["💸 Spending", "💰 Saving", "📈 Income", "❓ Uncategorized Transactions"])

### **SPENDING TAB**
with tab1:
    st.subheader(f"📊 Spending Analysis - {selected_month}")

    spending_df = filtered_df[filtered_df['action'].str.lower() == 'spend']
    
    if not spending_df.empty:
        category_spending = spending_df.groupby('category')['amount'].sum().sort_values(ascending=False)

        # Two side-by-side charts
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("💰 Spending per Category")
            fig, ax = plt.subplots(figsize=(10, 5))
            category_spending.sort_values(ascending=True).plot(kind="barh", ax=ax, color=plt.cm.Paired.colors, alpha=0.8)
            ax.set_xlabel("Total Spent ($)")
            ax.set_ylabel("Category")
            ax.set_title(f"Total Spending by Category ({selected_month})")
            plt.grid(axis="x", linestyle="--", alpha=0.5)
            plt.tight_layout()
            st.pyplot(fig)

        with col2:
            st.subheader("📊 Spending Distribution")
            fig, ax = plt.subplots(figsize=(8, 6))
            category_spending.plot(kind="pie", ax=ax, autopct='%1.1f%%', startangle=140, cmap="coolwarm", pctdistance=0.85)
            ax.set_ylabel("")
            ax.set_title(f"Spending Breakdown by Category ({selected_month})")
            plt.tight_layout()
            st.pyplot(fig)

        st.subheader(f"📑 Spending Transactions - {selected_month}")
        st.dataframe(spending_df)

    else:
        st.warning(f"⚠️ No spending transactions found for {selected_month}.")

### **UNCATEGORIZED TRANSACTIONS TAB**
with tab4:
    st.subheader("❓ Uncategorized Transactions")

    # Filter transactions marked as "Other"
    uncategorized_df = df[df['category'] == "Other"]

    if not uncategorized_df.empty:
        st.write("### 🚨 Transactions Without a Category")
        st.dataframe(uncategorized_df)
    else:
        st.success("✅ No uncategorized transactions found!")

    # Load and display category mapping file (Centered)
    category_mapping_df = load_category_mapping()
    st.markdown("<h4 style='text-align: center;'>🔍 Current Category Mappings</h4>", unsafe_allow_html=True)
    st.dataframe(category_mapping_df.style.set_properties(**{'text-align': 'center'}))

    # Form for adding new category mappings
    st.write("### ➕ Add New Category Mapping")
    with st.form("add_category_mapping"):
        keyword = st.text_input("Enter Keyword (e.g., 'Uber', 'Starbucks')").strip()
        category = st.text_input("Enter Category (e.g., 'Transport', 'Dining')").strip()
        submit_button = st.form_submit_button("Add Mapping")

    if submit_button:
        if keyword and category:
            if save_category_mapping(keyword, category):
                st.success(f"✅ Mapping added: '{keyword}' → '{category}'")
            else:
                st.warning("⚠️ This mapping already exists.")
            st.rerun()
        else:
            st.error("❌ Both Keyword and Category are required!")

    # Delete category mappings
    st.write("### ❌ Delete a Category Mapping")
    keyword_to_delete = st.selectbox("Select a keyword to delete", category_mapping_df["Keyword"].unique())
    if st.button("Delete Mapping"):
        delete_category_mapping(keyword_to_delete)
        st.success(f"✅ Deleted mapping: '{keyword_to_delete}'")
        st.rerun()
