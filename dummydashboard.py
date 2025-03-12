
import streamlit as st
import plotly.express as px
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

#streamlit run /Users/private/Library/CloudStorage/OneDrive-SharedLibraries-StudentConsultant/Business\ -\ Documents/General/03.\ Deliverables/dashboard.py


#PAGINA CONFIGURATIE
#--------------------------------------------- #
st.set_page_config(page_title="Saffier Dashboard", page_icon=":bar_chart:", layout="wide")

st.markdown(
    """
    <style>
        /* Pas de breedte van de sidebar aan */
        section[data-testid="stSidebar"] {
            width: 27% !important;  /* Maak de sidebar smaller */
        }

        /* Pas de hoofdcontent aan zodat deze beter uitlijnt */
        section.main {
            margin-left: 20% !important;  /* Zorgt voor betere uitlijning */
        }

        "<h1 style='font-size: 90px;'>ENERGIE DASHBOARD</h1>", 
    </style>
    """,
    unsafe_allow_html=True
)

# Voeg een unieke klasse toe aan de CSS-styling voor elektriciteit en gas
st.markdown(
    """
    <style>
        /* Algemene styling voor alle metrics */
        div[data-testid="metric-container"] {
            background-color: rgba(255, 255, 255, 0.6); /* Licht witte kleur */
            border-radius: 10px;  /* Afgeronde hoeken */
            padding: 10px; /* Ruimte binnen de container */
            margin-bottom: 10px; /* Ruimte tussen metrics */
        }

        /* Specifieke styling voor elektriciteit */
        div[data-testid="metric-container"]:has(> div > p:contains('Elektriciteit')) {
            background-color: rgba(227, 242, 253, 0.6); /* Lichtblauw voor elektriciteit */
        }

        /* Specifieke styling voor gas */
        div[data-testid="metric-container"]:has(> div > p:contains('Gas')) {
            background-color: rgba(255, 235, 238, 0.6); /* Lichtrood voor gas */
        }
    </style>
    """,
    unsafe_allow_html=True
)


st.title("ENERGIE DASHBOARD SAFFIER")
st.logo("logo.png")

















#---------------------DATA------------------------ #
@st.cache_data (ttl=1200)
def load_data():
    df = pd.read_excel("Dummydata_BI.xlsx")
    df["Datum & tijd"] = pd.to_datetime(df["Datum & tijd"])
    return df

df = load_data()  


#---------------------FILTERS------------------------ #

# Sidebar filters
st.sidebar.header("🔍 Filter data:")

# Locatie filter
locaties = df["Location"].unique()
locatie_selectie = st.sidebar.multiselect("Locatie", options=locaties,)

# Energietype filter
energie_stromen = df["Energiestroom"].unique()
energie_selectie = st.sidebar.selectbox("Energiestromen", options=energie_stromen)

# Checkbox voor temperatuurcorrectie
corrigeer_temp = st.sidebar.checkbox("Corrigeer verbruik voor temperatuur om beter te kunnen vergelijken")
verbruik_col = "Verbruik gecorrigeerd" if corrigeer_temp else "Verbruik totaal"

# Filter de dataset op gekozen waarden
df_filtered = df[
    (df["Location"].isin(locatie_selectie)) &
    (df["Energiestroom"]== energie_selectie)
]

df_filtered2 = df[(df["Location"].isin(locatie_selectie))]


def bepaal_eenheid(energiestroom, corrigeer_temp=False):
    """
    Retourneert de juiste eenheid voor gas of elektriciteit, 
    en voegt (gecorrigeerd) toe als temperatuurcorrectie is toegepast.
    """
    if energiestroom == "Gas":
        eenheid = "Verbruik (m³)"
    elif energiestroom == "Elektriciteit":
        eenheid = "Verbruik (kWh)"
    else:
        eenheid = "Verbruik"  # Fallback als iets anders geselecteerd wordt
    
    # Voeg '(gecorrigeerd)' toe als temperatuurcorrectie is ingeschakeld
    if corrigeer_temp:
        eenheid += " (gecorrigeerd)"
    
    return eenheid

def bepaal_eenheid_metric(energiestroom):
    """
    Retourneert alleen de eenheid (kWh of m³), zonder het woord 'Verbruik'.
    Handig voor gebruik in `st.metric()`.
    """
    return "m³" if energiestroom == "Gas" else "kWh"



st.markdown("<br><br>", unsafe_allow_html=True)









 # VISUALISATIE LIJNPLOT
# --------------------------------------------- # 


st.subheader(f'ALGEMENE ANALYSE VAN {energie_selectie.upper()} VERBRUIK')

# Datum selectie
startDate = df["Datum & tijd"].min()
endDate = df["Datum & tijd"].max()

# Date pickers
col1, col2 = st.columns((2))
with col1:
    date1 = st.date_input("Start Datum", startDate)
