import streamlit as st
import pandas as pd
import os

# Configuration de la page
st.set_page_config(page_title="J.A.R.V.I.S. — TEAM PPE", page_icon="⚛️", layout="wide")

# Style HUD Sci-Fi / JARVIS
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at center, #051329 0%, #020b18 70%, #00050d 100%);
        color: #00f0ff;
        font-family: 'Segoe UI', Roboto, sans-serif;
    }
    div[data-testid="stMetric"] {
        background: rgba(0, 30, 60, 0.4);
        border: 1px solid #00f0ff;
        box-shadow: 0 0 12px rgba(0, 240, 255, 0.25);
        border-radius: 10px;
        padding: 10px;
    }
    .hud-card {
        background: rgba(2, 18, 38, 0.85);
        border-left: 4px solid #00f0ff;
        border-radius: 6px;
        padding: 14px;
        margin-bottom: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .hud-critical { border-left-color: #ff0055; box-shadow: 0 0 10px rgba(255,0,85,0.3); }
    .hud-warning  { border-left-color: #ffaa00; box-shadow: 0 0 10px rgba(255,170,0,0.3); }
    .hud-ok       { border-left-color: #00ff88; box-shadow: 0 0 10px rgba(0,255,136,0.3); }
    h1, h2, h3, h4 { color: #00f0ff !important; text-shadow: 0 0 8px #00f0ff; }
</style>
""", unsafe_allow_html=True)

DEFAULT_FILE = "a094b4cc-43f7-4802-83f3-080cfb7d3360.csv"

st.title("⚛️ J.A.R.V.I.S. — TEAM PPE")
st.caption("SYSTEM STATUS: ONLINE // PILOTAGE DES INTERVENTIONS")

# Option pour uploader un nouveau fichier ou utiliser le fichier extrait par défaut
with st.sidebar:
    st.header("📂 Data Source")
    uploaded_file = st.file_uploader("Importer un nouvel extract CSV", type=["csv"])

@st.cache_data
def load_data(file_path_or_buffer):
    df = pd.read_csv(file_path_or_buffer, sep=";")
    return df

df = None
if uploaded_file is not None:
    df = load_data(uploaded_file)
elif os.path.exists(DEFAULT_FILE):
    df = load_data(DEFAULT_FILE)

if df is not None:
    st.markdown("---")
    
    # Calcul des KPIs
    total_tickets = len(df)
    prio_haute = len(df[df['prio'] <= 2])
    gelados = len(df[df['Etat_Gel'].notna()])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("TOTAL TICKETS", f"{total_tickets} TICKETS")
    col2.metric("PRIORITÉ URGENTE (P1/P2)", f"{prio_haute} SITES", delta_color="inverse")
    col3.metric("DOSSIERS GELÉS", f"{gelados} DOSSIERS", "ACTION REQUIS")
    
    st.markdown("---")
    
    # Filtres interactifs
    st.subheader("🎛️ FILTRES ET RECHERCHE INTERACTIVE")
    f_col1, f_col2, f_col3 = st.columns(3)
    
    with f_col1:
        service_filter = st.multiselect("Service Attribution", options=df['Service_Attribution'].dropna().unique())
    with f_col2:
        prio_filter = st.multiselect("Priorité", options=sorted(df['prio'].unique()))
    with f_col3:
        gel_filter = st.radio("Affichage Gel", ["Tous", "Gelés uniquement", "Non gelés"], horizontal=True)

    # Application des filtres
    df_filtered = df.copy()
    if service_filter:
        df_filtered = df_filtered[df_filtered['Service_Attribution'].isin(service_filter)]
    if prio_filter:
        df_filtered = df_filtered[df_filtered['prio'].isin(prio_filter)]
    if gel_filter == "Gelés uniquement":
        df_filtered = df_filtered[df_filtered['Etat_Gel'].notna()]
    elif gel_filter == "Non gelés":
        df_filtered = df_filtered[df_filtered['Etat_Gel'].isna()]

    st.subheader(f"📡 LISTE DES INCIDENTS ({len(df_filtered)} / {total_tickets})")

    # Tableau dynamique avec sélection / consultation
    st.dataframe(
        df_filtered[['numTicket', 'codeSite', 'nom_tvx_sin3', 'prio', 'Service_Attribution', 'Resp_Site_Mrs', 'Etat_Gel', 'motif_Gel', 'date_limite']],
        use_container_width=True,
        hide_index=True
    )
    
    # Vue détaillée par carte HUD au choix
    st.markdown("### 🔍 ZOOM SUR UN TICKET")
    ticket_selected = st.selectbox("Sélectionner un ticket à inspecter :", df_filtered['numTicket'].unique())
    
    if ticket_selected:
        t_data = df[df['numTicket'] == ticket_selected].iloc[0]
        css_class = "hud-critical" if t_data['prio'] <= 2 else ("hud-warning" if pd.notna(t_data['Etat_Gel']) else "hud-ok")
        
        st.markdown(f"""
        <div class="hud-card {css_class}">
            <h4>🔴 TICKET N° {t_data['numTicket']} — Code Site: {t_data['codeSite']}</h4>
            <b>Travaux :</b> {t_data['nom_tvx_sin3']}<br>
            <b>Priorité :</b> P{t_data['prio']} | <b>Service :</b> {t_data['Service_Attribution']}<br>
            <b>Responsables :</b> {t_data['Resp_Site_Tps']} / {t_data['Resp_Site_Mrs']}<br>
            <b>Date Limite :</b> {t_data['date_limite']}<br>
            <b>État Gel :</b> {t_data['Etat_Gel'] if pd.notna(t_data['Etat_Gel']) else 'Aucun'} 
            {f"({t_data['motif_Gel']})" if pd.notna(t_data['motif_Gel']) else ''}
        </div>
        """, unsafe_allow_html=True)

else:
    st.warning("Veuillez uploader un fichier CSV ou vérifier que 'a094b4cc-43f7-4802-83f3-080cfb7d3360.csv' est présent sur GitHub.")
