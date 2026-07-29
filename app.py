import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# Configuration de la page
st.set_page_config(page_title="J.A.R.V.I.S. — TEAM PPE", page_icon="⚛️", layout="wide")

DEFAULT_FILE = "a094b4cc-43f7-4802-83f3-080cfb7d3360.csv"

# Barre latérale - Options & Mode
with st.sidebar:
    st.header("⚙️ Configuration")
    theme_mode = st.radio("Thème d'affichage :", ["🌙 Mode Sombre (Sci-Fi)", "☀️ Mode Clair"], index=0)
    st.markdown("---")
    st.header("📂 Import Données")
    uploaded_file = st.file_uploader("Importer un extract CSV", type=["csv"])

# Application du Style selon le mode choisi
if "Sombre" in theme_mode:
    st.markdown("""
    <style>
        .stApp {
            background-color: #030a16;
            color: #00f0ff;
        }
        div[data-testid="stMetric"] {
            background: #08172e !important;
            border: 1px solid #00f0ff !important;
            border-radius: 8px;
            color: #00f0ff !important;
        }
        div[data-testid="stMetricValue"] { color: #00f0ff !important; }
        div[data-testid="stMetricLabel"] { color: #8ab4f8 !important; }
        .hud-card {
            background: #081b33;
            border-left: 5px solid #00f0ff;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 15px;
            color: #e0e0e0;
        }
        .hud-critical { border-left-color: #ff0055 !important; background: #260815 !important; }
        .hud-warning  { border-left-color: #ffaa00 !important; background: #261e08 !important; }
        .hud-ok       { border-left-color: #00ff88 !important; background: #082618 !important; }
        h1, h2, h3, h4, label { color: #00f0ff !important; }
        /* Style du tableau pour mode sombre */
        .stDataFrame { border: 1px solid #00f0ff; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .stApp {
            background-color: #f4f6f9;
            color: #1a1a1a;
        }
        div[data-testid="stMetric"] {
            background: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        div[data-testid="stMetricValue"] { color: #0f172a !important; }
        div[data-testid="stMetricLabel"] { color: #475569 !important; }
        .hud-card {
            background: #ffffff;
            border-left: 5px solid #0284c7;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 15px;
            color: #1e293b;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        .hud-critical { border-left-color: #dc2626 !important; background: #fef2f2 !important; }
        .hud-warning  { border-left-color: #d97706 !important; background: #fffbeb !important; }
        .hud-ok       { border-left-color: #16a34a !important; background: #f0fdf4 !important; }
        h1, h2, h3, h4, label { color: #0f172a !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚛️ J.A.R.V.I.S. — TEAM PPE")
st.caption("SYSTEM STATUS: ONLINE // PILOTAGE VALENCIENNES [HDF]")

@st.cache_data
def load_data(file_path_or_buffer):
    df = pd.read_csv(file_path_or_buffer, sep=";")
    if 'date_in_got' in df.columns:
        df['date_in_got_dt'] = pd.to_datetime(df['date_in_got'], errors='coerce')
    if 'prio' in df.columns:
        df = df.sort_values(by=['prio', 'date_in_got'], ascending=[True, False]).reset_index(drop=True)
    return df

df = None
if uploaded_file is not None:
    df = load_data(uploaded_file)
elif os.path.exists(DEFAULT_FILE):
    df = load_data(DEFAULT_FILE)

if df is not None:
    # Gestion de l'attribution des techniciens en Session State
    if "tech_assignments" not in st.session_state:
        st.session_state.tech_assignments = {}

    # Fusion des attributions dans le dataframe
    df['Technicien_Affecté'] = df.apply(
        lambda r: st.session_state.tech_assignments.get(r['numTicket'], r['Resp_Site_Mrs'] if pd.notna(r['Resp_Site_Mrs']) else "Non assigné"),
        axis=1
    )

    st.markdown("---")
    
    # KPIs principaux
    total_tickets = len(df)
    prio_haute = len(df[df['prio'] <= 2])
    gelados = len(df[df['Etat_Gel'].notna()])
    non_assignes = len(df[df['Technicien_Affecté'] == "Non assigné"])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("TOTAL TICKETS", f"{total_tickets}")
    col2.metric("PRIORITÉ URGENTE (P1/P2)", f"{prio_haute}", delta_color="inverse")
    col3.metric("DOSSIERS GELÉS", f"{gelados}")
    col4.metric("NON ASSIGNÉS", f"{non_assignes}", delta="À attribuer", delta_color="inverse")
    
    st.markdown("---")
    
    # Filtres interactifs avec Filtre Technicien
    st.subheader("🎛️ FILTRES ET RECHERCHE INTERACTIVE")
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    
    liste_techs = ["Tous", "Non assigné"] + sorted(list(set(df['Technicien_Affecté'].dropna().unique()) - {"Non assigné"}))
    
    with f_col1:
        service_filter = st.multiselect("Service Attribution", options=df['Service_Attribution'].dropna().unique())
    with f_col2:
        prio_filter = st.multiselect("Priorité (1 = Urgent)", options=sorted(df['prio'].unique()))
    with f_col3:
        tech_filter = st.selectbox("Filtrer par Technicien", options=liste_techs)
    with f_col4:
        gel_filter = st.radio("Affichage Gel", ["Tous", "Gelés", "Non gelés"], horizontal=True)

    # Application des filtres
    df_filtered = df.copy()
    if service_filter:
        df_filtered = df_filtered[df_filtered['Service_Attribution'].isin(service_filter)]
    if prio_filter:
        df_filtered = df_filtered[df_filtered['prio'].isin(prio_filter)]
    if tech_filter != "Tous":
        df_filtered = df_filtered[df_filtered['Technicien_Affecté'] == tech_filter]
    if gel_filter == "Gelés":
        df_filtered = df_filtered[df_filtered['Etat_Gel'].notna()]
    elif gel_filter == "Non gelés":
        df_filtered = df_filtered[df_filtered['Etat_Gel'].isna()]

    st.subheader(f"📡 LISTE DES INCIDENTS ({len(df_filtered)} / {total_tickets})")

    # Affichage du tableau nettoyé
    st.dataframe(
        df_filtered[['prio', 'numTicket', 'codeSite', 'nom_tvx_sin3', 'Service_Attribution', 'Technicien_Affecté', 'Etat_Gel', 'date_limite']],
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    
    # Section Action Technicien & Zoom Ticket
    st.subheader("🔍 ACTION & AFFECTATION TECHNICIEN")
    
    ticket_options = {row['numTicket']: f"P{row['prio']} - #{row['numTicket']} | {row['codeSite']} ({row['Technicien_Affecté']})" for _, row in df_filtered.iterrows()}
    
    if ticket_options:
        selected_id = st.selectbox(
            "Sélectionner un ticket à gérer :", 
            options=list(ticket_options.keys()), 
            format_func=lambda x: ticket_options[x]
        )
        
        if selected_id:
            t_data = df[df['numTicket'] == selected_id].iloc[0]
            css_class = "hud-critical" if t_data['prio'] <= 2 else ("hud-warning" if pd.notna(t_data['Etat_Gel']) else "hud-ok")
            
            st.markdown(f"""
            <div class="hud-card {css_class}">
                <h3>🔴 PRIORITÉ P{t_data['prio']} — TICKET N° {t_data['numTicket']} (Site: {t_data['codeSite']})</h3>
                <b>Travaux :</b> {t_data['nom_tvx_sin3']}<br>
                <b>Service Attribution :</b> {t_data['Service_Attribution']}<br>
                <b>Responsable TPS :</b> {t_data['Resp_Site_Tps'] if pd.notna(t_data['Resp_Site_Tps']) else 'N/C'}<br>
                <b>Technicien Actuel :</b> <b>{t_data['Technicien_Affecté']}</b><br>
                <b>Date Limite :</b> {t_data['date_limite']}<br>
                <b>État Gel :</b> {t_data['Etat_Gel'] if pd.notna(t_data['Etat_Gel']) else 'Aucun'} {f"({t_data['motif_Gel']})" if pd.notna(t_data['motif_Gel']) else ''}
            </div>
            """, unsafe_allow_html=True)

            # Formulaire de réaffectation de technicien
            with st.form(key=f"assign_form_{selected_id}"):
                st.write("👨‍🔧 **Réaffecter ce ticket à un technicien de l'équipe :**")
                nouveau_tech = st.selectbox(
                    "Choisir le technicien :",
                    ["Christopher T.", "Samir B.", "Gianni R.", "Bastien D.", "Julien F.", "Lahcen L.", "Non assigné"]
                )
                submit_assign = st.form_submit_button("✅ Valider l'affectation")
                
                if submit_assign:
                    st.session_state.tech_assignments[selected_id] = nouveau_tech
                    st.success(f"Ticket #{selected_id} réaffecté à {nouveau_tech} !")
                    st.rerun()

else:
    st.warning("Veuillez charger votre fichier CSV.")