with col2:
    date2 = st.date_input("Eind Datum", endDate)

# Filter op datum, locatie en energiestroom
df_filtered = df[
    (df["Datum & tijd"] >= pd.to_datetime(date1)) &
    (df["Datum & tijd"] <= pd.to_datetime(date2)) &
    (df["Location"].isin(locatie_selectie)) &
    (df["Energiestroom"] == energie_selectie)
].copy()

# Interval selectie
interval = st.selectbox("Selecteer interval", ["Uur", "Dag", "Week"])
toon_temp = st.checkbox("Toon temperatuur in grafiek")

# Eerst sorteren en index instellen
df_filtered = df_filtered.sort_values("Datum & tijd").set_index("Datum & tijd")

# Resamplen per locatie en energiestroom, zodat 'Energiestroom' behouden blijft
if interval == "Dag":
    df_filtered = df_filtered.groupby(["Location", "Energiestroom"]).resample("D").agg({
        "Verbruik totaal": "sum",
        "Temp": "mean"
    }).reset_index()
elif interval == "Week":
    df_filtered = df_filtered.groupby(["Location", "Energiestroom"]).resample("W").agg({
        "Verbruik totaal": "sum",
        "Temp": "mean"
    }).reset_index()
else:
    df_filtered = df_filtered.reset_index()  # Zorgt dat de originele structuur behouden blijft bij "Uur"

# Bepaal de juiste as-titels op basis van de energiestroom
y_axis_title = bepaal_eenheid(energie_selectie, corrigeer_temp=False)  # Zonder correctie
y_axis2_title = "Temperatuur (°C)"

# Visualisatie: Lijnchart met aggregatie
if not df_filtered.empty:
    fig = px.line(df_filtered, x="Datum & tijd", y="Verbruik totaal", color="Location", title="", markers=True,
                  labels={"Verbruik totaal": y_axis_title, "Datum & tijd": "Tijd"})

    if toon_temp:
        # Voeg temperatuur als tweede y-as toe
        fig.add_scatter(x=df_filtered["Datum & tijd"], y=df_filtered["Temp"], mode='lines', name=y_axis2_title, yaxis="y2")

        # Update layout met tweede y-as
        fig.update_layout(
            yaxis=dict(title=y_axis_title),  # Hoofd y-as links
            yaxis2=dict(
                title=y_axis2_title,  # Tweede y-as rechts
                overlaying="y",
                side="right",
                showgrid=False
            )
        )

    # Update layout voor legenda & x-as titel verwijderen
    fig.update_layout(
        xaxis_title="Verbruik van geselecteerde periode (zoals in Innax)",
        legend=dict(
            orientation="h",  # Horizontale legenda
            yanchor="top",
            y=-0.3,  # Plaats de legenda onder de grafiek
            xanchor="center",
            x=0.5
        ),
        legend_title_text=""  # Verwijdert de legenda-titel
    )

    # Toon de grafiek slechts één keer
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("⚠️ Geen data beschikbaar voor de geselecteerde filters.")

st.markdown("<br><br><br>", unsafe_allow_html=True)









# ==================== EMISSIEFACTOREN EN TARIEVEN ==================== #
# https://co2emissiefactoren.nl/factoren/2025/11/elektriciteit/?unit=kwh 

# Definieer de tarieven 
GAS_PRIJS_2023 = 0.6286  # Euro per m³
ELEKTRA_DAG_PRIJS_2023 = 0.2198  # Euro per kWh
ELEKTRA_NACHT_PRIJS_2023 = 0.1495   # Euro per kWh

GAS_PRIJS_2024 = 0.6394  # Euro per m³
ELEKTRA_DAG_PRIJS_2024 = 0.1632  # Euro per kWh
ELEKTRA_NACHT_PRIJS_2024 = 0.1393  # Euro per kWh


GAS_PRIJS_2025 = 0.5077  # Euro per m³
ELEKTRA_DAG_PRIJS_2025 = 0.1300  # Euro per kWh
ELEKTRA_NACHT_PRIJS_2025 = 0.1103  # Euro per kWh

# ==================== OVERZICHT YEAR TO YEAR COMPARISON ==================== #

st.subheader("YEAR TO YEAR OVERZICHT")

# Data voorbereiden
df_overzicht = df[df['Location'].isin(locatie_selectie)].copy()
df_overzicht['Date'] = pd.to_datetime(df_overzicht['Datum & tijd'])
df_overzicht['Year'] = df_overzicht['Date'].dt.year
df_overzicht['Dag'] = df_overzicht['Date'].dt.day_of_year  # Dagnummer in het jaar

# Bepaal de maximale dag met data in 2025
max_dag_2025 = df_overzicht[df_overzicht['Year'] == 2025]['Dag'].max()

