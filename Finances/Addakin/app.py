import streamlit as st
import pandas as pd
import os
import io
from github import Github

# GitHub Authentication (Store this securely in Streamlit secrets)
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "your-github-user/your-repo"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# User uploads a file
uploaded_file = st.file_uploader("Upload your financial file (.csv, .xlsx)", type=["csv", "xlsx"])

if uploaded_file:
    # Read file into Pandas
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Display editable table
    edited_df = st.data_editor(df)

    # Save the updated file locally
    if st.button("Save Changes Locally"):
        save_path = os.path.join("uploads", uploaded_file.name)
        os.makedirs("uploads", exist_ok=True)
        edited_df.to_csv(save_path, index=False)
        st.success(f"File saved locally: {save_path}")

    # Save & Push to GitHub
    if st.button("Save & Push to GitHub"):
        file_path = f"financial_data/{uploaded_file.name}"  # Path in GitHub repo
        new_content = edited_df.to_csv(index=False)

        # Check if file already exists on GitHub
        try:
            existing_file = repo.get_contents(file_path)
            repo.update_file(file_path, "Updated financial data", new_content, existing_file.sha)
        except:
            repo.create_file(file_path, "Initial upload of financial file", new_content)

        st.success("File successfully saved to GitHub!")
