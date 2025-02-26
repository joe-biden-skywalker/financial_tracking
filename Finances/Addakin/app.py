import streamlit as st
import pandas as pd
import os
import io
from github import Github, InputFileContent

# GitHub Authentication (Store this securely in Streamlit secrets)
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "your-github-user/your-repo"

# Authenticate with PyGithub
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# Create a session state for tracking file changes
if "edited_df" not in st.session_state:
    st.session_state.edited_df = None

# File uploader
uploaded_file = st.file_uploader("Upload your financial file (.csv, .xlsx)", type=["csv", "xlsx"])

if uploaded_file:
    # Read file into Pandas
    file_ext = uploaded_file.name.split(".")[-1]
    
    if file_ext == "csv":
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Display editable table
    st.session_state.edited_df = st.data_editor(df)

    # Save the updated file locally
    if st.button("Save Changes Locally"):
        save_path = os.path.join("uploads", uploaded_file.name)
        os.makedirs("uploads", exist_ok=True)
        st.session_state.edited_df.to_csv(save_path, index=False)
        st.success(f"File saved locally: {save_path}")

    # Save & Push to GitHub
    if st.button("Save & Push to GitHub"):
        file_path = f"financial_data/{uploaded_file.name}"  # Path in GitHub repo
        new_content = st.session_state.edited_df.to_csv(index=False)

        try:
            # Check if file exists in repo
            contents = repo.get_contents(file_path)
            repo.update_file(
                file_path, "Updated financial data", InputFileContent(new_content), contents.sha
            )
            st.success("File successfully updated in GitHub!")
        except Exception:
            repo.create_file(file_path, "Initial upload of financial file", InputFileContent(new_content))
            st.success("File successfully uploaded to GitHub!")