# Filter dezelfde periode in 2024
df_referentie_2024 = df_overzicht[df_overzicht['Dag'] <= max_dag_2025]

# Bereken verbruik per jaar (volledig en referentieperiode)
df_verbruik_jaar = df_overzicht.groupby(["Year", "Energiestroom"])[verbruik_col].sum().unstack()
df_verbruik_referentie = df_referentie_2024.groupby(["Year", "Energiestroom"])[verbruik_col].sum().unstack()

# Verbruik per jaar ophalen
verbruik_per_jaar = df_verbruik_jaar.to_dict()
referentie_per_jaar = df_verbruik_referentie.to_dict()

# Procentuele referentieverschillen ten opzichte van vorige jaren
def calc_delta(curr, prev):
    return f"{((curr - prev) / prev) * 100:.1f}%" if prev != 0 else "NVT"

delta_verbruik = {
    2024: calc_delta(verbruik_per_jaar[energie_selectie][2024], verbruik_per_jaar[energie_selectie][2023]),
    2025: calc_delta(verbruik_per_jaar[energie_selectie][2025], referentie_per_jaar[energie_selectie][2024])
}

# Kostenberekening per jaar
kosten_tarief = {
    "Elektriciteit": {2023: ELEKTRA_DAG_PRIJS_2023, 2024: ELEKTRA_DAG_PRIJS_2024, 2025: ELEKTRA_DAG_PRIJS_2025},
    "Gas": {2023: GAS_PRIJS_2023, 2024: GAS_PRIJS_2024, 2025: GAS_PRIJS_2025}
}

kosten_per_jaar = {
    jaar: verbruik_per_jaar[energie_selectie][jaar] * kosten_tarief[energie_selectie][jaar]
    for jaar in [2023, 2024, 2025]
}

# Referentie-kostenberekening per jaar
kosten_referentie_per_jaar = {
    2024: referentie_per_jaar[energie_selectie][2024] * kosten_tarief[energie_selectie][2024],
    2025: verbruik_per_jaar[energie_selectie][2025] * kosten_tarief[energie_selectie][2025]
}

# Procentuele verschillen in kosten
delta_kosten = {
    2024: calc_delta(kosten_per_jaar[2024], kosten_per_jaar[2023]),
    2025: calc_delta(kosten_per_jaar[2025], kosten_referentie_per_jaar[2024])
}

# CO₂-uitstoot berekening per jaar
co2_factor = {
    "Elektriciteit": {2023: 0.337, 2024: 0.328, 2025: 0.268},  # kg CO2 per kWh
    "Gas": {2023: 2.079, 2024: 2.134, 2025: 2.134}  # kg CO2 per m³
}

co2_per_jaar = {
    jaar: verbruik_per_jaar[energie_selectie][jaar] * co2_factor[energie_selectie][jaar]
    for jaar in [2023, 2024, 2025]
}

# Referentie-CO₂-uitstoot per jaar
co2_referentie_per_jaar = {
    2024: referentie_per_jaar[energie_selectie][2024] * co2_factor[energie_selectie][2024],
    2025: verbruik_per_jaar[energie_selectie][2025] * co2_factor[energie_selectie][2025]
}

# Procentuele verschillen in CO₂-uitstoot
delta_co2 = {
    2024: calc_delta(co2_per_jaar[2024], co2_per_jaar[2023]),
    2025: calc_delta(co2_per_jaar[2025], co2_referentie_per_jaar[2024])
}

# Layout - 3 kolommen per rij (Verbruik, Kosten, CO₂-uitstoot)
st.subheader(f"{locatie_selectie[0]} - {energie_selectie}" + (" (gecorrigeerd)" if corrigeer_temp else ""))

for jaar in [2023, 2024, 2025]:
    verbruik = verbruik_per_jaar[energie_selectie].get(jaar, 0)
    kosten = kosten_per_jaar.get(jaar, 0)
    co2 = co2_per_jaar.get(jaar, 0)
    
    delta_v = delta_verbruik.get(jaar, "NVT")
    delta_k = delta_kosten.get(jaar, "NVT")
    delta_c = delta_co2.get(jaar, "NVT")

    eenheid = "kWh" if energie_selectie == "Elektriciteit" else "m³"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(f"Verbruik {jaar} ({eenheid})", f"{verbruik:,.0f}", delta=(delta_v if jaar != 2023 else "NVT"), delta_color=("off" if jaar == 2023 else "inverse"))
    with col2:
        st.metric(f"Kosten {jaar} (€)", f"€{kosten:,.2f}", delta=(delta_k if jaar != 2023 else "NVT"), delta_color=("off" if jaar == 2023 else "inverse"))
    with col3:
        st.metric(f"CO₂-uitstoot {jaar} (kg)", f"{co2:,.0f}", delta=(delta_c if jaar != 2023 else "NVT"), delta_color=("off" if jaar == 2023 else "inverse"))

