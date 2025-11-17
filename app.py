import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
    "Nombre": ["Hospital Clínico UC", "CESFAM PA", "Hospital Regional", "Clínica BioBio", "CESFAM Viña Centro"],
    "Tipo": ["Hospital", "CESFAM", "Hospital", "Clínica", "CESFAM"]
})

# -------------------------------------------------------
# Barra lateral – escoger origen de datos
# -------------------------------------------------------
st.sidebar.header("⚙️ Configuración de datos")

usar_ejemplo = st.sidebar.checkbox("Usar dataset de ejemplo (recomendado)", value=True)

archivo = None
if not usar_ejemplo:
    archivo = st.sidebar.file_uploader("📂 Sube tu archivo CSV", type=["csv"])

# -------------------------------------------------------
# Cargar datos según selección
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
# Verificar columnas mínimas
# -------------------------------------------------------
columnas_requeridas = {"Region", "Comuna", "Nombre", "Tipo"}
if not columnas_requeridas.issubset(df.columns):
    st.error(f"El CSV debe contener las columnas: {', '.join(columnas_requeridas)}")
    st.stop()

# Limpieza
df = df.dropna(subset=["Region", "Comuna", "Nombre", "Tipo"])
for col in ["Region", "Comuna", "Nombre", "Tipo"]:
    df[col] = df[col].astype(str).str.strip()

# -------------------------------------------------------
# Filtros
# -------------------------------------------------------
st.sidebar.header("🔍 Filtros de búsqueda")

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
tipo_seleccionado = st.sidebar.multiselect("Tipo establecimiento:", options=tipos, default=tipos)

df_filtrado = df_filtrado[df_filtrado["Tipo"].isin(tipo_seleccionado)]

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
else:
    st.success(f"Se encontraron **{len(df_filtrado)} establecimientos**.")

# -------------------------------------------------------
# Gráficos
# -------------------------------------------------------
st.subheader("📊 Análisis gráfico")

# Distribución por región
fig, ax = plt.subplots(figsize=(10, 6))
sns.countplot(data=df_filtrado, x="Region", ax=ax, palette="viridis")
ax.set_title("Distribución de establecimientos por región")
plt.xticks(rotation=45)
st.pyplot(fig)

# Distribución por tipo
fig, ax = plt.subplots(figsize=(10, 6))
sns.countplot(data=df_filtrado, x="Tipo", ax=ax, palette="Set2")
ax.set_title("Distribución por tipo de establecimiento")
plt.xticks(rotation=45)
st.pyplot(fig)

# Totales
with st.expander("📊 Totales por región y comuna"):
    total_reg = df_filtrado.groupby("Region")["Nombre"].count().reset_index()
    total_reg.columns = ["Región", "Total"]

    st.write("### Totales por región")
    st.dataframe(total_reg, use_container_width=True)

    total_com = df_filtrado.groupby(["Region", "Comuna"])["Nombre"].count().reset_index()
    total_com.columns = ["Región", "Comuna", "Total"]

    st.write("### Totales por comuna")
    st.dataframe(total_com, use_container_width=True)

# Listado detallado
st.markdown("### 🏥 Establecimientos encontrados")
for region, subdf in df_filtrado.groupby("Region"):
    st.markdown(f"## 🗺️ {region}")
    for comuna, subdf2 in subdf.groupby("Comuna"):
        st.markdown(f"**Comuna: {comuna}**")
        for _, fila in subdf2.iterrows():
            st.markdown(f"- {fila['Nombre']} ({fila['Tipo']})")
        st.markdown("---")

# Descargar CSV
st.download_button(
    label="💾 Descargar datos filtrados (CSV)",
    data=df_filtrado.to_csv(index=False).encode("utf-8"),
    file_name="establecimientos_filtrados.csv",
    mime="text/csv"
)
