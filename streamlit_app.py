import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Display Title and Description
st.title("Bücher Stats 2")


# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)
url = "https://docs.google.com/spreadsheets/d/1UqgZb1MJCsfr9300dnphCGBvPlWxxMyNNnt4nppqdKY"

# Fetch existing vendors data
updates = conn.read(spreadsheet = url, worksheet="Updates", usecols=list(range(3))) # Updates
buecher = conn.read(spreadsheet = url, worksheet="Bücher", usecols=list(range(5))) # Bücher
updates = updates.dropna(how="all")
buecher = buecher.dropna(how="all")


st.markdown("### Neues Buch")

titel = st.text_input(label="Buchtitel")
autor = st.text_input(label="Autor")
seiten = st.number_input(label="Seiten")

if st.button('Enter neues Buch'):
    if not titel or not autor or not seiten:
                st.warning("Ensure all mandatory fields are filled.")
    new_data = pd.DataFrame({"Buch_ID": [buecher["Buch_ID"].max()+1],
                            "Titel": [titel], 
                             "Autor": [autor], 
                             "Seiten": [seiten],
                             "Fortschritt": [0]})
    new_buecher = pd.concat([buecher, new_data], ignore_index=True)
    conn.update(worksheet="Bücher", data=new_buecher)
    buecher = new_buecher
    st.success("Buch wurde erfolgreich hinzugefügt")

option = st.multiselect(
    'Welche Tabellen sollen angezeigt werden?',
    ['Upadtes', 'Bücher'])

for i in option:
    if i == "Updates":
        st.markdown("##### Updates")
        st.dataframe(updates)

    if i == "Bücher":
        st.markdown("##### Bücher")
        st.dataframe(buecher)