st.markdown("<br><br><br>", unsafe_allow_html=True)













# ==================== Dynamische Maandvergelijking ==================== #
st.subheader("DYNAMISCHE MAANDVERGELIJKING")

# Selecteer een maand op basis van de "Month"-kolom in de dataset
maand_optie = st.selectbox(
    "Selecteer een maand om te vergelijken",
    options=df["Month"].unique().tolist(),  
    index=0  
)

# Gebruik bestaande filters voor locatie en energiestroom
df_maandselectie = df[
    (df["Location"].isin(locatie_selectie)) &
    (df["Energiestroom"] == energie_selectie) &
    (df["Month"] == maand_optie)
].copy()

# Selecteer de juiste kolom afhankelijk van de checkbox
y_value = "Verbruik gecorrigeerd" if corrigeer_temp else "Verbruik totaal"
x_as_titel = bepaal_eenheid(energie_selectie, corrigeer_temp)

# Data groeperen per dag en uur voor vergelijking
df_maandselectie["Datum & tijd"] = pd.to_datetime(df_maandselectie["Datum & tijd"])
df_maandselectie["Dag"] = df_maandselectie["Datum & tijd"].dt.day  
df_maandselectie["Uur"] = df_maandselectie["Datum & tijd"].dt.hour  

df_verbruik_per_uur = df_maandselectie.groupby(["Year", "Dag", "Uur"])[y_value].sum().reset_index()

# Maak een uniforme tijdlijn per jaar
df_verbruik_per_uur["Virtuele_Tijd"] = pd.to_datetime(f"2025-{maand_optie}-" + df_verbruik_per_uur["Dag"].astype(str) + " " + df_verbruik_per_uur["Uur"].astype(str) + ":00")

# Lijngrafiek: Per uur, correct gefilterd en geaggregeerd
fig = px.line(
    df_verbruik_per_uur, 
    x="Virtuele_Tijd",  
    y=y_value,  
    color="Year", 
    title=f"{energie_selectie} verbruik in {maand_optie}" + (" (gecorrigeerd voor temperatuur)" if corrigeer_temp else ""),
    labels={y_value: x_as_titel, "Virtuele_Tijd": "Datum & Uur"},
    markers=False  
)

# Update x-as zodat het minder druk is
fig.update_layout(
    xaxis_title=f"Dagen in {maand_optie}",
    xaxis=dict(
        tickmode="auto",
        tickformat="%d %b",  
    ),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.3,
        xanchor="center",
        x=0.5
    )  
)

st.plotly_chart(fig, use_container_width=True)

# Totaal verbruik per jaar berekenen
df_verbruik_totaal = df_maandselectie.groupby("Year")[y_value].sum().reset_index()
df_verbruik_totaal.columns = ["Jaar", "Totaal Verbruik (MWh)"]

# Zorg ervoor dat alle jaren aanwezig zijn (2023, 2024, 2025)
verbruik_per_jaar = {jaar: df_verbruik_totaal.loc[df_verbruik_totaal["Jaar"] == jaar, "Totaal Verbruik (MWh)"].sum() for jaar in [2023, 2024, 2025]}

# Bereken de procentuele delta t.o.v. het voorgaande jaar
delta_2024 = ((verbruik_per_jaar[2024] - verbruik_per_jaar[2023]) / verbruik_per_jaar[2023]) * 100 if verbruik_per_jaar[2023] != 0 else 0
delta_2025 = ((verbruik_per_jaar[2025] - verbruik_per_jaar[2024]) / verbruik_per_jaar[2024]) * 100 if verbruik_per_jaar[2024] != 0 else 0

# Drie kolommen met `st.metric`
col2023, col2024, col2025 = st.columns(3)

# Dynamisch de juiste eenheid bepalen
eenheid_metric = bepaal_eenheid_metric(energie_selectie)

with col2023:
    st.metric(label=f"Verbruik {maand_optie} 2023", value=f"{verbruik_per_jaar[2023]:,.0f} {eenheid_metric}", delta=f"NVT", delta_color="off")

with col2024:
    st.metric(label=f"Verbruik {maand_optie} 2024", value=f"{verbruik_per_jaar[2024]:,.0f} {eenheid_metric}", delta=f"{delta_2024:.2f}%", delta_color="inverse")

with col2025:
    st.metric(label=f"Verbruik {maand_optie} 2025", value=f"{verbruik_per_jaar[2025]:,.0f} {eenheid_metric}", delta=f"{delta_2025:.2f}%", delta_color="inverse")
st.markdown("<br><br><br>", unsafe_allow_html=True)










# ==================== Dynamische Kwartaalvergelijking ==================== #
st.subheader("DYNAMISCHE KWARTAALVERGELIJKING")

