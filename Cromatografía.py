# Cromatografía.py – App para Olimpiada de Bioquímica

import streamlit as st
import pandas as pd

# --- Título de la app ---
st.set_page_config(page_title="Olimpiada de Bioquímica – Purificación de Proteínas")
st.title("🏆 Olimpiada de Bioquímica – Estrategia de Purificación de Proteínas")

# --- Enlace base para exportar como CSV desde Google Sheets ---
url_hoja = "https://docs.google.com/spreadsheets/d/1Rqk1GZ3Y5KKNT5VjTXI-pbFhlVZ-c-XcCCjmXAM6DiQ/export?format=csv&gid="

# Diccionario de pestañas (hojas) y sus IDs (gid)
sheets = {
    "Ejercicio": "0"
}

# Función para cargar una hoja de Google Sheets con manejo de errores
def cargar_hoja(nombre, gid):
    try:
        enlace = url_hoja + gid
        df = pd.read_csv(enlace)
        st.success(f"✅ Hoja '{nombre}' cargada correctamente desde Google Sheets.")
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar la hoja '{nombre}': {e}")
        return pd.DataFrame()

# Función para cargar un CSV desde GitHub
@st.cache_data
def cargar_csv_desde_github(url_raw, nombre, header='infer', names=None):
    try:
        df = pd.read_csv(url_raw, header=header, names=names)
        st.success(f"✅ Hoja '{nombre}' cargada correctamente desde GitHub.")
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar la hoja '{nombre}': {e}")
        return pd.DataFrame()

# --- Cargar hoja 'Ejercicio' desde Google Sheets ---
df_ejercicio = cargar_hoja("Ejercicio", sheets["Ejercicio"])

# --- Cargar hojas 'Purificación' y 'Datos' desde CSV en GitHub ---
url_purificacion = "https://raw.githubusercontent.com/kakuro83/BQ/07db0129a42190db7c548d2be1e7939e24e06833/Purificaci%C3%B3n.csv"
url_datos = "https://raw.githubusercontent.com/kakuro83/BQ/07db0129a42190db7c548d2be1e7939e24e06833/Datos.csv"
url_estudiantes = "https://raw.githubusercontent.com/kakuro83/BQ/main/Estudiantes.txt"

df_purificacion = cargar_csv_desde_github(url_purificacion, "Purificación")
df_datos = cargar_csv_desde_github(url_datos, "Datos")
df_estudiantes = cargar_csv_desde_github(url_estudiantes, "Estudiantes", header=None, names=["Estudiante"])

# --- Mostrar Datos Fijos y Columnas de Purificación ---
if not df_datos.empty:
    st.subheader("📊 Datos Fijos")
    st.dataframe(df_datos)

if not df_purificacion.empty:
    st.subheader("🧬 Información de las Columnas de Purificación")
    st.dataframe(df_purificacion)

# --- Selección de estudiante ---
if not df_estudiantes.empty:
    st.subheader("👤 Selección de Estudiante")
    lista_estudiantes = df_estudiantes["Estudiante"].dropna().tolist()
    estudiante = st.selectbox("Seleccione su nombre:", lista_estudiantes)

# --- Selección de proteína objetivo ---
if not df_ejercicio.empty:
    st.subheader("🧪 Selección de Proteína Objetivo")
    lista_proteinas = ["Seleccionar proteína"] + df_ejercicio["Nombre"].dropna().tolist()
    seleccion = st.selectbox("Seleccione una proteína para visualizar sus propiedades:", lista_proteinas)

    if seleccion != "Seleccionar proteína":
        df_proteina = df_ejercicio[df_ejercicio["Nombre"] == seleccion].copy()

        # Mostrar propiedades generales excluyendo columnas Banda A–E
        columnas_bandas = [col for col in df_proteina.columns if col.startswith("Banda")]
        df_info = df_proteina.drop(columns=columnas_bandas).T
        df_info.columns = ["Valor"]
        st.markdown("### 🔬 Propiedades Generales de la Proteína")
        st.dataframe(df_info)

        # Procesar y mostrar datos de bandas SDS-PAGE
        st.markdown("### 🧫 Análisis SDS-PAGE (Bandas Detectadas)")
        bandas = []
        for col in columnas_bandas:
            datos = df_proteina.iloc[0][col]
            if pd.notna(datos):
                valores = datos.split(";")
                if len(valores) == 4:
                    bandas.append({
                        "Banda": col.split()[-1],
                        "Recorrido": valores[0],
                        "Abundancia (%)": valores[1],
                        "Carga neta": valores[2],
                        "Propiedad estructural": valores[3]
                    })

        if bandas:
            df_bandas = pd.DataFrame(bandas)
            st.dataframe(df_bandas)

        # --- Estrategia de purificación ---
        st.subheader("⚗️ Estrategia de Purificación")
        tecnicas = df_purificacion["Técnica"].dropna().unique().tolist()
        etapas = []

        for i in range(1, 5):
            st.markdown(f"**Etapa {i}**")
            col1, col2, col3 = st.columns(3)
            with col1:
                tecnica = st.selectbox(f"Técnica {i}", ["Seleccionar"] + tecnicas, key=f"tecnica_{i}")
            with col2:
                corridas = st.number_input(f"Corridas {i}", min_value=1, step=1, key=f"corridas_{i}")
            with col3:
                velocidad = st.number_input(f"Velocidad (mg/min) {i}", min_value=0.1, step=0.1, key=f"velocidad_{i}")
            etapas.append({"Etapa": i, "Técnica": tecnica, "Corridas": corridas, "Velocidad": velocidad})

st.info("Esta es la vista base de los datos. A partir de aquí construiremos la lógica para diseñar la estrategia de purificación.")
