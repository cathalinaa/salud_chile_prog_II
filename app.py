import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------------
# Configuración general
# -------------------------------------------------------
st.set_page_config(page_title="Establecimientos de Salud en Chile", page_icon="🏥", layout="wide")

st.title("🏥 Establecimientos de Salud en Chile")
st.markdown("""
Sube tu archivo CSV o usa el dataset de ejemplo para visualizar establecimientos de salud en Chile.
Debe contener las columnas:
**Region**, **Comuna**, **Nombre**, **Tipo**.
""")

# -------------------------------------------------------
# Dataset de ejemplo (se carga automáticamente)
# -------------------------------------------------------
df_ejemplo = pd.DataFrame({
    "Region": ["Metropolitana", "Metropolitana", "Biobío", "Biobío", "Valparaíso"],
    "Comuna": ["Santiago", "Puente Alto", "Concepción", "Talcahuano", "Viña del Mar"],
    "Nombre": [
        "Hospital Clínico UC",
        "CESFAM Puente Alto",
        "Hospital Regional de Concepción",
        "Clínica BioBio",
        "CESFAM Viña Centro"
    ],
    "Tipo": ["Hospital", "CESFAM", "Hospital", "Clínica", "CESFAM"]
})

# -------------------------------------------------------
# Barra lateral: Selección de origen de datos
# -------------------------------------------------------
st.sidebar.header("⚙️ Configuración de datos")
usar_ejemplo = st.sidebar.checkbox("Usar dataset de ejemplo (recomendado)", value=True)

archivo = None
if not usar_ejemplo:
    archivo = st.sidebar.file_uploader("📂 Sube tu archivo CSV", type=["csv"])

# -------------------------------------------------------
# Cargar datos
# -------------------------------------------------------
if usar_ejemplo:
    df = df_ejemplo.copy()
else:
    if archivo is None:
        st.info("👈 Sube un archivo CSV o activa el dataset de ejemplo para comenzar.")
        st.stop()
    try:
        df = pd.read_csv(archivo)
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        st.stop()

# -------------------------------------------------------
# Verificar columnas
# -------------------------------------------------------
columnas_requeridas = {"Region", "Comuna", "Nombre", "Tipo"}
if not columnas_requeridas.issubset(df.columns):
    st.error(f"El CSV debe contener las columnas: {', '.join(columnas_requeridas)}")
    st.stop()

# Limpieza de datos
df = df.dropna(subset=["Region", "Comuna", "Nombre", "Tipo"])
for col in ["Region", "Comuna", "Nombre", "Tipo"]:
    df[col] = df[col].astype(str).str.strip()

# -------------------------------------------------------
# Filtros
# -------------------------------------------------------
st.sidebar.header("🔍 Filtros")

regiones = sorted(df["Region"].unique())
region_sel = st.sidebar.selectbox("Región:", ["Todas"] + regiones)

df_filtrado = df.copy()
if region_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Region"] == region_sel]

comunas = sorted(df_filtrado["Comuna"].unique())
comuna_sel = st.sidebar.selectbox("Comuna:", ["Todas"] + comunas)

if comuna_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Comuna"] == comuna_sel]

tipos = sorted(df["Tipo"].unique())
tipo_sel = st.sidebar.multiselect("Tipo establecimiento:", tipos, default=tipos)

df_filtrado = df_filtrado[df_filtrado["Tipo"].isin(tipo_sel)]

busqueda = st.sidebar.text_input("Buscar por nombre:")
if busqueda:
    df_filtrado = df_filtrado[df_filtrado["Nombre"].str.contains(busqueda, case=False)]

# -------------------------------------------------------
# Mostrar resultados
# -------------------------------------------------------
st.subheader("📋 Resultados filtrados")

if df_filtrado.empty:
    st.warning("No se encontraron establecimientos con los filtros seleccionados.")
    st.stop()

st.success(f"Se encontraron **{len(df_filtrado)} establecimientos**.")

# -------------------------------------------------------
# Gráficos con Matplotlib
# -------------------------------------------------------
st.subheader("📊 Análisis gráfico")

# ---- Gráfico por región ----
fig, ax = plt.subplots(figsize=(10, 5))
df_filtrado["Region"].value_counts().plot(kind="bar", ax=ax)
ax.set_title("Distribución de establecimientos por región")
ax.set_xlabel("Región")
ax.set_ylabel("Cantidad")
plt.xticks(rotation=45)
st.pyplot(fig)

# ---- Gráfico por tipo ----
fig, ax = plt.subplots(figsize=(10, 5))
df_filtrado["Tipo"].value_counts().plot(kind="bar", ax=ax)
ax.set_title("Distribución de establecimientos por tipo")
ax.set_xlabel("Tipo")
ax.set_ylabel("Cantidad")
plt.xticks(rotation=45)
st.pyplot(fig)

# -------------------------------------------------------
# Totales
# -------------------------------------------------------
with st.expander("📊 Totales por región y comuna"):
    total_region = df_filtrado.groupby("Region")["Nombre"].count().reset_index()
    total_region.columns = ["Región", "Total"]
    st.write("### Totales por región")
    st.dataframe(total_region, use_container_width=True)

    total_comuna = df_filtrado.groupby(["Region", "Comuna"])["Nombre"].count().reset_index()
    total_comuna.columns = ["Región", "Comuna", "Total"]
    st.write("### Totales por comuna")
    st.dataframe(total_comuna, use_container_width=True)

# -------------------------------------------------------
# Listado detallado
# -------------------------------------------------------
st.markdown("### 🏥 Establecimientos encontrados")

for region, df_region in df_filtrado.groupby("Region"):
    st.markdown(f"## 🗺️ {region}")
    for comuna, df_comuna in df_region.groupby("Comuna"):
        st.markdown(f"### 📍 Comuna: {comuna}")
        for _, fila in df_comuna.iterrows():
            st.markdown(f"- **{fila['Nombre']}** ({fila['Tipo']})")
        st.markdown("---")

# -------------------------------------------------------
# Descargar CSV
# -------------------------------------------------------
st.download_button(
    label="💾 Descargar datos filtrados (CSV)",
    data=df_filtrado.to_csv(index=False).encode("utf-8"),
    file_name="establecimientos_filtrados.csv",
    mime="text/csv"
)
