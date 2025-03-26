# Cromatografía.py – App para Olimpiada de Bioquímica

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
st.title("🏆 Olimpiada de Bioquímica – Estrategia de Purificación de Proteínas")

url_hoja = "https://docs.google.com/spreadsheets/d/1Rqk1GZ3Y5KKNT5VjTXI-pbFhlVZ-c-XcCCjmXAM6DiQ/export?format=csv&gid="
sheets = {"Ejercicio": "0"}

# Función para cargar desde Google Sheets
def cargar_hoja(nombre, gid):
    try:
        enlace = url_hoja + gid
        df = pd.read_csv(enlace)
        # st.success(f"✅ Hoja '{nombre}' cargada correctamente desde Google Sheets.")  # Oculto
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar la hoja '{nombre}': {e}")
        return pd.DataFrame()

# Función para cargar CSV desde GitHub
@st.cache_data
def cargar_csv_desde_github(url_raw, nombre, header='infer', names=None):
    try:
        df = pd.read_csv(url_raw, header=header, names=names)
        # st.success(f"✅ Hoja '{nombre}' cargada correctamente desde GitHub.")  # Oculto
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar la hoja '{nombre}': {e}")
        return pd.DataFrame()
# Función para ajustar la pureza considerando CIEX, AIEX y SEC
def ajustar_pureza_por_selectividad(tecnica, pureza_estim, df_bandas):
    objetivo = df_bandas[df_bandas["Propiedad estructural"].str.lower() == "objetivo"]
    if objetivo.empty:
        return pureza_estim

    try:
        abundancia_obj = float(objetivo["Abundancia (%)"].values[0])
    except:
        return pureza_estim

    if "CIEX" in tecnica:
        retenidas = df_bandas[df_bandas["Carga neta"].astype(int) >= 1]
    elif "AIEX" in tecnica:
        retenidas = df_bandas[df_bandas["Carga neta"].astype(int) <= -1]
    elif "SEC" in tecnica:
        def calcular_mr(recorrido):
            try:
                return 10 ** (2.2 - 0.015 * float(recorrido))
            except:
                return float('inf')
        df_bandas["Mr"] = df_bandas["Recorrido"].apply(calcular_mr)
        retenidas = df_bandas[df_bandas["Mr"] <= 60]
    else:
        return pureza_estim

    suma_abundancias = retenidas["Abundancia (%)"].astype(float).sum()
    if suma_abundancias == 0:
        return pureza_estim

    pureza_corr = (abundancia_obj / suma_abundancias) * pureza_estim
    return round(pureza_corr, 2)

# Carga de los archivos desde Google Sheets y GitHub
df_ejercicio = cargar_hoja("Ejercicio", sheets["Ejercicio"])
url_purificacion = "https://raw.githubusercontent.com/kakuro83/BQ/main/Purificaci%C3%B3n.csv"
df_purificacion = cargar_csv_desde_github(url_purificacion, "Purificación")

url_datos = "https://raw.githubusercontent.com/kakuro83/BQ/main/Datos.csv"
df_datos = cargar_csv_desde_github(url_datos, "Datos")

url_estudiantes = "https://raw.githubusercontent.com/kakuro83/BQ/main/Estudiantes.txt"
df_estudiantes = cargar_csv_desde_github(url_estudiantes, "Estudiantes", header=None, names=["Estudiante"])

# Mostrar los datos fijos
st.header("📌 Datos Fijos")
st.dataframe(df_datos)

# Mostrar la información de columnas
st.header("🧪 Información de las Columnas de Purificación")
st.dataframe(df_purificacion)

# Selección de estudiante y proteína
lista_estudiantes = df_estudiantes["Estudiante"].dropna().tolist()
estudiante_seleccionado = st.selectbox("Selecciona tu nombre:", ["Seleccionar estudiante"] + lista_estudiantes)

proteinas_disponibles = df_ejercicio["Nombre"].dropna().unique().tolist()
proteina_seleccionada = st.selectbox("Selecciona la proteína objetivo:", ["Seleccionar proteína"] + proteinas_disponibles)

if proteina_seleccionada != "Seleccionar proteína":
    df_proteina = df_ejercicio[df_ejercicio["Nombre"] == proteina_seleccionada]
    st.subheader("🔬 Información de la proteína seleccionada")
    st.dataframe(df_proteina)

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
    st.dataframe(df_bandas)

