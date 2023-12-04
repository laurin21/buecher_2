import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta

# Display Title and Description
st.title("Bücher Stats")


# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)
url = "https://docs.google.com/spreadsheets/d/1UqgZb1MJCsfr9300dnphCGBvPlWxxMyNNnt4nppqdKY"

# Fetch existing vendors data
updates = conn.read(spreadsheet = url, worksheet="Updates", usecols=list(range(3))) # Updates
buecher = conn.read(spreadsheet = url, worksheet="Bücher", usecols=list(range(6))) # Bücher
updates = updates.dropna(how="all")
buecher = buecher.dropna(how="all")
updates["Datum"] = pd.to_datetime(updates["Datum"], format = "%Y-%m-%d", errors = "coerce").dt.date 

# Datenverarbeitung
df_days = updates.groupby('Datum')['Gelesen'].sum().reset_index()
heute = pd.Timestamp.now().date()
alle_tage = pd.date_range(start=min(df_days['Datum']), end=heute, freq='D')
neues_df = pd.DataFrame({'Datum': alle_tage})
neues_df["Datum"] = pd.to_datetime(neues_df["Datum"], format = "%Y-%m-%d %h:%h:%s", errors = "coerce").dt.date 
df_days = pd.merge(neues_df, df_days, on='Datum', how='left')
df_days['Gelesen'] = df_days['Gelesen'].fillna(0)

df_days_buch = updates.loc[updates['Buch_ID'] == buecher["Titel"][buecher["Titel"] == buch_titel].index[0]+1].copy().groupby('Datum')['Gelesen'].sum().reset_index()
heute = pd.Timestamp.now().date()
alle_tage = pd.date_range(start=min(df_days_buch['Datum']), end=max(df_days_buch['Datum']), freq='D')
neues_df = pd.DataFrame({'Datum': alle_tage})
neues_df["Datum"] = pd.to_datetime(neues_df["Datum"], format = "%Y-%m-%d %h:%h:%s", errors = "coerce").dt.date 
df_days_buch = pd.merge(neues_df, df_days_buch, on='Datum', how='left')
df_days_buch['Gelesen'] = df_days_buch['Gelesen'].fillna(0)

st.markdown("")
st.markdown("---")
st.markdown("")

seiten_heute = df_days["Gelesen"][df_days["Datum"] == heute]
seiten_gestern = df_days["Gelesen"][df_days["Datum"] == heute - timedelta(days=1)]

if seiten_heute > seiten_gestern:
     seiten_delta = seiten_gestern / seiten_heute
else:
     seiten_delta = seiten_heute / seiten_gestern

st.metric(label = "Heute gelesen", value = f"{seiten_heute}", delta = seiten_delta)

st.markdown("#### Aktuelles Buch")
buch_titel = st.selectbox(label="Buch",
                     options=buecher["Titel"])

st.markdown("##### Neuer Eintrag")
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


st.markdown("")
st.markdown("---")
st.markdown("")

gesamt_tab, buch_tab = st.tabs(["Gesamte Histore", "Ausgewählter Titel"])

with gesamt_tab:
    st.markdown("##### Gesamte Historie")
    st.line_chart(data = df_days[["Datum", "Gelesen"]], 
              x = "Datum", 
              y = "Gelesen")
with buch_tab:

    st.markdown("##### Ausgewähltes Buch")
    st.line_chart(data = df_days_buch[["Datum", "Gelesen"]], 
              x = "Datum", 
              y = "Gelesen")
    


st.markdown("")



df_buch = updates.groupby('Buch_ID')['Gelesen'].sum().reset_index()
buecher["Gelesen"] = df_buch["Gelesen"]

buecher["Fortschritt"] = buecher["Start"] + buecher["Gelesen"]
buecher["Übrig"] = buecher["Seiten"] - buecher["Gelesen"]
buecher["Prozent"] = (buecher["Fortschritt"] / buecher["Seiten"]) * 100


st.markdown("")
st.markdown("---")
st.markdown("")


with st.expander("Neuer Titel"):
    titel = st.text_input(label="Buchtitel")
    autor = st.text_input(label="Autor")
    seiten = st.number_input(label="Seiten",
                        format = "%d",
                        value = 0)
    start = st.number_input(label="Start bei",
                        format = "%d",
                        value = 0)

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
    updates_tab, buecher_tab, tage_tab = st.tabs(["Updates", "Bücher", "Tageswerte"])

    with updates_tab:
        st.markdown("##### Updates")
        st.dataframe(data=updates.reset_index(drop=True))
    with buecher_tab:
        st.markdown("##### Bücher")
        st.dataframe(data=buecher.reset_index(drop=True))
    with tage_tab:
        st.markdown("##### Bücher")
        st.dataframe(data=df_days.reset_index(drop=True))