# Kwartaal selecteren
kwartaal_optie = st.selectbox(
    "Selecteer een kwartaal",
    options=["Q1", "Q2", "Q3", "Q4"],
    index=0  # Standaard op Q1
)

# Bepaal welke maanden bij het geselecteerde kwartaal horen
kwartaal_maanden = {
    "Q1": [1, 2, 3],
    "Q2": [4, 5, 6],
    "Q3": [7, 8, 9],
    "Q4": [10, 11, 12]
}

# Zorg dat "Datum & tijd" als datetime wordt gelezen en "Month" correct wordt gegenereerd
df["Datum & tijd"] = pd.to_datetime(df["Datum & tijd"])  # Zet om naar datetime
df["Month"] = df["Datum & tijd"].dt.month  # Extraheer de maand als integer

# Filter de dataset op de geselecteerde maanden en energiestroom
df_kwartaal = df[
    (df["Location"].isin(locatie_selectie)) &
    (df["Energiestroom"] == energie_selectie) &
    (df["Month"].isin(kwartaal_maanden[kwartaal_optie]))
].copy()

# Selecteer de juiste kolom afhankelijk van de checkbox
y_value = "Verbruik gecorrigeerd" if corrigeer_temp else "Verbruik totaal"

# Verbruik per dag in het kwartaal berekenen
df_kwartaal["Datum & tijd"] = pd.to_datetime(df_kwartaal["Datum & tijd"])
df_kwartaal["Dag"] = df_kwartaal["Datum & tijd"].dt.day_of_year  # Dagnummer in het jaar

df_verbruik_per_dag_kwartaal = df_kwartaal.groupby(["Year", "Dag"])[y_value].sum().reset_index()

# Lijngrafiek: Verbruik per dag per jaar voor het kwartaal
fig_kwartaal = px.line(
    df_verbruik_per_dag_kwartaal, 
    x="Dag",  
    y=y_value,  
    color="Year", 
    title=f"{energie_selectie} verbruik in {kwartaal_optie}" + (" (gecorrigeerd voor temperatuur)" if corrigeer_temp else ""),
    labels={y_value: bepaal_eenheid(energie_selectie, corrigeer_temp), "Dag": "Dag van het Jaar"},
    markers=False  
)

# Update x-as zodat het alleen de dagen in het kwartaal laat zien
fig_kwartaal.update_layout(
    xaxis_title="Dagen in het Kwartaal",
    xaxis=dict(
        tickmode="auto",
        tickformat="%d",  # Alleen de dag tonen
    ),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.3,
        xanchor="center",
        x=0.5
    )  
)

st.plotly_chart(fig_kwartaal, use_container_width=True)

# Totale verbruik per kwartaal berekenen
df_verbruik_kwartaal = df_kwartaal.groupby("Year")[y_value].sum().reset_index()
df_verbruik_kwartaal.columns = ["Jaar", "Totaal Verbruik (MWh)"]

# Zorg ervoor dat alle jaren aanwezig zijn
verbruik_per_kwartaal = {jaar: df_verbruik_kwartaal.loc[df_verbruik_kwartaal["Jaar"] == jaar, "Totaal Verbruik (MWh)"].sum() for jaar in df_verbruik_kwartaal["Jaar"]}

# Bereken de procentuele delta t.o.v. het voorgaande jaar
delta_2024 = ((verbruik_per_kwartaal[2024] - verbruik_per_kwartaal[2023]) / verbruik_per_kwartaal[2023]) * 100 if verbruik_per_kwartaal[2023] != 0 else 0
delta_2025 = 0  # Standaardwaarde

if 2025 in verbruik_per_kwartaal and 2024 in verbruik_per_kwartaal:
    if verbruik_per_kwartaal[2024] != 0:  # Voorkom delen door nul
        delta_2025 = ((verbruik_per_kwartaal[2025] - verbruik_per_kwartaal[2024]) / verbruik_per_kwartaal[2024]) * 100

eenheid_metric = bepaal_eenheid_metric(energie_selectie)

# Bepaal welke jaren beschikbaar zijn in de dataset
beschikbare_jaren = sorted([jaar for jaar in [2023, 2024, 2025] if jaar in verbruik_per_kwartaal])

# Maak alleen het aantal kolommen dat nodig is
cols = st.columns(len(beschikbare_jaren))  

# Vul de kolommen dynamisch
for i, jaar in enumerate(beschikbare_jaren):
    if jaar == 2023:
        delta = "NVT"
        delta_color = "off"  # Zet de kleur op 'off' voor 2023
    else:
        delta = f"{((verbruik_per_kwartaal[jaar] - verbruik_per_kwartaal.get(jaar - 1, 0)) / verbruik_per_kwartaal.get(jaar - 1, 1)) * 100:.2f}%"
        delta_color = "inverse"

    with cols[i]:
        st.metric(label=f"Verbruik {kwartaal_optie} {jaar}", value=f"{verbruik_per_kwartaal[jaar]:,.0f} {eenheid_metric}", delta=delta, delta_color=delta_color)