# Bloque de estrategia: diseño de hasta 4 etapas
    st.header("⚗️ Estrategia de Purificación")
st.markdown("""
🔧 En esta sección debes diseñar una estrategia de hasta **4 etapas de purificación**.

🧪 La **recuperación** de la proteína objetivo depende del **factor de saturación (Fs)**, que se calcula como:

> Fs = Carga pasada por corrida / Capacidad de la columna

📉 Si la columna está sobrecargada (Fs > 1), la recuperación se reduce.

💧 La **pureza** alcanzada dependerá de la **velocidad de alimentación (mg/min)**: velocidades más bajas permiten mejores separaciones.

💰 Los **costos totales** incluyen:
- El costo por cada corrida de columna,
- Los **costos fijos operativos (USD/h)**,
- Y los **costos por tiempo**, que aumentan con la duración del proceso.
""")


    # Obtener info de la proteína objetivo desde SDS-PAGE
objetivo = df_bandas[df_bandas["Propiedad estructural"].str.lower() == "objetivo"]
    if not objetivo.empty:
        abundancia_objetivo = float(objetivo["Abundancia (%)"].values[0])
        carga_objetivo = int(objetivo["Carga neta"].values[0])
        recorrido_objetivo = float(objetivo["Recorrido"].values[0])
        etiquetas_objetivo = df_proteina["Etiquetas"].values[0].lower()
    else:
        st.error("❌ No se encontró la banda con 'Objetivo' en el análisis SDS-PAGE.")
        st.stop()

    # Condiciones iniciales
    pureza_inicial = abundancia_objetivo
    recuperacion_anterior = float(df_proteina["Cantidad (mg)"].values[0]) * (abundancia_objetivo / 100)
    costos_acumulados = 0
    tiempo_total_h = 0

    opciones_tecnicas = ["Seleccionar"] + df_purificacion["Técnica"].dropna().tolist()

    for i in range(1, 5):
        st.markdown(f"### Etapa {i}")
        col1, col2, col3 = st.columns(3)
        tecnica = col1.selectbox(f"Técnica {i}", opciones_tecnicas, key=f"tecnica_{i}")
        corridas = col2.number_input(f"Corridas {i}", min_value=1, value=1, key=f"corridas_{i}")
        velocidad = col3.number_input(f"Velocidad (mg/min) {i}", min_value=0.1, value=1.0, step=0.1, key=f"velocidad_{i}")

        if tecnica != "Seleccionar":
            fila = df_purificacion[df_purificacion["Técnica"] == tecnica]
            if not fila.empty:
                capacidad = float(fila["Capacidad (mg)"].values[0])
                costo_columna = float(fila["Costo (USD)"].values[0])
                recuperacion_pct = float(fila["Recuperación (%)"].values[0])
                pureza_base = float(fila["Pureza base (%)"].values[0])
                vmax = float(fila["Velocidad media (mg/min)"].values[0])
                pmax = float(fila["Pureza máxima (%)"].values[0])

                # Validaciones técnicas por tipo de columna
                advertencia = ""
                tecnica_lower = tecnica.lower()
                if "intercambio catiónico" in tecnica_lower and carga_objetivo < 1:
                    advertencia = "⚠️ CIEX solo retiene proteínas con carga neta ≥ +1."
                elif "intercambio aniónico" in tecnica_lower and carga_objetivo > -1:
                    advertencia = "⚠️ AIEX solo retiene proteínas con carga neta ≤ -1."
                elif "his-tag" in tecnica_lower and "his-tag" not in etiquetas_objetivo:
                    advertencia = "⚠️ Se requiere la etiqueta 'His-tag' para esta columna."
                elif "lectina" in tecnica_lower and "glicoproteína" not in etiquetas_objetivo:
                    advertencia = "⚠️ Se requiere que la proteína sea una glicoproteína."
                elif "tamaño" in tecnica_lower:
                    mr_objetivo = 10 ** (2.2 - 0.015 * recorrido_objetivo)
                    if mr_objetivo > 60:
                        advertencia = f"⚠️ Mr estimado: {mr_objetivo:.1f} kDa. SEC solo permite proteínas ≤ 60 kDa."

                if advertencia:
                    st.warning(advertencia)

                # Mezcla de entrada para esta etapa
                mezcla_etapa = recuperacion_anterior / (pureza_inicial / 100)
                carga = carga_por_corrida(mezcla_etapa, corridas)
                fs = factor_saturacion(carga, capacidad)

                # Recuperación
                recuperacion = recuperacion_proteina(recuperacion_pct, fs, mezcla_etapa, pureza_inicial)
                
                # Pureza
                pureza_estim = calcular_pureza(velocidad, pureza_base, vmax, pmax, pureza_inicial)
                pureza_corr = ajustar_pureza_por_selectividad(tecnica, pureza_estim, df_bandas)

                # Tiempo y costo
                tiempo_min = calcular_tiempo(carga, velocidad, corridas)
                tiempo_h = tiempo_min / 60
                
                # Obtener costo operativo (con coma decimal corregida)
                costo_operativo_str = df_datos[df_datos["Parámetro"] == "Costos fijos operativos (USD/h)"]["Valor"].values[0]
                costo_operativo = float(costo_operativo_str.replace(",", "."))
                
                # Costo total = costo de columna + costo operativo por tiempo
                costo_total = calcular_costo(costo_columna, corridas) + (tiempo_h * costo_operativo * 2)

                # Acumular totales
                costos_acumulados += costo_total
                tiempo_total_h += tiempo_h

                # Mostrar resultados por etapa
                st.success(f"✅ Recuperación: `{recuperacion:.2f}` mg")
                st.info(f"📊 Pureza estimada: `{pureza_estim:.1f}%` → Ajustada: `{pureza_corr:.1f}%`")
                st.warning(f"⏱️ Tiempo estimado: `{tiempo_h:.2f}` h")
                st.markdown(f"💲 Costo total etapa: `{costo_total:.2f} USD`")
                st.markdown(f"📦 Factor de saturación (Fs): `{fs:.2f}`")

                # Preparar condiciones para la siguiente etapa
                pureza_inicial = pureza_corr
                recuperacion_anterior = recuperacion

    # Resultados Finales del Proceso
    st.subheader("💰 Resultados Finales del Proceso")
    st.markdown("Estos valores consideran únicamente la **última etapa procesada**.")

    try:
        niveles = [1, 2, 3, 4]
        precios = {}
        umbrales = {}
        for n in niveles:
            valor_str = df_datos[df_datos["Parámetro"] == f"Valor comercial nivel {n} (USD)"]["Valor"].values[0]
            pureza_str = df_datos[df_datos["Parámetro"] == f"Pureza mínima nivel {n} (%)"]["Valor"].values[0]
            precios[n] = float(valor_str.replace(",", "."))
            umbrales[n] = float(pureza_str.replace(",", "."))

        # Determinar nivel de precio por pureza final
        nivel_aplicado = max([n for n in niveles if pureza_inicial >= umbrales[n]], default=None)
        if nivel_aplicado is None:
            st.error("❌ No se alcanzó ningún nivel mínimo de pureza comercial.")
            st.stop()

        valor_unitario_str = df_datos[df_datos["Parámetro"] == "Costos fijos operativos (USD/h)"]["Valor"].values[0]
        valor_unitario_usd_mg = precios[nivel_aplicado]
        costo_operativo = float(valor_unitario_str.replace(",", "."))

        ganancia_bruta = recuperacion_anterior * valor_unitario_usd_mg
        ganancia_neta = ganancia_bruta - costos_acumulados - (costo_operativo * tiempo_total_h)
        rentabilidad = ganancia_neta / tiempo_total_h if tiempo_total_h > 0 else 0

        # Mostrar resultados finales
        st.markdown(f"- 🧪 **Pureza final alcanzada:** `{pureza_inicial:.2f}%`")
        st.markdown(f"- 📦 **Recuperación final:** `{recuperacion_anterior:.2f}` mg")
        st.markdown(f"- ⏱️ **Tiempo total del proceso:** `{tiempo_total_h:.2f}` horas")
        st.markdown(f"- 💲 **Costo total acumulado:** `{costos_acumulados:.2f} USD`")
        st.markdown(f"- 💰 **Ganancia neta estimada:** `{ganancia_neta:.2f} USD`")
        st.markdown(f"- 📈 **Rentabilidad:** `{rentabilidad:.2f} USD/h`")
        st.caption(f"Nivel de pureza comercial aplicado: {nivel_aplicado} (≥ {umbrales[nivel_aplicado]}%) → {valor_unitario_usd_mg} USD/mg")

    except Exception as e:
        st.error(f"❌ Error al calcular los resultados finales: {e}")
