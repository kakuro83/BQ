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
def cargar_csv_desde_github(url_raw, nombre):
    try:
        df = pd.read_csv(url_raw)
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

df_purificacion = cargar_csv_desde_github(url_purificacion, "Purificación")
df_datos = cargar_csv_desde_github(url_datos, "Datos")

# --- Mostrar vista previa si se cargaron correctamente ---
if not df_ejercicio.empty:
    st.subheader("🧪 Proteína Objetivo y Condiciones Iniciales")
    st.dataframe(df_ejercicio)

if not df_purificacion.empty:
    st.subheader("🧬 Columnas de Purificación Disponibles")
    st.dataframe(df_purificacion)

if not df_datos.empty:
    st.subheader("📊 Parámetros Globales del Sistema")
    st.dataframe(df_datos)

st.info("Esta es la vista base de los datos. A partir de aquí construiremos la lógica para diseñar la estrategia de purificación.")
