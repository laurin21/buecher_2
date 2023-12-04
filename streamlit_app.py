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

st.markdown("## Neuer Eintrag")
buch_titel = st.selectbox(label="Buch",
                     options=buecher["Titel"])
datum = st.text_input(label="Datum")
seite = st.number_input(label="Seite")
if st.button('Neuer Eintrag'):
    if not buch_titel or not datum or not seite:
        st.warning("Ensure all mandatory fields are filled.")
    new_data = pd.DataFrame({"Datum": [datum],
                            "Titel": [buecher["Titel"].index(buch_titel)], 
                            "Gelesen": [seite]})
    new_updates = pd.concat([buecher, new_data], ignore_index=True)
    conn.update(worksheet="Updates", data=new_updates)
    updates = new_updates
    st.success("Buch wurde erfolgreich hinzugefügt")

with st.expander("Neuer Titel"):
    titel = st.text_input(label="Buchtitel")
    autor = st.text_input(label="Autor")
    seiten = st.number_input(label="Seiten")
    start = st.number_input(label="Start bei")

    if st.button('Enter neues Buch'):
        if not titel or not autor or not seiten:
                    st.warning("Ensure all mandatory fields are filled.")
        new_data = pd.DataFrame({"Buch_ID": [buecher["Buch_ID"].max()+1],
                                "Titel": [titel], 
                                 "Autor": [autor], 
                                 "Seiten": [seiten],
                                 "Fortschritt": [start]})
        new_buecher = pd.concat([buecher, new_data], ignore_index=True)
        conn.update(worksheet="Bücher", data=new_buecher)
        buecher = new_buecher
        st.success("Buch wurde erfolgreich hinzugefügt")