st.markdown("<br><br><br>", unsafe_allow_html=True)













# ==================== Dynamische Jaarvergelijking (Referentieverschil) ==================== #
st.subheader("DYNAMISCHE JAARVERGLIJKING")

# Bepaal de maximale dag met data in 2025
df["Datum & tijd"] = pd.to_datetime(df["Datum & tijd"])
df["Dag"] = df["Datum & tijd"].dt.day_of_year  # Dagnummer in het jaar

max_dag_2025 = df[df["Year"] == 2025]["Dag"].max()

#  Volledige dataset tonen in de grafiek
df_jaarselectie_volledig = df[
    (df["Location"].isin(locatie_selectie)) &
    (df["Energiestroom"] == energie_selectie)
].copy()

df_verbruik_per_dag_volledig = df_jaarselectie_volledig.groupby(["Year", "Dag"])[y_value].sum().reset_index()

# Lijngrafiek: Verbruik per dag per jaar (volledig jaar)
fig_jaar = px.line(
    df_verbruik_per_dag_volledig, 
    x="Dag",  
    y=y_value,  
    color="Year", 
    title=f"Jaarlijkse {energie_selectie} vergelijking per Dag" + (" (gecorrigeerd voor temperatuur)" if corrigeer_temp else ""),
    labels={y_value: bepaal_eenheid(energie_selectie, corrigeer_temp), "Dag": "Dag van het Jaar"},
    markers=False  
)

# Update x-as en legenda
fig_jaar.update_layout(
    xaxis_title="Dagen in het Jaar",
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.3,
        xanchor="center",
        x=0.5
    )  
)

st.plotly_chart(fig_jaar, use_container_width=True)

# Alleen referentievergelijking beperken tot max_dag_2025
df_jaarselectie_referentie = df[
    (df["Location"].isin(locatie_selectie)) &
    (df["Energiestroom"] == energie_selectie) &
    (df["Dag"] <= max_dag_2025)  # Alleen tot dezelfde dag als in 2025
].copy()

df_verbruik_per_dag_referentie = df_jaarselectie_referentie.groupby(["Year", "Dag"])[y_value].sum().reset_index()

# Bereken verbruik per jaar, beperkt tot max_dag_2025
df_verbruik_jaar_referentie = df_jaarselectie_referentie.groupby("Year")[y_value].sum().reset_index()
df_verbruik_jaar_referentie.columns = ["Jaar", "Verbruik in Periode (kWh)"]

verbruik_per_jaar = {jaar: df_verbruik_jaar_referentie.loc[df_verbruik_jaar_referentie["Jaar"] == jaar, "Verbruik in Periode (kWh)"].sum() for jaar in df_verbruik_jaar_referentie["Jaar"]}

# Procentuele referentieverschillen t.o.v. vorige jaren
delta_2024 = ((verbruik_per_jaar[2024] - verbruik_per_jaar[2023]) / verbruik_per_jaar[2023]) * 100 if verbruik_per_jaar[2023] != 0 else 0
delta_2025 = ((verbruik_per_jaar[2025] - verbruik_per_jaar[2024]) / verbruik_per_jaar[2024]) * 100 if verbruik_per_jaar[2024] != 0 else 0

eenheid_metric = bepaal_eenheid_metric(energie_selectie)

# Bepaal welke jaren beschikbaar zijn in de dataset
beschikbare_jaren = sorted([jaar for jaar in [2023, 2024, 2025] if jaar in verbruik_per_jaar])

# Maak alleen het aantal kolommen dat nodig is
cols = st.columns(len(beschikbare_jaren))  

# Vul de kolommen dynamisch
for i, jaar in enumerate(beschikbare_jaren):
    if jaar == 2023:
        delta = "NVT"
        delta_color = "off"  # Zet de kleur op 'off' voor 2023
    else:
        delta = f"{((verbruik_per_jaar[jaar] - verbruik_per_jaar.get(jaar - 1, 0)) / verbruik_per_jaar.get(jaar - 1, 1)) * 100:.2f}%"
        delta_color = "inverse"

    with cols[i]:
        st.metric(label=f"Verbruik {jaar}", value=f"{verbruik_per_jaar[jaar]:,.0f} {eenheid_metric}", delta=delta, delta_color=delta_color)

st.markdown("<br><br><br>", unsafe_allow_html=True)















# ==================== Piekdetectie ==================== #
st.subheader("PIEKDETECTIE ANALYSE")
# Selectbox voor periode
periode_optie = st.selectbox(
    "Selecteer periode",
    ["Afgelopen maand", "Laatste twee maanden", "Laatste drie maanden", "Afgelopen jaar"],
    index=2  # Standaard op 3 maanden
)

