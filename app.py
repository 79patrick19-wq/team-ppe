import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

# Configuration de la page
st.set_page_config(page_title="PILOTAGE TEAM PPE", page_icon="📊", layout="wide")

DEFAULT_FILE = "a094b4cc-43f7-4802-83f3-080cfb7d3360.csv"

# Barre latérale - Options & Mode
with st.sidebar:
    st.header("⚙️ Configuration")
    theme_mode = st.radio("Thème d'affichage :", ["🌙 Mode Sombre", "☀️ Mode Clair"], index=0)
    st.markdown("---")
    st.header("📂 Import Données")
    uploaded_file = st.file_uploader("Importer un extract CSV", type=["csv"])

# Style dynamique selon le mode choisi avec lisibilité corrigée
if "Sombre" in theme_mode:
    st.markdown("""
    <style>
        .stApp { background-color: #0d1117; color: #f0f6fc !important; }
        div[data-testid="stMetric"] { background: #161b22 !important; border: 1px solid #30363d !important; border-radius: 8px; }
        div[data-testid="stMetricValue"] { color: #58a6ff !important; }
        div[data-testid="stMetricLabel"] { color: #8b949e !important; }
        .hud-card { background: #161b22; border-left: 5px solid #58a6ff; border-radius: 8px; padding: 16px; margin-bottom: 15px; color: #f0f6fc; }
        .hud-critical { border-left-color: #f85149 !important; background: #271012 !important; }
        .hud-warning  { border-left-color: #d29922 !important; background: #261e08 !important; }
        .hud-ok       { border-left-color: #3fb950 !important; background: #0d2818 !important; }
        h1, h2, h3, h4, label { color: #58a6ff !important; }
        
        /* Correction texte des puces radio et sélecteurs */
        div[role="radiogroup"] label, div[role="radiogroup"] label span { color: #f0f6fc !important; font-weight: 500; }
        .stRadio label div[data-testid="stMarkdownContainer"] p { color: #58a6ff !important; font-size: 15px; }
        div[data-baseweb="select"] span { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .stApp { background-color: #f4f6f9; color: #1a1a1a; }
        div[data-testid="stMetric"] { background: #ffffff !important; border: 1px solid #cbd5e1 !important; border-radius: 8px; }
        div[data-testid="stMetricValue"] { color: #0f172a !important; }
        div[data-testid="stMetricLabel"] { color: #475569 !important; }
        .hud-card { background: #ffffff; border-left: 5px solid #0284c7; border-radius: 8px; padding: 16px; margin-bottom: 15px; color: #1e293b; }
        .hud-critical { border-left-color: #dc2626 !important; background: #fef2f2 !important; }
        .hud-warning  { border-left-color: #d97706 !important; background: #fffbeb !important; }
        .hud-ok       { border-left-color: #16a34a !important; background: #f0fdf4 !important; }
        h1, h2, h3, h4, label { color: #0f172a !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 PILOTAGE ACTIVITÉ — TEAM PPE")
st.caption("TABLEAU DE BORD DE SUIVI DES INCIDENTS ET INTERVENTIONS")

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
    # Session States
    if "tech_assignments" not in st.session_state:
        st.session_state.tech_assignments = {}

    # Affectation dynamique
    df['Technicien_Affecté'] = df.apply(
        lambda r: st.session_state.tech_assignments.get(r['numTicket'], r['Resp_Site_Mrs'] if pd.notna(r['Resp_Site_Mrs']) else "Non assigné"),
        axis=1
    )

    st.markdown("---")

    # 🎙️ MODULE COMMANDES VOCALES
    st.subheader("🎙️ COMMANDE VOCALE")
    
    components.html("""
        <div style="font-family: sans-serif; text-align: center; background: transparent;">
            <button id="mic_btn" onclick="startDictation()" style="
                background: linear-gradient(135deg, #0284c7, #0369a1);
                color: white;
                font-weight: bold;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                font-size: 15px;
            ">
                🎤 DICTER UNE RECHERCHE
            </button>
            <p id="status" style="color: #38bdf8; margin-top: 8px; font-size: 14px;"></p>
        </div>

        <script>
            function startDictation() {
                if (window.hasOwnProperty('webkitSpeechRecognition') || window.hasOwnProperty('SpeechRecognition')) {
                    var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                    recognition.lang = "fr-FR";
                    recognition.continuous = false;
                    recognition.interimResults = false;

                    document.getElementById('status').innerText = "🎙️ Écoute en cours... Parlez maintenant !";

                    recognition.onresult = function(e) {
                        var resultText = e.results[0][0].transcript;
                        document.getElementById('status').innerText = "✅ Reconnu : " + resultText;
                        navigator.clipboard.writeText(resultText);
                        alert("Recherche vocale capturée : '" + resultText + "' ! Collez-la (Ctrl+V) dans la barre de recherche ci-dessous.");
                    };

                    recognition.onerror = function(e) {
                        document.getElementById('status').innerText = "⚠️ Erreur micro : " + e.error;
                    };

                    recognition.start();
                } else {
                    alert("Reconnaissance vocale non supportée sur ce navigateur. Utilisez Chrome ou Safari.");
                }
            }
        </script>
    """, height=90)

    # Barre de recherche textuelle / vocale
    search_query = st.text_input("🔍 Recherche rapide (N° Ticket, Site, Mot-clé ou Technicien) :", value="", placeholder="Ex: Valenciennes, P1, Christopher, 15549636...")

    # KPIs
    total_tickets = len(df)
    prio_haute = len(df[df['prio'] <= 2])
    gelados = len(df[df['Etat_Gel'].notna()])
    non_assignes = len(df[df['Technicien_Affecté'] == "Non assigné"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("TOTAL TICKETS", f"{total_tickets}")
    col2.metric("PRIORITÉ URGENTE (P1/P2)", f"{prio_haute}", delta_color="inverse")
    col3.metric("DOSSIERS GELÉS", f"{gelados}")
    col4.metric("NON ASSIGNÉS", f"{non_assignes}", delta_color="inverse")

    st.markdown("---")

    # Filtres interactifs
    st.subheader("🎛️ FILTRES INTERACTIFS")
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)

    liste_techs = ["Tous", "Non assigné"] + sorted(list(set(df['Technicien_Affecté'].dropna().unique()) - {"Non assigné"}))

    with f_col1:
        service_filter = st.multiselect("Service Attribution", options=df['Service_Attribution'].dropna().unique())
    with f_col2:
        prio_filter = st.multiselect("Priorité", options=sorted(df['prio'].unique()))
    with f_col3:
        tech_filter = st.selectbox("Filtrer par Technicien", options=liste_techs)
    with f_col4:
        gel_filter = st.radio("Affichage Gel", ["Tous", "Gelés", "Non gelés"], horizontal=True)

    # Application des filtres
    df_filtered = df.copy()

    if search_query:
        df_filtered = df_filtered[
            df_filtered['numTicket'].astype(str).str.contains(search_query, case=False, na=False) |
            df_filtered['codeSite'].astype(str).str.contains(search_query, case=False, na=False) |
            df_filtered['nom_tvx_sin3'].astype(str).str.contains(search_query, case=False, na=False) |
            df_filtered['Technicien_Affecté'].astype(str).str.contains(search_query, case=False, na=False)
        ]

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

    st.subheader(f"📋 LISTE DES INCIDENTS ({len(df_filtered)} / {total_tickets})")

    st.dataframe(
        df_filtered[['prio', 'numTicket', 'codeSite', 'nom_tvx_sin3', 'Service_Attribution', 'Technicien_Affecté', 'Etat_Gel', 'date_limite']],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # Section Réaffectation Technicien
    st.subheader("🛠️ GESTION & AFFECTATION DES TICKETS")

    ticket_options = {row['numTicket']: f"P{row['prio']} - #{row['numTicket']} | {row['codeSite']} ({row['Technicien_Affecté']})" for _, row in df_filtered.iterrows()}

    if ticket_options:
        selected_id = st.selectbox(
            "Sélectionner un ticket à attribuer :", 
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
                <b>Technicien Actuel :</b> <b>{t_data['Technicien_Affecté']}</b><br>
                <b>Date Limite :</b> {t_data['date_limite']}<br>
                <b>État Gel :</b> {t_data['Etat_Gel'] if pd.notna(t_data['Etat_Gel']) else 'Aucun'}
            </div>
            """, unsafe_allow_html=True)

            with st.form(key=f"assign_form_{selected_id}"):
                st.write("👨‍🔧 **Changer l'affectation du technicien :**")
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
