import streamlit as st
from datetime import datetime, date
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
import json
import tempfile

# --- Autenticación Google Sheets desde secrets o archivo local ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

if "gcp_service_account" in st.secrets:
    sa_dict = {key: st.secrets["gcp_service_account"][key] for key in st.secrets["gcp_service_account"]}
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        json.dump(sa_dict, tmp)
        cred_file = tmp.name
else:
    cred_file = "credenciales.json"

creds = ServiceAccountCredentials.from_json_keyfile_name(cred_file, scope)
client = gspread.authorize(creds)

# --- Leer la hoja ---
sheet = client.open("Midtown Spain Set Up Form").sheet1
data = sheet.get_all_values()

# --- Extraer los datos relevantes ---
last_updated = data[2][8]  # Celda I3
total_received = data[5][7]  # Celda H6
total_goal = data[5][8]      # Celda I6
still_need = data[5][9]      # Celda J6
individual_surplus = data[5][10]  # Celda K6

# --- Cálculo de días restantes ---
fecha_tope = date(2025, 7, 24)
dias_restantes = (fecha_tope - date.today()).days

# --- Diseño Streamlit ---
st.set_page_config(page_title="Recaudación Viaje España", layout="centered")

st.title("🌍 Recaudación - Misión a España 🇪🇸")
st.subheader(f"🕒 Días restantes: **{dias_restantes}**")
st.markdown(f"📅 Última actualización: **{last_updated}**")

col1, col2 = st.columns(2)
with col1:
    st.metric("💰 Total Recibido", total_received)
    st.metric("🎯 Meta Total", total_goal)
with col2:
    st.metric("❗ Faltante", still_need)
    st.metric("📈 Superávit Individual", individual_surplus)

# --- Gráfico de Progreso ---
recibido = float(total_received.replace("$", "").replace(",", ""))
meta = float(total_goal.replace("$", "").replace(",", ""))
faltante = meta - recibido

fig, ax = plt.subplots()
ax.barh(["Meta"], [meta], color="lightgray", label="Meta")
ax.barh(["Meta"], [recibido], color="green", label="Recibido")
ax.set_xlim(0, meta)
ax.set_xlabel("USD")
ax.set_title("Progreso de Recaudación")
for i, v in enumerate([recibido]):
    ax.text(v + meta * 0.01, i, f"${v:,.0f}", va='center')
st.pyplot(fig)

st.markdown("---")
st.markdown("✅ La página se actualiza automáticamente cada vez que se abre.")
