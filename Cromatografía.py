# 📥 Cromatografía.py - Bloque 1: Carga de datos desde Google Sheets (sin API externa), TXT y Excel (todo público)

import pandas as pd
import requests
import io
import streamlit as st

st.title("📥 Carga de datos - Sistema de Cromatografía")

# --- 1. Google Sheets (sin API externa, desde CSV export) ---
def cargar_csv_desde_google(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return pd.read_csv(io.StringIO(response.text)).dropna(how="all")
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Error al cargar CSV desde: {url}\n{e}")
        return pd.DataFrame()

# ID real del documento compartido y GID de las hojas
sheet_id = "1Rqk1GZ3Y5KKNT5VjTXI-pbFhlVZ-c-XcCCjmXAM6DiQ"
url_proteinas = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
url_columnas = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=830674505"
url_fijos = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=1578172910"

hoja_proteinas = cargar_csv_desde_google(url_proteinas)
hoja_columnas = cargar_csv_desde_google(url_columnas)
hoja_fijos = cargar_csv_desde_google(url_fijos)

if not hoja_fijos.empty:
    if "Parámetro" in hoja_fijos.columns and "Valor" in hoja_fijos.columns:
        parametros_fijos = dict(zip(hoja_fijos["Parámetro"], hoja_fijos["Valor"]))
    else:
        st.warning("⚠️ Las columnas esperadas 'Parámetro' y 'Valor' no están presentes en 'DatosFijos'.")
        parametros_fijos = {}
else:
    parametros_fijos = {}

# --- 2. TXT de Estudiantes desde GitHub ---
estudiantes_url = "https://raw.githubusercontent.com/kakuro83/BQ/3698fd9da17043e75779d8897fd0fe622229dfba/Estudiantes.txt"
lista_estudiantes = pd.read_csv(estudiantes_url, header=None)[0].dropna().tolist()

# --- 3. Excel para registro de respuestas desde GitHub ---
url_excel = "https://raw.githubusercontent.com/kakuro83/BQ/3698fd9da17043e75779d8897fd0fe622229dfba/Respuestas.xlsx"
try:
    import openpyxl
    response = requests.get(url_excel)
    df_respuestas = pd.read_excel(io.BytesIO(response.content), engine="openpyxl")
except ImportError:
    st.warning("⚠️ Falta el paquete 'openpyxl'. Agrega 'openpyxl' en requirements.txt para leer archivos Excel.")
    df_respuestas = pd.DataFrame()

# Verificación visual en Streamlit
st.success("✅ Datos cargados correctamente (sin APIs externas):")
st.markdown(f"- **Proteínas:** {len(hoja_proteinas)} entradas")
st.markdown(f"- **Columnas:** {len(hoja_columnas)} técnicas")
st.markdown(f"- **Parámetros fijos:** {len(parametros_fijos)}")
st.markdown(f"- **Estudiantes:** {len(lista_estudiantes)}")
st.markdown(f"- **Respuestas cargadas:** {df_respuestas.shape[0]} filas")

# Mostrar ejemplos
with st.expander("👁 Ver muestra de las tablas cargadas"):
    if not hoja_proteinas.empty:
        st.subheader("🔬 Proteínas")
        st.dataframe(hoja_proteinas.head())

    if not hoja_columnas.empty:
        st.subheader("🧪 Columnas de purificación")
        st.dataframe(hoja_columnas.head())

    if parametros_fijos:
        st.subheader("⚙️ Parámetros fijos")
        st.dataframe(pd.DataFrame(parametros_fijos.items(), columns=["Parámetro", "Valor"]))

    if lista_estudiantes:
        st.subheader("👤 Lista de estudiantes")
        st.write(lista_estudiantes[:5])

    if not df_respuestas.empty:
        st.subheader("📄 Respuestas registradas")
        st.dataframe(df_respuestas.head())
