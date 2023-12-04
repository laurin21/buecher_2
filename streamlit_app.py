import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Display Title and Description
st.title("Bücher Stats 2")


# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)
url = "https://docs.google.com/spreadsheets/d/1UqgZb1MJCsfr9300dnphCGBvPlWxxMyNNnt4nppqdKY"

# Fetch existing vendors data
existing_data = conn.read(spreadsheet = url, worksheet="Updates", usecols=list(range(6)), ttl=5)
existing_data = existing_data.dropna(how="all")

st.dataframe(existing_data)