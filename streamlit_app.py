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
buecher = conn.read(spreadsheet = url, worksheet="Bücher", usecols=list(range(8))) # Bücher
updates = updates.dropna(how="all")
buecher = buecher.dropna(how="all")
updates["Datum"] = pd.to_datetime(updates["Datum"], format = "%Y-%m-%d", errors = "coerce").dt.date 


st.markdown("---")

heute = pd.Timestamp.now().date()

df_days = updates.groupby('Datum')['Gelesen'].sum().reset_index()
alle_tage = pd.date_range(start=min(df_days['Datum']), end=heute, freq='D')
neues_df = pd.DataFrame({'Datum': alle_tage})
neues_df["Datum"] = pd.to_datetime(neues_df["Datum"], format = "%Y-%m-%d %h:%h:%s", errors = "coerce").dt.date 
df_days = pd.merge(neues_df, df_days, on='Datum', how='left')
df_days['Gelesen'] = df_days['Gelesen'].fillna(0)

seiten_heute = df_days.loc[df_days['Datum'] == heute, 'Gelesen'].values[0]
seiten_gestern = df_days.loc[df_days['Datum'] == heute - timedelta(days=1), 'Gelesen'].values[0]


if seiten_heute > seiten_gestern:
     seiten_delta = seiten_gestern / seiten_heute
if seiten_heute < seiten_gestern:
     seiten_delta = seiten_heute / seiten_gestern
if seiten_heute == 0:
     seiten_delta = -9.99
if seiten_gestern == 0:
     seiten_delta = +9.99

st.metric(label = "Heute gelesen", value = f"{int(seiten_heute)}", delta = f"{int(seiten_delta*100)}%")

st.markdown("---")

last_book = int(updates["Buch_ID"].iloc[-1]-1)
last_page = int(buecher.loc[buecher['Buch_ID'] == last_book + 1, 'Fortschritt'].values[0])

st.markdown("##### Aktuelles Buch")
buch_titel = st.selectbox(label="Buchtitel",
                     options=buecher["Titel"],
                     label_visibility = "collapsed",
                     index = last_book)

st.markdown("")

with st.expander("Neuer Eintrag"):
    st.markdown("##### Neuer Eintrag")
    datum = st.date_input(label="Datum")
    seiten_input = st.number_input(label="Seite",
                            format = "%d",
                            value = last_page)
    seite = seiten_input - last_page
    if st.button('Enter'):
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

df_days_buch = updates.loc[updates['Buch_ID'] == buecher["Titel"][buecher["Titel"] == buch_titel].index[0]+1].copy().groupby('Datum')['Gelesen'].sum().reset_index()
alle_tage = pd.date_range(start=min(df_days_buch['Datum']), end=max(df_days_buch['Datum']), freq='D')
neues_df = pd.DataFrame({'Datum': alle_tage})
neues_df["Datum"] = pd.to_datetime(neues_df["Datum"], format = "%Y-%m-%d %h:%h:%s", errors = "coerce").dt.date 
df_days_buch = pd.merge(neues_df, df_days_buch, on='Datum', how='left')
df_days_buch['Gelesen'] = df_days_buch['Gelesen'].fillna(0)

df_buch = updates.groupby('Buch_ID')['Gelesen'].sum().reset_index()
buecher["Gelesen"] = df_buch["Gelesen"]

buecher["Fortschritt"] = buecher["Start"] + buecher["Gelesen"]
buecher["Übrig"] = buecher["Seiten"] - buecher["Gelesen"]
buecher["Prozent"] = (buecher["Fortschritt"] / buecher["Seiten"]) * 100

######

gesamt_tab, buch_tab = st.tabs(["Gesamte Histore", "Ausgewählter Titel"])

with gesamt_tab:
    st.line_chart(data = df_days[["Datum", "Gelesen"]], 
              x = "Datum", 
              y = "Gelesen")
with buch_tab:

    st.markdown(f"##### {buch_titel}")
    st.line_chart(data = df_days_buch[["Datum", "Gelesen"]], 
              x = "Datum", 
              y = "Gelesen")
    col1, col2, col3 = st.columns(3)
    col1.metric(label = "Fortschritt", value = int(buecher.loc[buecher['Titel'] == buch_titel, 'Fortschritt'].values[0]))
    col2.metric(label = "Prozent", value = f"{int(buecher.loc[buecher['Titel'] == buch_titel, 'Prozent'].values[0])}%")
    col3.metric(label = "Übrig", value = int(buecher.loc[buecher['Titel'] == buch_titel, 'Übrig'].values[0]))
    


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

st.markdown("")
st.markdown("---")
st.markdown("")

if st.button("Sync Data"):
     conn.update(worksheet="Updates", data=updates)