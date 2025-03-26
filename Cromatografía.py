import streamlit as st
import pandas as pd
from ecuaciones import (
    carga_por_corrida,
    factor_saturacion,
    recuperacion_proteina,
    calcular_pureza,
    calcular_tiempo,
    calcular_costo,
    calcular_ganancia_neta,
    calcular_rentabilidad
)

st.set_page_config(page_title="Olimpiada de Bioquímica – Purificación de Proteínas")
st.title("🏆 Estrategia de Purificación de Proteínas")

url_hoja = "https://docs.google.com/spreadsheets/d/1Rqk1GZ3Y5KKNT5VjTXI-pbFhlVZ-c-XcCCjmXAM6DiQ/export?format=csv&gid="
sheets = {"Ejercicio": "0"}

# Función para cargar desde Google Sheets
def cargar_hoja(nombre, gid):
    try:
        enlace = url_hoja + gid
        df = pd.read_csv(enlace)
        # st.success(f"✅ Hoja '{nombre}' cargada correctamente desde Google Sheets.")
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar la hoja '{nombre}': {e}")
        return pd.DataFrame()

# Función para cargar CSV desde GitHub
@st.cache_data
def cargar_csv_desde_github(url_raw, nombre, header='infer', names=None):
    try:
        df = pd.read_csv(url_raw, header=header, names=names)
        # st.success(f"✅ Hoja '{nombre}' cargada correctamente desde GitHub.")
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar la hoja '{nombre}': {e}")
        return pd.DataFrame()

# Cargar los datos desde Google Sheets y GitHub
df_ejercicio = cargar_hoja("Ejercicio", sheets["Ejercicio"])

url_purificacion = "https://raw.githubusercontent.com/kakuro83/BQ/main/Purificaci%C3%B3n.csv"
df_purificacion = cargar_csv_desde_github(url_purificacion, "Purificación")

url_datos = "https://raw.githubusercontent.com/kakuro83/BQ/main/Datos.csv"
df_datos = cargar_csv_desde_github(url_datos, "Datos")

url_estudiantes = "https://raw.githubusercontent.com/kakuro83/BQ/main/Estudiantes.txt"
df_estudiantes = cargar_csv_desde_github(url_estudiantes, "Estudiantes", header=None, names=["Estudiante"])

# 📌 Datos Fijos – Mostrar en expander como lista
with st.expander("📌 Ver parámetros generales del sistema"):
    st.markdown("<h4 style='text-align: center;'>📋 Parámetros Generales</h4>", unsafe_allow_html=True)
    for _, fila in df_datos.iterrows():
        parametro = fila["Parámetro"]
        valor = fila["Valor"]
        st.markdown(f"- **{parametro}:** {valor}")

# 🧪 Información de columnas: selección individual
st.markdown("<h3 style='text-align: center'>🧪 Información de las Columnas de Purificación</h3>", unsafe_allow_html=True)
tecnica_elegida = st.selectbox("Selecciona una técnica de purificación:", df_purificacion["Técnica"].dropna().tolist())

fila_columna = df_purificacion[df_purificacion["Técnica"] == tecnica_elegida]
if not fila_columna.empty:
    fila = fila_columna.iloc[0]
    st.markdown("**📋 Detalles de la columna seleccionada:**")
    st.markdown(f"""
- **Capacidad:** {fila['Capacidad (mg)']} mg  
- **Costo:** {fila['Costo (USD)']} USD  
- **Recuperación estimada:** {fila['Recuperación (%)']} %  
- **Pureza base:** {fila['Pureza base (%)']} %  
- **Velocidad media:** {fila['Velocidad media (mg/min)']} mg/min  
- **Pureza máxima alcanzable:** {fila['Pureza máxima (%)']} %
""")
