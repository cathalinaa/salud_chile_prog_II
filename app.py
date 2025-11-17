import streamlit as st
import pandas as pd

# -------------------------------------------------------
# Configuración general
# -------------------------------------------------------
st.set_page_config(page_title="Establecimientos de Salud en Chile", page_icon="🏥", layout="wide")

st.title("🏥 Establecimientos de Salud en Chile")
st.markdown("""
Este sitio carga automáticamente el CSV oficial desde **datos.gob.cl**
correspondiente a los establecimientos de salud vigentes en Chile.
""")

# URL del CSV oficial
URL = "https://datos.gob.cl/dataset/2c44d782-3365-44e3-aefb-2c8b8363a1bc/resource/2c44d782-3365-44e3-aefb-2c8b8363a1bc/download/establecimientos_de_salud_vigentes.csv"

st.info("📥 Descargando datos desde datos.gob.cl...")

# -------------------------------------------------------
# Descarga del CSV oficial
# -------------------------------------------------------
try:
    df = pd.read_csv(URL, encoding="latin1")
except Exception as e:
    st.error(f"Error al descargar los datos: {e}")
    st.stop()

# Renombrar columnas importantes si no coinciden
df.columns = df.columns.str.strip()

# Intentar detectar columnas equivalentes
columnas_equivalentes = {
    "region": "Region",
    "nombre_region": "Region",
    "comuna": "Comuna",
    "nombre_comuna": "Comuna",
    "nombre": "Nombre",
    "razon_social": "Nombre",
    "tipo": "Tipo",
    "tipo_establecimiento": "Tipo"
}

for col_original, col_nueva in columnas_equivalentes.items():
    if col_original in df.columns and col_nueva not in df.columns:
        df[col_nueva] = df[col_original]

columnas_requeridas = ["Region", "Comuna", "Nombre", "Tipo"]

if not set(columnas_requeridas).issubset(df.columns):
    st.error("⚠️ El dataset oficial no contiene las columnas mínimas requeridas.")
    st.write("Columnas encontradas:", list(df.columns))
    st.stop()

# -------------------------------------------------------
# Limpieza básica
# -------------------------------------------------------
df = df.dropna(subset=["Region", "Comuna", "Nombre", "Tipo"])
df["Region"] = df["Region"].astype(str).str.strip()
df["Comuna"] = df["Comuna"].astype(str).str.strip()
df["Nombre"] = df["Nombre"].astype(str).str.strip()
df["Tipo"] = df["Tipo"].astype(str).str.strip()

# -------------------------------------------------------
# Filtros en la barra lateral
# -------------------------------------------------------
st.sidebar.header("🔍 Filtros")

regiones = sorted(df["Region"].unique())
region_seleccionada = st.sidebar.selectbox("Selecciona una región:", ["Todas"] + regiones)

df_filtrado = df.copy()
if region_seleccionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Region"] == region_seleccionada]

comunas = sorted(df_filtrado["Comuna"].unique())
comuna_seleccionada = st.sidebar.selectbox("Selecciona una comuna:", ["Todas"] + comunas)

if comuna_seleccionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Comuna"] == comuna_seleccionada]

tipos = sorted(df["Tipo"].unique())
tipo_seleccionado = st.sidebar.multiselect(
    "Selecciona tipo de establecimiento:",
    options=tipos,
    default=tipos
)
df_filtrado = df_filtrado[df_filtrado["Tipo"].isin(tipo_seleccionado)]

busqueda = st.sidebar.text_input("Buscar por nombre:")

if busqueda:
    df_filtrado = df_filtrado[df]()

