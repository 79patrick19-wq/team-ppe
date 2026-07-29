import streamlit as st
import pandas as pd

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
    h1, h2, h3 { color: #00f0ff !important; text-shadow: 0 0 8px #00f0ff; }
</style>
""", unsafe_allow_html=True)

st.title("⚛️ J.A.R.V.I.S. — TEAM PPE")
st.caption("SYSTEM STATUS: ONLINE // VALENCIENNES [HDF]")

st.markdown("---")

# Métriques HUD
c1, c2 = st.columns(2)
c1.metric("GTI CRITIQUE", "1 INCIDENT", "-15 MIN", delta_color="inverse")
c2.metric("GTR GELÉE", "1 SITE", "PDP ATTENTE")

st.subheader("📡 INCIDENTS EN COURS")

st.markdown("""
<div class="hud-card hud-critical">
    <b style="color:#ff0055;">🔴 TCK-2026-809 — Cambrai</b> (GTI : 15 min)<br>
    <small>Signal Faible Optique | Technicien: Non assigné</small>
</div>
<div class="hud-card hud-warning">
    <b style="color:#ffaa00;">🟠 TCK-2026-804 — Douai</b> (GTR GELÉE)<br>
    <small>Défaut NRO | Technicien: Samir B. (Attente PDP)</small>
</div>
<div class="hud-card hud-ok">
    <b style="color:#00ff88;">🟢 TCK-2026-801 — Valenciennes</b> (GTR: 1h45)<br>
    <small>Coupure Fibre | Technicien: Christopher T.</small>
</div>
""", unsafe_allow_html=True)
