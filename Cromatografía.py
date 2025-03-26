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

# 📌 Datos Fijos – Mostrar en expander como lista y tabla de precios
with st.expander("📌 Ver parámetros generales del sistema"):
    st.markdown("<h4 style='text-align: center;'>📋 Parámetros Generales</h4>", unsafe_allow_html=True)

    if not df_datos.empty:
        # Mostrar todos los parámetros excepto los de nivel comercial
        for _, fila in df_datos.iterrows():
            parametro = fila["Parámetro"]
            if "Valor comercial nivel" not in parametro and "Pureza mínima nivel" not in parametro:
                valor = fila["Valor"]
                st.markdown(f"- **{parametro}:** {valor}")

        # Construir tabla con los niveles de pureza y precios
        try:
            niveles = []
            precios = []
            umbrales = []

            for i in range(1, 5):
                valor_str = df_datos[df_datos["Parámetro"] == f"Valor comercial nivel {i} (USD)"]["Valor"].values[0]
                pureza_str = df_datos[df_datos["Parámetro"] == f"Pureza mínima nivel {i} (%)"]["Valor"].values[0]
                niveles.append(f"Nivel {i}")
                precios.append(f"{valor_str} USD/mg")
                umbrales.append(f"≥ {pureza_str} %")

            df_precios = pd.DataFrame({
                "Nivel de Pureza": niveles,
                "Pureza mínima": umbrales,
                "Precio por mg": precios
            })

            st.markdown("<h5 style='text-align: center;'>💰 Niveles de Pureza Comercial</h5>", unsafe_allow_html=True)
            st.dataframe(
                df_precios.style.set_properties(**{"text-align": "center"}).set_table_styles(
                    [{"selector": "th", "props": [("text-align", "center")]}]
                ),
                use_container_width=True,
                hide_index=True
            )
        except Exception as e:
            st.error(f"⚠️ No fue posible generar la tabla de precios: {e}")
    else:
        st.warning("⚠️ No se pudo cargar correctamente la hoja de parámetros.")
