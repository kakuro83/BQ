# Cromatografía_modificado.py

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

# Funciones de carga

def cargar_hoja(nombre, gid):
    try:
        enlace = url_hoja + gid
        df = pd.read_csv(enlace)
        # st.success(f"✅ Hoja '{nombre}' cargada correctamente desde Google Sheets.")
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar la hoja '{nombre}': {e}")
        return pd.DataFrame()

@st.cache_data
def cargar_csv_desde_github(url_raw, nombre, header='infer', names=None):
    try:
        df = pd.read_csv(url_raw, header=header, names=names)
        # st.success(f"✅ Hoja '{nombre}' cargada correctamente desde GitHub.")
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar la hoja '{nombre}': {e}")
        return pd.DataFrame()

# Carga de archivos externos
df_ejercicio = cargar_hoja("Ejercicio", sheets["Ejercicio"])
df_purificacion = cargar_csv_desde_github("https://raw.githubusercontent.com/kakuro83/BQ/main/Purificaci%C3%B3n.csv", "Purificación")
df_datos = cargar_csv_desde_github("https://raw.githubusercontent.com/kakuro83/BQ/main/Datos.csv", "Datos")
df_estudiantes = cargar_csv_desde_github("https://raw.githubusercontent.com/kakuro83/BQ/main/Estudiantes.txt", "Estudiantes", header=None, names=["Estudiante"])

# Mostrar tablas iniciales
st.header("📌 Datos Fijos")
st.dataframe(df_datos.style.set_properties(**{"text-align": "center"}).set_table_styles([{"selector": "th", "props": [("text-align", "center")]}]), use_container_width=True)

st.header("🧪 Información de las Columnas de Purificación")
st.dataframe(df_purificacion.style.set_properties(**{"text-align": "center"}).set_table_styles([{"selector": "th", "props": [("text-align", "center")]}]), use_container_width=True)

# Selección de estudiante y proteína
st.subheader("🎓 Selección de Participante y Proteína")
col1, col2 = st.columns(2)

with col1:
    estudiante_seleccionado = st.selectbox("👤 Estudiante:", ["Seleccionar estudiante"] + df_estudiantes["Estudiante"].dropna().tolist())

with col2:
    proteinas_disponibles = df_ejercicio["Nombre"].dropna().unique().tolist()
    proteina_seleccionada = st.selectbox("🧪 Proteína objetivo:", ["Seleccionar proteína"] + proteinas_disponibles)

if estudiante_seleccionado == "Seleccionar estudiante" or proteina_seleccionada == "Seleccionar proteína":
    st.info("Por favor, selecciona un estudiante y una proteína para continuar.")

if proteina_seleccionada != "Seleccionar proteína":
    df_proteina = df_ejercicio[df_ejercicio["Nombre"] == proteina_seleccionada]
    st.subheader("🔬 Información de la proteína seleccionada")
    columnas_info = ["Nombre", "Carga", "Etiquetas", "Propiedades", "Cantidad (mg)"]
    st.dataframe(df_proteina[columnas_info].style.set_properties(**{"text-align": "center"})
                 .set_table_styles([{"selector": "th", "props": [("text-align", "center")]}]),
                 use_container_width=True)

    # Procesamiento de bandas SDS-PAGE
    bandas = ["A", "B", "C", "D", "E"]
    columnas_bandas = ["Recorrido", "Abundancia (%)", "Carga neta", "Propiedad estructural"]
    data_bandas = {col: [] for col in columnas_bandas}

    for banda in bandas:
        valores = df_proteina[f"Banda {banda}"].values[0].split(";")
        for i, col in enumerate(columnas_bandas):
            data_bandas[col].append(valores[i].strip())

    df_bandas = pd.DataFrame(data_bandas)
    st.subheader("🧫 Bandas SDS-PAGE de la mezcla")
    st.dataframe(df_bandas.style.set_properties(**{"text-align": "center"})
                 .set_table_styles([{"selector": "th", "props": [("text-align", "center")]}]),
                 use_container_width=True)

    # Estrategia de purificación
    st.header("⚗️ Estrategia de Purificación")

    with st.expander("📘 Consideraciones importantes"):
        st.markdown("""
Cada **corrida** representa la cantidad de mezcla de proteínas que se procesa por la columna. Es importante tener en cuenta la **capacidad máxima** de cada columna para evitar sobrecargas. Para ello, utilizamos el **Factor de Saturación (Fs)**:

- Si **Fs > 1**, la columna está sobrecargada. Esto no siempre es negativo, pero puede reducir la **recuperación**.
- Si **Fs < 1**, la recuperación puede mejorar, pero se requieren más corridas, lo que **incrementa el costo total del proceso**.

La **pureza** de la proteína es clave para definir su **valor comercial**. Un factor determinante en esta pureza es la **velocidad de procesamiento**:

- Velocidades **menores** a la velocidad media aumentan la pureza, pero **prolongan el tiempo** (y por tanto, los costos).
- Velocidades **mayores** aceleran el proceso, pero **reducen la pureza**, afectando el precio de venta.

También debes tener en cuenta las **limitaciones técnicas** de ciertas columnas:

- Las de **intercambio iónico** discriminan según la **carga neta** de la proteína.
- Las de **exclusión por tamaño (SEC)** dependen del **peso molecular**.

Si en alguna etapa seleccionas una columna **inadecuada** para las propiedades de la proteína objetivo, el sistema te lo advertirá para que puedas ajustar tu estrategia.
""")