# Bepaal het aantal maanden op basis van de keuze
maanden = {"Afgelopen maand": 1, "Laatste twee maanden": 2, "Laatste drie maanden": 3, "Afgelopen jaar": 12}[periode_optie]

# Gebruik bestaande filters voor locatie en energiestroom
df_piek = df[
    (df["Location"].isin(locatie_selectie)) &
    (df["Energiestroom"] == energie_selectie)
].copy()

# Selecteer de juiste kolom afhankelijk van de checkbox
y_value = "Verbruik gecorrigeerd" if corrigeer_temp else "Verbruik totaal"

# Zorg dat de datum in het juiste format staat en filter op de gekozen periode
df_piek["Datum & tijd"] = pd.to_datetime(df_piek["Datum & tijd"])
df_piek = df_piek[df_piek["Datum & tijd"] >= df_piek["Datum & tijd"].max() - pd.DateOffset(months=maanden)]

# Zet datum als index
df_piek = df_piek.set_index("Datum & tijd")

# Resample naar uur-interval en neem de som per uur
df_piek = df_piek.resample("H").sum().reset_index()

# Nieuwe drempelberekening per energiestroom
df_piek["Moving_Avg"] = df_piek[y_value].rolling(window=24, min_periods=1).mean()

df_piek["Q1"] = df_piek[y_value].quantile(0.25)
df_piek["Q3"] = df_piek[y_value].quantile(0.75)
df_piek["IQR"] = df_piek["Q3"] - df_piek["Q1"]

# Dynamische piekdrempels: verschillende factoren per energiestroom
piekfactoren = {"Elektriciteit": 1.25, "Gas": 1.6}  # Gas heeft een hogere drempel
factor = piekfactoren.get(energie_selectie, 1.5)  # Standaard factor als energie_selectie ontbreekt
df_piek["Threshold"] = df_piek["Moving_Avg"] + factor * df_piek["IQR"]

df_piek["Is_Peak"] = df_piek[y_value] > df_piek["Threshold"]
df_peaks = df_piek[df_piek["Is_Peak"]].copy()

# Controleer of er pieken zijn gevonden
if not df_peaks.empty:
    df_peaks["Piek Moment"] = df_peaks["Datum & tijd"].dt.strftime("%Y-%m-%d %H:%M")

# Visualisatie: Lijngrafiek met pieken en trendlijn
fig = px.line(df_piek, x="Datum & tijd", y=y_value, title=f"Gedetecteerde {energie_selectie} pieken in {periode_optie}" + (" (gecorrigeerd voor temperatuur)" if corrigeer_temp else ""))

# Trendlijn toevoegen
fig.add_scatter(x=df_piek["Datum & tijd"], y=df_piek["Moving_Avg"], mode='lines', name="Trendlijn (Moving Average)")

# Markeer piekpunten
if not df_peaks.empty:
    fig.add_scatter(x=df_peaks["Datum & tijd"], y=df_peaks[y_value], mode='markers', name="Pieken", marker=dict(color="red", size=8))

# Grafiek opmaak: Legenda onderaan
fig.update_layout(
    xaxis_title="Datum",
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.3,
        xanchor="center",
        x=0.5
    ),
    legend_title_text=""
)

st.plotly_chart(fig, use_container_width=True)

# Toon pieken in een tabel
if not df_peaks.empty:
    df_peaks_display = df_peaks[["Piek Moment", y_value]].set_index("Piek Moment")
    st.dataframe(df_peaks_display, use_container_width=True)
else:
    st.info(f"Geen significante pieken gevonden in de gekozen periode ({periode_optie}).")
st.markdown("<br><br><br>", unsafe_allow_html=True)



























# ==================== Verbruiksdistributie per Temperatuur ==================== #
st.subheader("TEMPERATUUR ANALYSE")

# Gebruik bestaande filters voor locatie en energiestroom
df_temp_analyse = df[
    (df["Location"].isin(locatie_selectie)) &
    (df["Energiestroom"] == energie_selectie)
].copy()

# Temperatuur selectie via slider (afronden op hele graden)
min_temp, max_temp = int(df_temp_analyse["Temp"].min()), int(df_temp_analyse["Temp"].max())

temp_range = st.slider(
    "Selecteer temperatuurbereik:",
    min_value=min_temp, 
    max_value=max_temp, 
    value=(min_temp, max_temp),
    step=1  # Zorgt ervoor dat de gebruiker alleen hele graden kan selecteren
)

# Filter de dataset op geselecteerd temperatuurbereik
df_temp_analyse = df_temp_analyse[
    (df_temp_analyse["Temp"] >= temp_range[0]) & 
    (df_temp_analyse["Temp"] <= temp_range[1])
]

