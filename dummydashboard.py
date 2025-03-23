import streamlit as st
import plotly.express as px
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

#streamlit run /Users/private/Library/CloudStorage/OneDrive-SharedLibraries-StudentConsultant/Business\ -\ Documents/General/03.\ Deliverables/Dummydashboard.py


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
            margin-left: 10% !important;  /* Zorgt voor betere uitlijning */
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

st.markdown(
    """
    <style>
        /* Fix: Zorg dat de hoofdinhoud volledig gecentreerd wordt */
        .block-container {
            max-width: 100% !important; /* Pas de breedte aan (100% kan ook) */
            margin: auto; /* Centreer de inhoud */
        }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------- Opening ------------------------ #
st.title("ENERGIE DASHBOARD SAFFIER")
st.logo("logo.png")
#st.logo('/Users/private/Library/CloudStorage/OneDrive-SharedLibraries-StudentConsultant/Business - Documents/General/03. Deliverables/logo.png')


# --------------------- DATA ------------------------ #
# @st.cache_data(ttl=1200) #20min
@st.cache_data(ttl=86400)
def load_data():
    df = pd.read_excel("/Users/private/Library/CloudStorage/OneDrive-SharedLibraries-StudentConsultant/Business - Documents/General/03. Deliverables/Dummydata_BI.xlsx")
    df["Datum & tijd"] = pd.to_datetime(df["Datum & tijd"])
    return df

df = load_data()  

# --------------------- FILTERS ------------------------ #

# Sidebar filters
st.sidebar.header("🔍 Filter data:")

# Locatie filter (standaard "Loosduinen" geselecteerd)
locaties = df["Location"].unique()
locatie_selectie = st.sidebar.selectbox("Locatie", options=locaties, index=None, placeholder="Selecteer een locatie")

# Energietype filter (zonder zonnepanelen, geen standaardwaarde)
energie_stromen = [e for e in df["Energiestroom"].unique() if e != "Zonnepanelen"]
energie_selectie = st.sidebar.selectbox("Energiestromen", options=energie_stromen, index=None, placeholder="Selecteer een energiestroom")

# Checkbox voor temperatuurcorrectie
corrigeer_temp = st.sidebar.checkbox("Corrigeer verbruik voor temperatuur om beter te kunnen vergelijken")
verbruik_col = "Verbruik gecorrigeerd" if corrigeer_temp else "Verbruik totaal"

# Filter de dataset op gekozen waarden
df_filtered = df[
    (df["Location"] == locatie_selectie) & 
    (df["Energiestroom"] == energie_selectie)
]
df_filtered2 = df[df["Location"] == locatie_selectie]

# Controleer of de gebruiker een selectie heeft gemaakt
if not locatie_selectie or not energie_selectie:
    st.warning("🔍 Selecteer een Locatie en een Energiestroom om de data te analyseren.")
    st.stop()

# Controleer of er data beschikbaar is voor de geselecteerde filters
if df_filtered.empty:
    st.warning(f"⚠️ Geen {energie_selectie} data beschikbaar voor de locatie {locatie_selectie} en de geselecteerde filters.")
    st.stop()


# --------------------- HULPFUNCTIES ------------------------ #
def bepaal_eenheid(energiestroom, corrigeer_temp=False):
    """
    Retourneert de juiste eenheid voor gas, elektriciteit en water,
    en voegt '(gecorrigeerd)' toe als temperatuurcorrectie is toegepast.
    """
    if "Gas" in energiestroom:
        eenheid = "Verbruik (m³)"
    elif "Elektriciteit" in energiestroom:
        eenheid = "Verbruik (kWh)"
    elif "Water" in energiestroom:
        eenheid = "Verbruik (m³)"
    else:
        eenheid = "Verbruik"  # Fallback
    
    if corrigeer_temp and "Elektriciteit" in energiestroom:  # Alleen elektriciteit wordt gecorrigeerd voor temperatuur
        eenheid += " (gecorrigeerd)"
    
    return eenheid

def bepaal_eenheid_metric(energiestroom):
    """
    Retourneert alleen de eenheid (kWh of m³), zonder het woord 'Verbruik'.
    Handig voor gebruik in `st.metric()`.
    """
    if "Gas" in energiestroom or "Water" in energiestroom:
        return "m³"
    return "kWh"











# ---------------------VISUALISATIE LIJNPLOT------------------------ # 
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
    (df["Location"] == (locatie_selectie)) &
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

st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)



















# ==================== EMISSIEFACTOREN EN TARIEVEN ==================== #
# https://co2emissiefactoren.nl/factoren/2025/11/elektriciteit/?unit=kwh 

# Definieer de tarieven 
GAS_PRIJS = {2023: 0.6286, 2024: 0.6394, 2025: 0.5077}  # Euro per m³
ELEKTRA_PRIJS = {2023: 0.2198, 2024: 0.1632, 2025: 0.1300}  # Euro per kWh
WATER_PRIJS = {2023: 1.20, 2024: 1.25, 2025: 1.30}  # Euro per m³ (geschat)

# CO₂-emissiefactoren per eenheid (geen CO₂ voor water)
CO2_FACTOR = {
    "Elektriciteit": {2023: 0.337, 2024: 0.328, 2025: 0.268},  # kg CO₂ per kWh
    "Gas": {2023: 2.079, 2024: 2.134, 2025: 2.134},  # kg CO₂ per m³
}











# ---------------------VISUALISATIE LIJNPLOT------------------------ # 
st.subheader(f"YEAR TO YEAR OVERZICHT {energie_selectie.upper()}")

# ---- VOORBEREIDING ---- #
df_overzicht = df[df['Location'] == locatie_selectie].copy()
df_overzicht['Date'] = pd.to_datetime(df_overzicht['Datum & tijd'])
df_overzicht['Year'] = df_overzicht['Date'].dt.year
df_overzicht['Dag'] = df_overzicht['Date'].dt.day_of_year
max_dag_2025 = df_overzicht[df_overzicht['Year'] == 2025]['Dag'].max()
df_referentie_2024 = df_overzicht[df_overzicht['Dag'] <= max_dag_2025]

# Groepeer
df_jaar = df_overzicht.groupby(["Year", "Energiestroom"])[["Verbruik totaal", "Verbruik gecorrigeerd"]].sum().unstack()
df_ref = df_referentie_2024.groupby(["Year", "Energiestroom"])[["Verbruik totaal", "Verbruik gecorrigeerd"]].sum().unstack()

# Dicts
v_norm = df_jaar["Verbruik totaal"].to_dict()
v_corr = df_jaar["Verbruik gecorrigeerd"].to_dict()
r_norm = df_ref["Verbruik totaal"].to_dict()
r_corr = df_ref["Verbruik gecorrigeerd"].to_dict()

# Tarieven en CO₂-factors
kosten_tarief = {"Elektriciteit": ELEKTRA_PRIJS, "Gas": GAS_PRIJS, "Water": WATER_PRIJS}
co2_factor = CO2_FACTOR.get(energie_selectie, {})

# Hulpfunctie
def calc_delta(curr, prev):
    return f"{((curr - prev) / prev) * 100:.1f}%" if prev else "NVT"

eenheid = bepaal_eenheid_metric(energie_selectie)

# ---- METRICS WEERGAVE ---- #
st.subheader(f"{locatie_selectie} – {energie_selectie}")
col_links, col_rechts = st.columns(2)

with col_links:
    st.markdown("### Werkelijk verbruik")
    for jaar in [2023, 2024, 2025]:
        verbruik = v_norm[energie_selectie].get(jaar, 0)
        kosten = verbruik * kosten_tarief[energie_selectie][jaar]
        co2 = verbruik * co2_factor.get(jaar, 0) if energie_selectie in CO2_FACTOR else None

        # ➤ Correcte referentie: 2024 vs 2023, 2025 vs referentieperiode 2024
        if jaar == 2024:
            prev = v_norm[energie_selectie].get(2023, 0)
        elif jaar == 2025:
            prev = r_norm[energie_selectie].get(2024, 0)
        else:
            prev = None

        delta_v = calc_delta(verbruik, prev) if prev else "NVT"
        delta_k = calc_delta(kosten, prev * kosten_tarief[energie_selectie].get(jaar - 1, 0)) if prev else "NVT"
        delta_c = calc_delta(co2, prev * co2_factor.get(jaar - 1, 0)) if prev and energie_selectie in CO2_FACTOR else "NVT"

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(f"Verbruik {jaar}", f"{verbruik:,.0f} {eenheid}", delta=delta_v)
        with c2:
            st.metric(f"Kosten {jaar}", f"€{kosten:,.2f}", delta=delta_k)
        with c3:
            if co2 is not None:
                st.metric(f"CO₂-uitstoot {jaar}", f"{co2:,.0f} kg", delta=delta_c)


with col_rechts:
    st.markdown("### Gecorrigeerd verbruik")
    for jaar in [2023, 2024, 2025]:
        verbruik = v_corr[energie_selectie].get(jaar, 0)
        kosten = verbruik * kosten_tarief[energie_selectie][jaar]
        co2 = verbruik * co2_factor.get(jaar, 0) if energie_selectie in CO2_FACTOR else None

        # Vergelijk 2024 vs 2023 en 2025 vs referentie 2024
        if jaar == 2024:
            prev = v_corr[energie_selectie].get(2023, 0)
        elif jaar == 2025:
            prev = r_corr[energie_selectie].get(2024, 0)
        else:
            prev = None

        delta_v = calc_delta(verbruik, prev) if prev else "NVT"
        delta_k = calc_delta(kosten, prev * kosten_tarief[energie_selectie].get(jaar - 1, 0)) if prev else "NVT"
        delta_c = calc_delta(co2, prev * co2_factor.get(jaar - 1, 0)) if prev and energie_selectie in CO2_FACTOR else "NVT"

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(f"Verbruik {jaar}", f"{verbruik:,.0f} {eenheid}", delta=delta_v)
        with c2:
            st.metric(f"Kosten {jaar}", f"€{kosten:,.2f}", delta=delta_k)
        with c3:
            if co2 is not None:
                st.metric(f"CO₂-uitstoot {jaar}", f"{co2:,.0f} kg", delta=delta_c)
st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)

















# --------------------- VISUALISATIE ZONNEPANELEN ------------------------ #
if energie_selectie == "Elektriciteit":  # Alleen tonen bij elektriciteit
    st.subheader(f'ZONNEPANELEN OPBRENGST VOOR {locatie_selectie.upper()}')

    # Datumselectie
    startDate = df["Datum & tijd"].min()
    endDate = df["Datum & tijd"].max()

    col1, col2 = st.columns((2))
    with col1:
        date1_zonnepanelen = st.date_input("Start Datum", startDate, key="start_zonnepanelen")
    with col2:
        date2_zonnepanelen = st.date_input("Eind Datum", endDate, key="eind_zonnepanelen")

    # Filter zonnepaneeldata
    df_zonnepanelen = df[
        (df["Datum & tijd"] >= pd.to_datetime(date1_zonnepanelen)) &
        (df["Datum & tijd"] <= pd.to_datetime(date2_zonnepanelen)) &
        (df["Location"] == locatie_selectie) &
        (df["Energiestroom"] == "Zonnepanelen")
    ].copy()

    # Filter temperatuurdata los
    df_temperatuur = df[
        (df["Datum & tijd"] >= pd.to_datetime(date1_zonnepanelen)) &
        (df["Datum & tijd"] <= pd.to_datetime(date2_zonnepanelen)) &
        (df["Location"] == locatie_selectie)
    ][["Datum & tijd", "Temp"]].dropna().copy()

    # Check of er zonnepaneeldata is
    if df_zonnepanelen.empty:
        st.warning(f"⚠️ Geen zonnepaneeldata beschikbaar voor {locatie_selectie}. Mogelijk geen zonnepanelen of nog niet geïntegreerd.")
    else:
        # Intervalkeuze + temperatuur toggle
        interval_zonnepanelen = st.selectbox("Selecteer interval", ["Uur", "Dag", "Week"], key="interval_zonnepanelen")
        toon_temp_zonnepanelen = st.checkbox("Toon temperatuur in grafiek", key="toon_temp_zonnepanelen")

        # Sorteren & index
        df_zonnepanelen = df_zonnepanelen.sort_values("Datum & tijd").set_index("Datum & tijd")
        df_temperatuur = df_temperatuur.sort_values("Datum & tijd").set_index("Datum & tijd")

        # Aggregatie
        if interval_zonnepanelen == "Dag":
            df_zonnepanelen = df_zonnepanelen.resample("D").sum().reset_index()
            df_temperatuur = df_temperatuur.resample("D").mean().reset_index() if toon_temp_zonnepanelen and not df_temperatuur.empty else None
        elif interval_zonnepanelen == "Week":
            df_zonnepanelen = df_zonnepanelen.resample("W").sum().reset_index()
            df_temperatuur = df_temperatuur.resample("W").mean().reset_index() if toon_temp_zonnepanelen and not df_temperatuur.empty else None
        else:
            df_zonnepanelen = df_zonnepanelen.reset_index()
            df_temperatuur = df_temperatuur.reset_index() if toon_temp_zonnepanelen and not df_temperatuur.empty else None

        # Titels
        y_axis_title = "Opbrengst Zonnepanelen (kWh)"
        y_axis2_title = "Temperatuur (°C)"

        # Grafiek
        fig = px.line(
            df_zonnepanelen,
            x="Datum & tijd",
            y="Verbruik totaal",
            labels={"Verbruik totaal": y_axis_title, "Datum & tijd": "Tijd"},
            markers=True
        )

        # Voeg temperatuur toe
        if toon_temp_zonnepanelen and df_temperatuur is not None and not df_temperatuur.empty:
            fig.add_scatter(
                x=df_temperatuur["Datum & tijd"],
                y=df_temperatuur["Temp"],
                mode="lines",
                name=y_axis2_title,
                yaxis="y2"
            )

            # Tweede y-as instellen
            fig.update_layout(
                yaxis=dict(title=y_axis_title),
                yaxis2=dict(
                    title=y_axis2_title,
                    overlaying="y",
                    side="right",
                    showgrid=False
                )
            )

        # Legenda onderaan gecentreerd
        fig.update_layout(
            xaxis_title="Opbrengst van geselecteerde periode",
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
st.markdown("<br><br><br>", unsafe_allow_html=True)
















# ==================== DYNAMISCHE MAANDVERGELIJKING ==================== #
st.subheader("DYNAMISCHE MAANDVERGELIJKING")

# Zorg ervoor dat maanden correct gesorteerd zijn (indien als string, zet om naar datetime en terug naar string)
maanden_uniek = sorted(df["Month"].unique(), key=lambda x: pd.to_datetime(x, format="%B").month)

# Selecteer een maand uit de gesorteerde maanden
maand_optie = st.selectbox(
    "Selecteer een maand om te vergelijken",
    options=maanden_uniek,
    index=0
)

# Filter de dataset op geselecteerde locatie, energiestroom en maand
df_maandselectie = df[
    (df["Location"] == locatie_selectie) &
    (df["Energiestroom"] == energie_selectie) &
    (df["Month"] == maand_optie)
].copy()

# Controleer of er data is voor de geselecteerde maand
if df_maandselectie.empty:
    st.warning(f"⚠️ Geen data beschikbaar voor {energie_selectie} in {maand_optie} op locatie {locatie_selectie}.")
else:
    # Selecteer de juiste kolom afhankelijk van de checkbox
    y_value = "Verbruik gecorrigeerd" if corrigeer_temp else "Verbruik totaal"
    x_as_titel = bepaal_eenheid(energie_selectie, corrigeer_temp)

    # Data groeperen per dag en uur voor vergelijking
    df_maandselectie["Datum & tijd"] = pd.to_datetime(df_maandselectie["Datum & tijd"])
    df_maandselectie["Dag"] = df_maandselectie["Datum & tijd"].dt.day
    df_maandselectie["Uur"] = df_maandselectie["Datum & tijd"].dt.hour

    df_verbruik_per_uur = df_maandselectie.groupby(["Year", "Dag", "Uur"])[y_value].sum().reset_index()

    # Maak een uniforme tijdlijn per jaar
    df_verbruik_per_uur["Virtuele_Tijd"] = pd.to_datetime(
        f"2025-{maand_optie}-" + df_verbruik_per_uur["Dag"].astype(str) + " " +
        df_verbruik_per_uur["Uur"].astype(str) + ":00"
    )

    # Plot verbruik per uur met jaren als vergelijking
    fig = px.line(
        df_verbruik_per_uur,
        x="Virtuele_Tijd",
        y=y_value,
        color="Year",
        title=f"{energie_selectie} verbruik in {maand_optie}" + (" (gecorrigeerd)" if corrigeer_temp else ""),
        labels={y_value: x_as_titel, "Virtuele_Tijd": "Datum & Uur"},
        markers=False
    )

    # Update de x-as voor een duidelijke tijdsweergave
    fig.update_layout(
        xaxis_title=f"Dagen in {maand_optie}",
        xaxis=dict(tickmode="auto", tickformat="%d %b"),
        legend=dict(orientation="h", yanchor="top", y=-0.3, xanchor="center", x=0.5)
    )

    st.plotly_chart(fig, use_container_width=True)

    # ==================== TOTAAL VERBRUIK PER JAAR ==================== #
    df_verbruik_totaal = df_maandselectie.groupby("Year")[y_value].sum().reset_index()
    df_verbruik_totaal.columns = ["Jaar", "Totaal Verbruik"]

    # Bestaande jaren ophalen
    beschikbare_jaren = df_verbruik_totaal["Jaar"].unique().tolist()

    # Verbruik per jaar ophalen (indien aanwezig)
    verbruik_per_jaar = {jaar: df_verbruik_totaal.loc[df_verbruik_totaal["Jaar"] == jaar, "Totaal Verbruik"].sum()
                         for jaar in beschikbare_jaren}

    # Procentuele delta's berekenen (indien beide jaren aanwezig zijn)
    def bereken_delta(huidig, vorig):
        if vorig == 0 or vorig is None:
            return "NVT"
        return ((huidig - vorig) / vorig) * 100

    delta_2024 = bereken_delta(verbruik_per_jaar.get(2024, 0), verbruik_per_jaar.get(2023, 0))
    delta_2025 = bereken_delta(verbruik_per_jaar.get(2025, 0), verbruik_per_jaar.get(2024, 0))

    # Dynamisch tonen van metrics (alleen als het jaar data heeft)
    eenheid_metric = bepaal_eenheid_metric(energie_selectie)

    kolommen = st.columns(len(beschikbare_jaren))

    for i, jaar in enumerate(beschikbare_jaren):
        delta = delta_2024 if jaar == 2024 else (delta_2025 if jaar == 2025 else "NVT")
        delta_color = "inverse" if isinstance(delta, (int, float)) and delta < 0 else "normal" if isinstance(delta, (int, float)) else "off"

        kolommen[i].metric(
            label=f"Verbruik {maand_optie} {jaar}",
            value=f"{verbruik_per_jaar[jaar]:,.0f} {eenheid_metric}",
            delta=f"{delta:.2f}%" if isinstance(delta, (int, float)) else "NVT",
            delta_color=delta_color
        )

st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)

















# ==================== DYNAMISCHE KWARTAALVERGELIJKING ==================== #
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

# Zet "Datum & tijd" correct naar datetime-formaat en extraheer de maand
df["Datum & tijd"] = pd.to_datetime(df["Datum & tijd"])
df["Month"] = df["Datum & tijd"].dt.month

# Filter de dataset op locatie, energiestroom en geselecteerde maanden
df_kwartaal = df[
    (df["Location"] == locatie_selectie) &
    (df["Energiestroom"] == energie_selectie) &
    (df["Month"].isin(kwartaal_maanden[kwartaal_optie]))
].copy()

# Controleer of er data beschikbaar is
if df_kwartaal.empty:
    st.warning(f"⚠️ Geen data beschikbaar voor {energie_selectie} in {kwartaal_optie} op locatie {locatie_selectie}.")
else:
    # Selecteer de juiste kolom afhankelijk van de temperatuurcorrectie
    y_value = "Verbruik gecorrigeerd" if corrigeer_temp else "Verbruik totaal"

    # Bereken verbruik per dag
    df_kwartaal["Dag"] = df_kwartaal["Datum & tijd"].dt.day_of_year
    df_verbruik_per_dag_kwartaal = df_kwartaal.groupby(["Year", "Dag"])[y_value].sum().reset_index()

    # Lijngrafiek maken
    fig_kwartaal = px.line(
        df_verbruik_per_dag_kwartaal,
        x="Dag",
        y=y_value,
        color="Year",
        title=f"{energie_selectie} verbruik in {kwartaal_optie}" + (" (gecorrigeerd)" if corrigeer_temp else ""),
        labels={y_value: bepaal_eenheid(energie_selectie, corrigeer_temp), "Dag": "Dag van het Jaar"},
        markers=False
    )

    fig_kwartaal.update_layout(
        xaxis_title="Dagen in het Kwartaal",
        xaxis=dict(tickmode="auto", tickformat="%d"),
        legend=dict(orientation="h", yanchor="top", y=-0.3, xanchor="center", x=0.5)
    )

    st.plotly_chart(fig_kwartaal, use_container_width=True)

    # ==================== TOTAAL VERBRUIK PER KWARTAAL ==================== #
    df_verbruik_kwartaal = df_kwartaal.groupby("Year")[y_value].sum().reset_index()
    df_verbruik_kwartaal.columns = ["Jaar", "Totaal Verbruik"]

    # Alleen jaren opslaan die daadwerkelijk data hebben
    beschikbare_jaren = df_verbruik_kwartaal["Jaar"].tolist()
    verbruik_per_kwartaal = {jaar: df_verbruik_kwartaal.loc[df_verbruik_kwartaal["Jaar"] == jaar, "Totaal Verbruik"].sum() for jaar in beschikbare_jaren}

    # Procentuele delta's correct berekenen zonder KeyErrors
    def bereken_delta(huidig, vorig):
        if vorig == 0 or vorig is None:
            return "NVT"
        return ((huidig - vorig) / vorig) * 100

    delta_2024 = bereken_delta(verbruik_per_kwartaal.get(2024, 0), verbruik_per_kwartaal.get(2023, 0))
    delta_2025 = bereken_delta(verbruik_per_kwartaal.get(2025, 0), verbruik_per_kwartaal.get(2024, 0))

    eenheid_metric = bepaal_eenheid_metric(energie_selectie)

    # Dynamische kolommen maken voor de jaren die beschikbaar zijn
    kolommen = st.columns(len(beschikbare_jaren))

    for i, jaar in enumerate(beschikbare_jaren):
        delta = delta_2024 if jaar == 2024 else (delta_2025 if jaar == 2025 else "NVT")
        delta_color = "inverse" if isinstance(delta, (int, float)) and delta < 0 else "normal" if isinstance(delta, (int, float)) else "off"

        with kolommen[i]:
            st.metric(
                label=f"Verbruik {kwartaal_optie} {jaar}",
                value=f"{verbruik_per_kwartaal[jaar]:,.0f} {eenheid_metric}",
                delta=f"{delta:.2f}%" if isinstance(delta, (int, float)) else "NVT",
                delta_color=delta_color
            )

st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)



















# ==================== DYNAMISCHE JAARVERGELIJKING ==================== #
st.subheader("DYNAMISCHE JAARVERGELIJKING")

# Datum naar datetime en dagnummer berekenen
df["Datum & tijd"] = pd.to_datetime(df["Datum & tijd"])
df["Dag"] = df["Datum & tijd"].dt.day_of_year  

# Bepaal de maximale dag met data in 2025
max_dag_2025 = df[df["Year"] == 2025]["Dag"].max()

# === **Controle of er data is voor de locatie en energiestroom** === #
df_jaarselectie_volledig = df[
    (df["Location"] == locatie_selectie) &
    (df["Energiestroom"] == energie_selectie)
].copy()

if df_jaarselectie_volledig.empty:
    st.warning(f"⚠️ Geen data beschikbaar voor {energie_selectie} op locatie {locatie_selectie}.")
else:
    # **Verbruik per dag voor de volledige dataset**
    df_verbruik_per_dag_volledig = df_jaarselectie_volledig.groupby(["Year", "Dag"])[y_value].sum().reset_index()

    # === **Lijngrafiek: Verbruik per dag per jaar** === #
    fig_jaar = px.line(
        df_verbruik_per_dag_volledig, 
        x="Dag",  
        y=y_value,  
        color="Year", 
        title=f"Jaarlijkse {energie_selectie} vergelijking per dag" + (" (gecorrigeerd)" if corrigeer_temp else ""),
        labels={y_value: bepaal_eenheid(energie_selectie, corrigeer_temp), "Dag": "Dag van het Jaar"},
        markers=False  
    )

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

    # **Filter voor referentievergelijking tot max_dag_2025**
    df_jaarselectie_referentie = df[
        (df["Location"] == locatie_selectie) &
        (df["Energiestroom"] == energie_selectie) &
        (df["Dag"] <= max_dag_2025)
    ].copy()

    # **Bereken verbruik per jaar, beperkt tot max_dag_2025**
    df_verbruik_jaar_referentie = df_jaarselectie_referentie.groupby("Year")[y_value].sum().reset_index()
    df_verbruik_jaar_referentie.columns = ["Jaar", "Verbruik in Periode"]

    # **Sla alleen jaren op die daadwerkelijk bestaan**
    beschikbare_jaren = df_verbruik_jaar_referentie["Jaar"].tolist()
    verbruik_per_jaar = {
        jaar: df_verbruik_jaar_referentie.loc[df_verbruik_jaar_referentie["Jaar"] == jaar, "Verbruik in Periode"].sum()
        for jaar in beschikbare_jaren
    }

    # === **Procentuele verschillen correct berekenen** === #
    def bereken_delta(huidig, vorig):
        if vorig == 0 or vorig is None:
            return "NVT"
        return ((huidig - vorig) / vorig) * 100

    delta_2024 = bereken_delta(verbruik_per_jaar.get(2024, 0), verbruik_per_jaar.get(2023, 0))
    delta_2025 = bereken_delta(verbruik_per_jaar.get(2025, 0), verbruik_per_jaar.get(2024, 0))

    eenheid_metric = bepaal_eenheid_metric(energie_selectie)

    # **Dynamische kolommen maken voor bestaande jaren**
    kolommen = st.columns(len(beschikbare_jaren))

    for i, jaar in enumerate(beschikbare_jaren):
        delta = delta_2024 if jaar == 2024 else (delta_2025 if jaar == 2025 else "NVT")
        delta_color = "inverse" if isinstance(delta, (int, float)) and delta < 0 else "normal" if isinstance(delta, (int, float)) else "off"

        with kolommen[i]:
            st.metric(
                label=f"Verbruik {jaar}",
                value=f"{verbruik_per_jaar[jaar]:,.0f} {eenheid_metric}",
                delta=f"{delta:.2f}%" if isinstance(delta, (int, float)) else "NVT",
                delta_color=delta_color
            )

st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)




















# ==================== Piekdetectie ==================== #
st.subheader("PIEKDETECTIE ANALYSE")

# Selectbox voor periode
periode_optie = st.selectbox(
    "Selecteer periode",
    ["Afgelopen maand", "Laatste twee maanden", "Laatste drie maanden", "Afgelopen jaar"],
    index=2  # Standaard op 3 maanden
)

# Slider voor gevoeligheidsinstelling (K-waarde)
k_waarde = st.slider(
    "Gevoeligheid piekdetectie (K-waarde)",
    min_value=1.0, 
    max_value=3.0, 
    value=1.5,  # Standaardwaarde
    step=0.1
)

# Bepaal het aantal maanden op basis van de gekozen periode
maanden = {"Afgelopen maand": 1, "Laatste twee maanden": 2, "Laatste drie maanden": 3, "Afgelopen jaar": 12}[periode_optie]

# Gebruik bestaande filters voor locatie en energiestroom
df_piek = df[
    (df["Location"] == locatie_selectie) &
    (df["Energiestroom"] == energie_selectie)
].copy()

# Selecteer de juiste kolom afhankelijk van de checkbox
y_value = "Verbruik gecorrigeerd" if corrigeer_temp else "Verbruik totaal"

# Zorg dat de datum in het juiste format staat en filter op de gekozen periode
df_piek["Datum & tijd"] = pd.to_datetime(df_piek["Datum & tijd"])
df_piek = df_piek[df_piek["Datum & tijd"] >= df_piek["Datum & tijd"].max() - pd.DateOffset(months=maanden)]

# Zet datum als index en resample per uur
df_piek = df_piek.set_index("Datum & tijd").resample("H").sum().reset_index()

# Berekening van statistische drempelwaarden voor piekdetectie
df_piek["Moving_Avg"] = df_piek[y_value].rolling(window=24, min_periods=1).mean()
df_piek["Q1"] = df_piek[y_value].quantile(0.25)
df_piek["Q3"] = df_piek[y_value].quantile(0.75)
df_piek["IQR"] = df_piek["Q3"] - df_piek["Q1"]

# Dynamische drempel berekening op basis van de sliderwaarde (K-waarde)
df_piek["Threshold"] = df_piek["Moving_Avg"] + k_waarde * df_piek["IQR"]

# Detecteer pieken
df_piek["Is_Peak"] = df_piek[y_value] > df_piek["Threshold"]
df_peaks = df_piek[df_piek["Is_Peak"]].copy()

# Tel het aantal pieken
aantal_pieken = len(df_peaks)

# Visualisatie: Lijngrafiek met pieken en trendlijn
fig = px.line(df_piek, x="Datum & tijd", y=y_value, title=f"")

# Trendlijn toevoegen
fig.add_scatter(x=df_piek["Datum & tijd"], y=df_piek["Moving_Avg"], mode='lines', name="Trendlijn (Moving Average)")

# Markeer piekpunten
if not df_peaks.empty:
    fig.add_scatter(x=df_peaks["Datum & tijd"], y=df_peaks[y_value], mode='markers', name="Pieken", marker=dict(color="red", size=8))

# Grafiek-opmaak: Legenda onderaan
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
st.write(f'Gedetecteerde {energie_selectie} pieken in {periode_optie}{" (gecorrigeerd)" if corrigeer_temp else ""}')
if not df_peaks.empty:
    df_peaks_display = df_peaks[["Datum & tijd", y_value]].rename(columns={"Datum & tijd": "Piek Moment"})
    st.dataframe(df_peaks_display, use_container_width=True)
else:
    st.info(f"Geen significante pieken gevonden in de gekozen periode ({periode_optie}).")
st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
























# ==================== Verbruiksdistributie per Temperatuur ==================== #
st.subheader("TEMPERATUUR ANALYSE")

# Gebruik bestaande filters voor locatie en energiestroom
df_temp_analyse = df[
    (df["Location"] == (locatie_selectie)) &
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
st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)












# ==================== SIMULATIE EFFECT TEMPERATUUR (POLYNOMIAAL) ==================== #
st.subheader("SIMULATIE: EFFECT VAN TEMPERATUUR OP VERBRUIK")

# Alleen tonen als temperatuur beschikbaar is
if "Temp" in df_filtered.columns and not df_filtered["Temp"].isnull().all():

    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import PolynomialFeatures
    from sklearn.pipeline import make_pipeline
    import plotly.graph_objects as go

    # ▸ Slider voor temperatuurverschuiving
    temp_shift = st.slider("Simuleer temperatuurverandering (in °C)", -5, 5, 2)

    # ▸ Data voorbereiden (altijd werkelijke verbruik)
    df_model = df_filtered.copy()
    df_model = df_model[["Temp", "Verbruik totaal"]].dropna()
    verbruik_col = "Verbruik totaal"

    if df_model.empty:
        st.warning("⚠️ Niet genoeg data beschikbaar om simulatie uit te voeren.")
    else:
        # ▸ Polynomiale regressie (graad 2)
        degree = 2
        poly_model = make_pipeline(PolynomialFeatures(degree), LinearRegression())
        poly_model.fit(df_model[["Temp"]], df_model[[verbruik_col]])

        # ▸ Simulatie uitvoeren met kolomnaam behouden (Temp)
        df_model["Simulatie_Verbruik"] = poly_model.predict(
            df_model[["Temp"]].assign(Temp=df_model["Temp"] + temp_shift)
        )

        # ▸ KPI tonen
        verbruik_origineel = df_model[verbruik_col].mean()
        verbruik_simulatie = df_model["Simulatie_Verbruik"].mean()
        delta_pct = (((verbruik_simulatie - verbruik_origineel) / verbruik_origineel) * 100)
        eenheid_simulatie = bepaal_eenheid_metric(energie_selectie)
        delta_label = f"{delta_pct:+.1f}%"


        # ▸ Correct kleurgebruik via numeriek delta + 'normal'
        st.metric(
            label=f"Gesimuleerd verbruik bij {temp_shift:+}°C",
            value=f"{verbruik_simulatie:,.0f} {eenheid_simulatie}",
            delta=f"{delta_pct:.2f}%",
            delta_color="inverse",
        )

        # ▸ Visualisatie
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_model["Temp"], y=df_model[verbruik_col],
            mode="markers", name="Werkelijk verbruik", opacity=0.5
        ))
        fig.add_trace(go.Scatter(
            x=df_model["Temp"], y=df_model["Simulatie_Verbruik"],
            mode="lines", name="Gesimuleerd verbruik (poly)", line=dict(color="orange")
        ))
        fig.update_layout(
            title="Temperatuur vs Verbruik (Polynomiale simulatie)",
            xaxis_title="Temperatuur (°C)",
            yaxis_title=bepaal_eenheid(energie_selectie),
            legend=dict(
                orientation="h", yanchor="top", y=-0.3, xanchor="center", x=0.5
            )
        )
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Temperatuurdata niet beschikbaar voor deze selectie.")
st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
















# ==================== LOCATIE BENCHMARKING TOOL ==================== #
st.subheader("LOCATIE BENCHMARKING TOOL")

# Oppervlakte per locatie 
oppervlakte_m2 = {
    "Loosduinen": 12726,
    "Royal&Rustiek": 10199,
    "Mechropa": 5348,
    "3linden": 7339  
}

# **Filter de data op de geselecteerde periode en energiestroom**
df_locatie_benchmark = df[
    (df["Datum & tijd"] >= pd.to_datetime(date1)) & 
    (df["Datum & tijd"] <= pd.to_datetime(date2)) &
    (df["Energiestroom"] == energie_selectie)  # Alleen geselecteerde energiestroom tonen
].copy()

# **Check of er data is na filtering**
if df_locatie_benchmark.empty:
    st.warning(f"⚠️ Geen data beschikbaar voor {energie_selectie} in de geselecteerde periode.")
else:
    # **Groeperen per locatie en energiestroom**
    df_locatie_benchmark = df_locatie_benchmark.groupby(["Location"])["Verbruik totaal"].sum().reset_index()

    # **Oppervlakte toevoegen en missing values correct afhandelen**
    df_locatie_benchmark["Oppervlakte (m²)"] = df_locatie_benchmark["Location"].map(oppervlakte_m2)

    # **Controleer of alle locaties een bekende oppervlakte hebben**
    if df_locatie_benchmark["Oppervlakte (m²)"].isnull().any():
        st.warning("Sommige locaties missen oppervlaktegegevens, waardoor 'Verbruik per m²' niet berekend kan worden.")

    # **Bereken verbruik per m², maar alleen als oppervlakte bekend is**
    df_locatie_benchmark["Verbruik per m²"] = df_locatie_benchmark.apply(
        lambda row: row["Verbruik totaal"] / row["Oppervlakte (m²)"] if row["Oppervlakte (m²)"] else None, axis=1
    ).round(2)

    # **Kolomtitel instellen op basis van energiestroom**
    eenheid = "kWh/m²" if energie_selectie == "Elektriciteit" else "m³/m²"
    kolom_te_tonen = f"Verbruik per m² ({eenheid})"

    # **Hernoem de kolom voor consistentie**
    df_locatie_benchmark.rename(columns={"Verbruik per m²": kolom_te_tonen}, inplace=True)

    # **Controleer of er bruikbare data is na filtering**
    if df_locatie_benchmark[kolom_te_tonen].notnull().sum() == 0:
        st.warning("⚠️ Geen bruikbare verbruik per m² data beschikbaar.")
    else:
        # **Barplot van verbruik per m²**
        fig = px.bar(
            df_locatie_benchmark.dropna(subset=[kolom_te_tonen]),  # Verwijder locaties zonder oppervlakte
            x="Location",
            y=kolom_te_tonen,
            title=f"Verbruik per m² voor {energie_selectie}",
            labels={"Location": "Locatie", kolom_te_tonen: f"Verbruik ({eenheid})"},
            color="Location",
            barmode="group",
            width=600,
        )

        # **Grafiek Layout Updaten**
        fig.update_layout(
            xaxis_title="",
            yaxis_title=f"Verbruik per m²",
            showlegend=False,
        )

        # **Toon de grafiek**
        st.plotly_chart(fig, use_container_width=True)
st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)











