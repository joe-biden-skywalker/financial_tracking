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
    login_button = st.button("Login", key="login_button_unique")  # Unique key assigned

    if login_button:
        if username == CORRECT_USERNAME and password == CORRECT_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Incorrect username or password. Try again.")

# If not authenticated, show login page
if not st.session_state.authenticated:
    login()
    st.stop()  # Prevents the rest of the app from loading if not logged in

# Define file path dynamically
csv_file = "Finances/Addakin/streamlit/finances.csv"
feedback_folder = "Finances/Addakin/data"
feedback_file = os.path.join(feedback_folder, "feedback.txt")

# Load CSV data safely
def load_data():
    try:
        df = pd.read_csv(csv_file)
        df.columns = df.columns.str.lower().str.strip()  # Normalize column names to lowercase and remove spaces
        return df
    except FileNotFoundError:
        st.error(f"❌ CSV file not found at: {csv_file}")
        return None

# Create feedback directory if not exists
if not os.path.exists(feedback_folder):
    os.makedirs(feedback_folder)

# Streamlit UI (Only visible after successful login)
st.set_page_config(layout="wide")
st.title("📊 Addakin's Financial Overview")

df = load_data()

if df is None:
    st.stop()  # Prevent further execution if CSV is missing

months_ordered = ["January", "February", "March", "April", "May", "June", "July", 
                  "August", "September", "October", "November", "December"]

# Standardize 'month' column
df['month'] = df['month'].str.capitalize()

# Sidebar Logout Button (Fixed with unique key)
if st.sidebar.button("🚪 Logout", key="logout_button_unique"):
    st.session_state.authenticated = False
    st.experimental_rerun()

# Sidebar Filters
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
            fig,