# Dag/Nacht categoriseren
df_temp_analyse["Uur"] = pd.to_datetime(df_temp_analyse["Datum & tijd"]).dt.hour
df_temp_analyse["Moment van de dag"] = df_temp_analyse["Uur"].apply(lambda x: "Dag" if 6 <= x < 18 else "Nacht")

# Gebruik de functie om de juiste as-titel te bepalen
x_as_titel = bepaal_eenheid(energie_selectie, corrigeer_temp)

y_column = "Verbruik gecorrigeerd" if corrigeer_temp else "Verbruik totaal"

# Maak histogram van verbruik (x-as: verbruik, y-as: frequentie)
fig = px.histogram(
    df_temp_analyse, 
    x=y_column,  # X-as is het geselecteerde verbruikstype
    color="Moment van de dag",  # Dag/Nacht onderscheid
    barmode="group",  # Zet dag en nacht naast elkaar
    title=f"Frequentie van {energie_selectie} verbruik bij Temperatuur ({temp_range[0]}°C - {temp_range[1]}°C)",
    opacity=0.8,  
    nbins=30  # Aantal bins voor betere verdeling
)

# Aanpassingen aan de layout
fig.update_layout(
    xaxis_title=x_as_titel,  # Dynamisch gekozen titel
    yaxis_title="Frequentie",
    legend_title="Moment van de dag",
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.2,
        xanchor="center",
        x=0.5
    )
)

# Toon de plot
st.plotly_chart(fig, use_container_width=True)
st.markdown("<br><br><br>", unsafe_allow_html=True)

# Bepaal Q1, Q3 en IQR
Q1 = df_temp_analyse[y_column].quantile(0.25)
Q3 = df_temp_analyse[y_column].quantile(0.75)
IQR = Q3 - Q1

# Bepaal outlier grens (bovenkant)
upper_bound = Q3 + 1.5 * IQR

# Filter outliers (waarden boven de grens)
df_outliers = df_temp_analyse[df_temp_analyse[y_column] > upper_bound]

# Sorteer de outliers op verbruik van hoog naar laag
df_outliers = df_outliers.sort_values(by=y_column, ascending=False)

# Selecteer relevante kolommen voor analyse
df_outliers = df_outliers[["Datum & tijd", "Temp", y_column, "Moment van de dag"]]

# Weergeven als een tabel in Streamlit
if not df_outliers.empty:
    st.write("Hieronder zie je de metingen met extreem hoog verbruik:")
    st.dataframe(df_outliers, use_container_width=True)
else:
    st.success("Er zijn geen extreme uitschieters in het verbruik.")





















# ==================== LOCATIE BENCHMARKING TOOL ==================== #
st.subheader("LOCATIE BENCHMARKING TOOL")

# Dummy oppervlakte per locatie
oppervlakte_m2 = {"Loosduinen": 12726, "Royal&Rustiek": 10199, "Mechropa": 5348}

# Filter de data voor de geselecteerde periode en energiestroom
df_locatie_benchmark = df[
    (df["Datum & tijd"] >= pd.to_datetime(date1)) & 
    (df["Datum & tijd"] <= pd.to_datetime(date2)) &
    (df["Energiestroom"] == energie_selectie)  # Alleen geselecteerde energiestroom tonen
].copy()

# Groeperen per locatie en energiestroom
df_locatie_benchmark = df_locatie_benchmark.groupby(["Location"])["Verbruik totaal"].sum().reset_index()

# Bereken verbruik per m² voor elektriciteit en gas
df_locatie_benchmark["Oppervlakte (m²)"] = df_locatie_benchmark["Location"].map(oppervlakte_m2)
df_locatie_benchmark["Verbruik per m²"] = (df_locatie_benchmark["Verbruik totaal"] / df_locatie_benchmark["Oppervlakte (m²)"]).fillna(0).round(2)

# Kolomtitel aanpassen afhankelijk van energiestroom
eenheid = "kWh/m²" if energie_selectie == "Elektriciteit" else "m³/m²"
kolom_te_tonen = f"Verbruik per m² ({eenheid})"

# Hernoem kolom voor consistentie
df_locatie_benchmark.rename(columns={"Verbruik per m²": kolom_te_tonen}, inplace=True)

# Barplot van verbruik per m²
fig = px.bar(df_locatie_benchmark, 
             x="Location", 
             y=kolom_te_tonen, 
             title=f"Verbruik per m² voor {energie_selectie}",
             labels={"Location": "Locatie", kolom_te_tonen: f"Verbruik ({eenheid})"},
             color="Location",
             barmode="group",
             width = 600,)

# Grafiek Layout Updaten
fig.update_layout(
    xaxis_title='',  
    yaxis_title=f"Verbruik per m²)",
    showlegend=False,
)

# Toon de grafiek
st.plotly_chart(fig, use_container_width= False)