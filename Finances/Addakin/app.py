# File paths
category_mapping_file = "Finances/Addakin/spending_categories.csv"

# Load category mapping
def load_category_mapping():
    try:
        return pd.read_csv(category_mapping_file)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Keyword", "Category"])  # Return empty DataFrame if missing

# Save new category mapping
def save_category_mapping(df):
    df.to_csv(category_mapping_file, index=False)

# Filter transactions marked as "Other"
uncategorized_df = df[df['category'] == "Other"]

with tab4:
    st.subheader("❓ Uncategorized Transactions")

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
