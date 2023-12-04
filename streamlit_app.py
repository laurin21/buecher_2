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
buecher = conn.read(spreadsheet = url, worksheet="Bücher", usecols=list(range(6))) # Bücher
updates = updates.dropna(how="all")
buecher = buecher.dropna(how="all")
updates["Datum"] = pd.to_datetime(updates["Datum"], format = "%Y-%m-%d", errors = "coerce").dt.date 

              
st.markdown("#### Neuer Eintrag")
buch_titel = st.selectbox(label="Buch",
                     options=buecher["Titel"])
datum = st.date_input(label="Datum")
seite = st.number_input(label="Seite",
                        format = "%d",
                        value = 0)
if st.button('Neuer Eintrag'):
    if not buch_titel or not datum or not seite:
        st.warning("Ensure all mandatory fields are filled.")

    else:
        new_data = pd.DataFrame({"Datum": [datum],
                                 "Buch_ID": [buecher["Titel"][buecher["Titel"] == buch_titel].index[0]+1], 
                                 "Gelesen": [seite]})
        new_updates = pd.concat([updates, new_data], ignore_index=True)
        conn.update(worksheet="Updates", data=new_updates)
        updates = new_updates

df_days = updates.groupby('Datum')['Gelesen'].sum().reset_index()
st.line_chart(data = df_days[["Datum", "Gelesen"]], x = "Datum", y = "Gelesen")

df_buch = updates.groupby('Buch_ID')['Gelesen'].sum().reset_index()
buecher["Gelesen"] = df_buch["Gelesen"]

buecher["Fortschritt"] = buecher["Start"] + buecher["Gelesen"]
buecher["Übrig"] = buecher["Seiten"] - buecher["Gelesen"]
buecher["Prozent"] = buecher["Gelesen"] / buecher["Seiten"]



st.markdown("")
st.markdown("---")
st.markdown("")

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

st.markdown("")
st.markdown("---")
st.markdown("")

see_data = st.expander('Ganzer Datensatz')
with see_data:
    aus_tab, ein_tab = st.tabs(["Updates", "Bücher"])

    with aus_tab:
        st.markdown("##### Updates")
        st.dataframe(data=updates.reset_index(drop=True))
    with ein_tab:
        st.markdown("##### Bücher")
        st.dataframe(data=buecher.reset_index(drop=True))