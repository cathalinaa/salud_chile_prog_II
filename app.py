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
Sube tu archivo CSV con los establecimientos de salud en Chile.
El archivo debe contener al menos las columnas:
**Region**, **Comuna**, **Nombre**, **Tipo** (por ejemplo: Hospital, Clínica, CESFAM).
""")

# -------------------------------------------------------
# Subir archivo CSV
# -------------------------------------------------------
archivo = st.file_uploader("📂 Sube tu archivo CSV", type=["csv"])

if archivo is not None:
    # Leer CSV
    try:
        df = pd.read_csv(archivo)
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        st.stop()

    # Verificar columnas mínimas
    columnas_requeridas = {"Region", "Comuna", "Nombre", "Tipo"}
    if not columnas_requeridas.issubset(df.columns):
        st.error(f"El CSV debe contener las columnas: {', '.join(columnas_requeridas)}")
        st.stop()

    # Limpiar datos básicos
    df = df.dropna(subset=["Region", "Comuna", "Nombre", "Tipo"])
    df["Region"] = df["Region"].astype(str).str.strip()
    df["Comuna"] = df["Comuna"].astype(str).str.strip()
    df["Nombre"] = df["Nombre"].astype(str).str.strip()
    df["Tipo"] = df["Tipo"].astype(str).str.strip()

    # -------------------------------------------------------
    # Filtros interactivos
    # -------------------------------------------------------
    st.sidebar.header("🔍 Filtros de búsqueda")

    # Filtro por región
    regiones = sorted(df["Region"].unique())
    region_seleccionada = st.sidebar.selectbox("Selecciona una región:", ["Todas"] + regiones)

    if region_seleccionada != "Todas":
        df_filtrado_region = df[df["Region"] == region_seleccionada]
    else:
        df_filtrado_region = df.copy()

    # Filtro por comuna
    comunas = sorted(df_filtrado_region["Comuna"].unique())
    comuna_seleccionada = st.sidebar.selectbox("Selecciona una comuna:", ["Todas"] + comunas)

    # Filtro por tipo de establecimiento
    tipos = sorted(df["Tipo"].unique())
    tipo_seleccionado = st.sidebar.multiselect(
        "Selecciona tipo de establecimiento:",
        options=tipos,
        default=tipos
    )

    # Búsqueda por nombre
    busqueda = st.sidebar.text_input("Buscar por nombre (opcional):")

    # -------------------------------------------------------
    # Aplicar filtros
    # -------------------------------------------------------
    df_filtrado = df_filtrado_region[df_filtrado_region["Tipo"].isin(tipo_seleccionado)]

    if comuna_seleccionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Comuna"] == comuna_seleccionada]

    if busqueda:
        df_filtrado = df_filtrado[df_filtrado["Nombre"].str.contains(busqueda, case=False, na=False)]

    # -------------------------------------------------------
    # Mostrar resultados
    # -------------------------------------------------------
    st.subheader("📋 Resultados filtrados")

    if df_filtrado.empty:
        st.warning("No se encontraron establecimientos con los filtros seleccionados.")
    else:
        st.success(f"Se encontraron **{len(df_filtrado)} establecimientos**.")

        # -------------------------------------------------------
        # Graficar distribución por región y tipo
        # -------------------------------------------------------
        st.subheader("📊 Análisis gráfico")

        # Gráfico de distribución por región
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.countplot(data=df_filtrado, x="Region", ax=ax, palette="viridis")
        ax.set_title("Distribución de establecimientos por región")
        ax.set_xlabel("Región")
        ax.set_ylabel("Cantidad de establecimientos")
        st.pyplot(fig)

        # Gráfico de distribución por tipo de establecimiento
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.countplot(data=df_filtrado, x="Tipo", ax=ax, palette="Set2")
        ax.set_title("Distribución de establecimientos por tipo")
        ax.set_xlabel("Tipo de establecimiento")
        ax.set_ylabel("Cantidad de establecimientos")
        st.pyplot(fig)

        # -------------------------------------------------------
        # Totales por región y comuna
        # -------------------------------------------------------
        with st.expander("📊 Totales por región y comuna"):
            total_region = df_filtrado.groupby("Region")["Nombre"].count().reset_index()
            total_region.columns = ["Región", "Total Establecimientos"]
            st.write("### Totales por región")
            st.dataframe(total_region, use_container_width=True)

            total_comuna = df_filtrado.groupby(["Region", "Comuna"])["Nombre"].count().reset_index()
            total_comuna.columns = ["Región", "Comuna", "Total Establecimientos"]
            st.write("### Totales por comuna")
            st.dataframe(total_comuna, use_container_width=True)

        # -------------------------------------------------------
        # Listado detallado de establecimientos
        # -------------------------------------------------------
        st.markdown("### 🏥 Establecimientos encontrados")
        for region, df_region in df_filtrado.groupby("Region"):
            st.markdown(f"## 🗺️ {region}")
            for comuna, df_comuna in df_region.groupby("Comuna"):
                st.markdown(f"**Comuna: {comuna}**")
                for _, fila in df_comuna.iterrows():
                    st.markdown(f"- {fila['Nombre']} ({fila['Tipo']})")
                st.markdown("---")

        # -------------------------------------------------------
        # Descargar datos filtrados
        # -------------------------------------------------------
        st.download_button(
            label="💾 Descargar datos filtrados (CSV)",
            data=df_filtrado.to_csv(index=False).encode("utf-8"),
            file_name="establecimientos_filtrados.csv",
            mime="text/csv"
        )
else:
    st.info("👆 Esperando que subas tu archivo CSV para comenzar.")
