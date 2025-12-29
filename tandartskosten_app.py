import streamlit as st
import pandas as pd

# Pagina configuratie
st.set_page_config(
    page_title="Tandartskosten Calculator",
    page_icon="🦷",
    layout="wide"
)

# Custom CSS voor mooie styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A5F;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #5A7A9A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
    }
    .savings-positive {
        color: #10B981;
        font-weight: bold;
    }
    .savings-negative {
        color: #EF4444;
        font-weight: bold;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🦷 Tandartskosten Calculator</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Bereken wat je bespaart met een aanvullende tandartsverzekering</p>', unsafe_allow_html=True)

# Definieer de verzekeringen
verzekeringen = [
    {"naam": "Geen dekking", "percentage": 0, "max": 0},
    {"naam": "75% tot €100", "percentage": 75, "max": 100},
    {"naam": "75% tot €250", "percentage": 75, "max": 250},
    {"naam": "75% tot €500", "percentage": 75, "max": 500},
    {"naam": "75% tot €750", "percentage": 75, "max": 750},
    {"naam": "75% tot €1000", "percentage": 75, "max": 1000},
    {"naam": "100% tot €100", "percentage": 100, "max": 100},
    {"naam": "100% tot €250", "percentage": 100, "max": 250},
    {"naam": "100% tot €500", "percentage": 100, "max": 500},
    {"naam": "100% tot €750", "percentage": 100, "max": 750},
    {"naam": "100% tot €1000", "percentage": 100, "max": 1000},
]

def bereken_eigen_bijdrage(kosten, percentage, max_vergoeding):
    """
    Berekent wat je zelf betaalt na verzekering.
    """
    if percentage == 0 or max_vergoeding == 0:
        return kosten
    
    kosten_binnen_limiet = min(kosten, max_vergoeding)
    kosten_boven_limiet = max(0, kosten - max_vergoeding)
    eigen_bijdrage_binnen = kosten_binnen_limiet * (1 - percentage / 100)
    eigen_bijdrage_boven = kosten_boven_limiet
    
    return eigen_bijdrage_binnen + eigen_bijdrage_boven

# Sidebar voor input
st.sidebar.header("⚙️ Instellingen")

# Kosten input
kosten = st.sidebar.slider(
    "💰 Verwachte tandartskosten per jaar",
    min_value=0,
    max_value=2000,
    value=500,
    step=50,
    format="€%d"
)

# Of handmatig invoeren
kosten_handmatig = st.sidebar.number_input(
    "Of voer exact bedrag in:",
    min_value=0,
    max_value=10000,
    value=kosten,
    step=10
)

# Gebruik handmatig als het anders is dan de slider
if kosten_handmatig != kosten:
    kosten = kosten_handmatig

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Hoe werkt het?")
st.sidebar.markdown("""
1. Stel je verwachte tandartskosten in
2. Bekijk hoeveel je betaalt per verzekering
3. Vergelijk en kies de beste optie
""")

# Hoofdcontent
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown(f"### 📊 Resultaten voor €{kosten:,} aan tandartskosten")

# Bereken voor alle verzekeringen
resultaten = []
for verz in verzekeringen:
    eigen_bijdrage = bereken_eigen_bijdrage(kosten, verz['percentage'], verz['max'])
    besparing = kosten - eigen_bijdrage
    resultaten.append({
        "Verzekering": verz['naam'],
        "Dekking %": f"{verz['percentage']}%",
        "Max dekking": f"€{verz['max']}" if verz['max'] > 0 else "-",
        "Je betaalt zelf": f"€{eigen_bijdrage:,.0f}",
        "Besparing": f"€{besparing:,.0f}",
        "eigen_bijdrage_raw": eigen_bijdrage,
        "besparing_raw": besparing
    })

df = pd.DataFrame(resultaten)

# Highlight de beste optie (laagste eigen bijdrage, exclusief geen dekking)
beste_idx = df[df["Verzekering"] != "Geen dekking"]["eigen_bijdrage_raw"].idxmin()

# Metrics bovenaan
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="💸 Zonder verzekering",
        value=f"€{kosten:,}",
        delta=None
    )

with col2:
    beste_verz = df.loc[beste_idx]
    st.metric(
        label="🏆 Beste optie",
        value=beste_verz["Verzekering"],
        delta=None
    )

with col3:
    st.metric(
        label="💰 Je betaalt dan",
        value=beste_verz["Je betaalt zelf"],
        delta=f"-€{beste_verz['besparing_raw']:,.0f}",
        delta_color="inverse"
    )

with col4:
    st.metric(
        label="✨ Maximale besparing",
        value=f"€{beste_verz['besparing_raw']:,.0f}",
        delta=None
    )

st.markdown("---")

# Tabel met alle resultaten
st.markdown("### 📋 Overzicht alle verzekeringen")

# Maak een mooie weergave DataFrame
display_df = df[["Verzekering", "Dekking %", "Max dekking", "Je betaalt zelf", "Besparing"]].copy()

# Styling functie voor de tabel
def highlight_beste(row):
    if row.name == beste_idx:
        return ['background-color: #D1FAE5; font-weight: bold'] * len(row)
    return [''] * len(row)

styled_df = display_df.style.apply(highlight_beste, axis=1)

st.dataframe(
    styled_df,
    use_container_width=True,
    hide_index=True
)

st.caption("💚 Groen gemarkeerd = beste optie voor jouw situatie")

# Grafiek
st.markdown("---")
st.markdown("### 📈 Visuele vergelijking")

chart_data = df[["Verzekering", "eigen_bijdrage_raw"]].copy()
chart_data.columns = ["Verzekering", "Eigen bijdrage (€)"]
chart_data = chart_data.set_index("Verzekering")

st.bar_chart(chart_data, color="#667eea")

# Extra uitleg
with st.expander("ℹ️ Hoe wordt dit berekend?"):
    st.markdown("""
    ### Berekeningslogica
    
    **Voorbeeld:** Je hebt een verzekering "75% tot €500" en je tandartskosten zijn €700:
    
    1. **Tot €500:** De verzekering vergoedt 75%, dus je betaalt 25% = €125
    2. **Boven €500:** De overige €200 betaal je volledig zelf
    3. **Totaal eigen bijdrage:** €125 + €200 = €325
    
    ### Let op!
    - Dit is een vereenvoudigde berekening
    - De daadwerkelijke premiekosten van de verzekering zijn niet meegenomen
    - Neem altijd contact op met je verzekeraar voor exacte voorwaarden
    """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888;'>Gemaakt met ❤️ in Cursor | "
    "Dit is een hulpmiddel - raadpleeg altijd je verzekeraar voor definitieve informatie</p>",
    unsafe_allow_html=True
)

