import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import folium
from streamlit_folium import st_folium
import numpy as np

# -------------------------------------------------------
# Configuración general
# -------------------------------------------------------
st.set_page_config(
    page_title="Establecimientos de Salud en Chile",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Establecimientos de Salud en Chile")
st.markdown("""
Aplicación oficial conectada directamente a la API de datos.gob.cl
Incluye filtros avanzados, mapas, gráficos y análisis automáticos.
""")

# -------------------------------------------------------
# API oficial
# -------------------------------------------------------
API_URL = (
    "https://datos.gob.cl/api/3/action/datastore_search"
    "?resource_id=2c44d782-3365-44e3-aefb-2c8b8363a1bc"
    "&limit=5000"
)

with st.spinner("Cargando datos desde la API..."):
    response = requests.get(API_URL)
    data = response.json()
    records = data["result"]["records"]
    df = pd.DataFrame(records)

# -------------------------------------------------------
# Normalización de columnas
# -------------------------------------------------------
df = df.rename(columns={
    "RegionGlosa": "Region",
    "ComunaGlosa": "Comuna",
    "EstablecimientoGlosa": "Nombre",
    "TipoEstablecimientoGlosa": "Tipo",
    "Latitud": "Lat",
    "Longitud": "Lon",
    "TieneServicioUrgencia": "Urgencia",
    "TipoUrgencia": "UrgenciaTipo",
})

# Convertir coordenadas a float
df["Lat"] = pd.to_numeric(df["Lat"], errors="coerce")
df["Lon"] = pd.to_numeric(df["Lon"], errors="coerce")

df = df.dropna(subset=["Region", "Comuna", "Nombre", "Tipo"])

# -------------------------------------------------------
# SIDEBAR – FILTROS
# -------------------------------------------------------
st.sidebar.title("🔍 Filtros")

# Filtro región
regiones = sorted(df["Region"].unique())
region_sel = st.sidebar.selectbox("Región:", ["Todas"] + regiones)

df_filt = df.copy() if region_sel == "Todas" else df[df["Region"] == region_sel]

# Filtro comuna
comunas = sorted(df_filt["Comuna"].unique())
comuna_sel = st.sidebar.selectbox("Comuna:", ["Todas"] + comunas)

if comuna_sel != "Todas":
    df_filt = df_filt[df_filt["Comuna"] == comuna_sel]

# Filtro tipo
tipos = sorted(df["Tipo"].unique())
tipo_sel = st.sidebar.multiselect("Tipo de establecimiento:", tipos, default=tipos)

df_filt = df_filt[df_filt["Tipo"].isin(tipo_sel)]

# Filtro urgencia
urgencias_opciones = ["Todos", "Público", "Privado"]
urg_sel = st.sidebar.selectbox("Servicio de Urgencias:", urgencias_opciones)

if urg_sel == "Público":
    df_filt = df_filt[df_filt["UrgenciaTipo"].str.contains("Público", na=False)]
elif urg_sel == "Privado":
    df_filt = df_filt[df_filt["UrgenciaTipo"].str.contains("Privado", na=False)]

# -------------------------------------------------------
# RESULTADOS
# -------------------------------------------------------
st.subheader("📋 Resultados filtrados")

if df_filt.empty:
    st.warning("No se encontraron establecimientos.")
    st.stop()

st.success(f"Se encontraron **{len(df_filt)}** establecimientos.")

# -------------------------------------------------------
# MAPA
# -------------------------------------------------------
st.subheader("🗺️ Mapa de establecimientos")

df_map = df_filt.dropna(subset=["Lat", "Lon"])

if df_map.empty:
    st.warning("No hay coordenadas disponibles para este filtro.")
else:
    m = folium.Map(location=[-33.45, -70.65], zoom_start=5)

    for _, row in df_map.iterrows():
        folium.Marker(
            [row["Lat"], row["Lon"]],
            popup=f"{row['Nombre']}<br>{row['Tipo']}<br>{row['Comuna']}",
            tooltip=row["Nombre"]
        ).add_to(m)

    st_folium(m, height=480)

# -------------------------------------------------------
# GRÁFICOS
# -------------------------------------------------------
st.subheader("📊 Gráficos por tipo de establecimiento")

col1, col2 = st.columns(2)

# Hospitales
with col1:
    st.write("### Hospitales por región")
    hos = df_filt[df_filt["Tipo"].str.contains("Hospital", case=False)]
    fig, ax = plt.subplots()
    sns.countplot(data=hos, y="Region", order=hos["Region"].value_counts().index)
    st.pyplot(fig)

# Clínicas
with col2:
    st.write("### Clínicas por región")
    cli = df_filt[df_filt["Tipo"].str.contains("Clínica", case=False)]
    fig, ax = plt.subplots()
    sns.countplot(data=cli, y="Region", order=cli["Region"].value_counts().index)
    st.pyplot(fig)

# CESFAM
st.write("### CESFAM por región")
cesfam = df_filt[df_filt["Tipo"].str.contains("CESFAM", case=False)]
fig, ax = plt.subplots(figsize=(8,4))
sns.countplot(data=cesfam, y="Region", order=cesfam["Region"].value_counts().index)
st.pyplot(fig)

# General
st.write("### Total de establecimientos por región")
fig, ax = plt.subplots(figsize=(8,4))
sns.countplot(data=df_filt, y="Region", order=df_filt["Region"].value_counts().index)
st.pyplot(fig)

# -------------------------------------------------------
# 🔥 INTERACCIONES AVANZADAS
# -------------------------------------------------------
st.subheader("🤖 Interacciones avanzadas")

tab1, tab2, tab3, tab4 = st.tabs([
    "📍 Buscar establecimientos cercanos",
    "⏱ Urgencia 24 horas",
    "🥧 Distribución por tipo",
    "🏆 Ranking de comunas"
])

# 1 — Buscar cercanos
with tab1:
    lat_user = st.number_input("Tu latitud:", value=-33.45)
    lon_user = st.number_input("Tu longitud:", value=-70.65)
    radio_km = st.slider("Radio (km):", 1, 50, 10)

    def dist(lat1, lon1, lat2, lon2):
        return 6371 * np.arccos(
            np.cos(np.radians(lat1)) *
            np.cos(np.radians(lat2)) *
            np.cos(np.radians(lon2) - np.radians(lon1)) +
            np.sin(np.radians(lat1)) *
            np.sin(np.radians(lat2))
        )

    df_dist = df_map.copy()
    df_dist["Distancia"] = df_dist.apply(
        lambda r: dist(lat_user, lon_user, r["Lat"], r["Lon"]), axis=1)

    cerca = df_dist[df_dist["Distancia"] <= radio_km]
    st.write(cerca[["Nombre", "Tipo", "Comuna", "Distancia"]])

# 2 — Urgencia 24h
with tab2:
    urg24 = df_filt[df_filt["Urgencia"].str.contains("Sí", na=False)]
    st.write(f"Urgencias 24h encontradas: **{len(urg24)}**")
    st.dataframe(urg24)

# 3 — Pie chart
with tab3:
    fig, ax = plt.subplots()
    df_filt["Tipo"].value_counts().plot.pie(autopct="%1.1f%%")
    st.pyplot(fig)

# 4 — Ranking comunas
with tab4:
    ranking = df_filt["Comuna"].value_counts().head(10)
    st.write("### Comunas con más centros de salud")
    st.bar_chart(ranking)
