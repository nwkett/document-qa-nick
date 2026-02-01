import streamlit as st

st.set_page_config(page_title="Labs", layout="wide")

# Create a navigation object with pages
pg = st.navigation(
    [
        st.Page("pages/lab1.py", title="Lab 1", icon="1️⃣"),
        st.Page("pages/lab2.py", title="Lab 2", icon="2️⃣", default=True),
    ]
)

# Run the selected page
pg.run()