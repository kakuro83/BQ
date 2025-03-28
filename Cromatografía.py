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

url_datos = "https://raw.githubusercontent.com/kakuro83/BQ/main/Datos.csv"
df_datos = cargar_csv_desde_github(url_datos, "Datos")

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

df_ejercicio = cargar_hoja("Ejercicio", sheets["Ejercicio"])

# 🎓 Selección de participante y proteína
st.subheader("🎓 Selección de Participante y Proteína")
proteinas_disponibles = df_ejercicio["Nombre"].dropna().unique().tolist()
proteina_seleccionada = st.selectbox("🧪 Proteína objetivo:", ["Seleccionar proteína"] + proteinas_disponibles)

if proteina_seleccionada == "Seleccionar proteína":
    st.info("Por favor, selecciona una proteína para continuar.")
else:
    df_proteina = df_ejercicio[df_ejercicio["Nombre"] == proteina_seleccionada]

    # Mostrar información de la proteína (filtrando columnas relevantes)
    columnas_info = ["Nombre", "Carga", "Etiquetas", "Propiedades", "Cantidad (mg)"]
    st.subheader("🔬 Información de la proteína seleccionada")
    st.dataframe(
        df_proteina[columnas_info]
        .style.set_properties(**{"text-align": "center"})
        .set_table_styles([{"selector": "th", "props": [("text-align", "center")]}]),
        use_container_width=True,
        hide_index=True
    )

# 🧫 Procesamiento de bandas SDS-PAGE (solo si hay proteína seleccionada)
if proteina_seleccionada != "Seleccionar proteína":
    bandas = ["A", "B", "C", "D", "E"]
    columnas_bandas = ["Recorrido", "Abundancia (%)", "Carga neta", "Propiedad estructural"]
    data_bandas = {col: [] for col in columnas_bandas}

    for banda in bandas:
        valores = df_proteina[f"Banda {banda}"].values[0].split(";")
        for i, col in enumerate(columnas_bandas):
            data_bandas[col].append(valores[i].strip())

    df_bandas = pd.DataFrame(data_bandas)

    st.subheader("🧫 Bandas SDS-PAGE de la mezcla")
    st.dataframe(
        df_bandas.style.set_properties(**{"text-align": "center"}).set_table_styles(
            [{"selector": "th", "props": [("text-align", "center")]}]
        ),
        use_container_width=True,
        hide_index=True
    )

url_purificacion = "https://raw.githubusercontent.com/kakuro83/BQ/main/Purificaci%C3%B3n.csv"
df_purificacion = cargar_csv_desde_github(url_purificacion, "Purificación")

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

# ⚠️ Validación previa
if proteina_seleccionada == "Seleccionar proteína":
    st.warning("Selecciona una proteína para continuar con la estrategia.")
    st.stop()

# ⚗️ Estrategia de Purificación
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

# Información de técnicas de purificación
st.markdown("### 🧪 Detalles de cada técnica disponible")
tecnica_info = st.selectbox("Selecciona una técnica para revisar su información:", df_purificacion["Técnica"].dropna().tolist())

fila_tec = df_purificacion[df_purificacion["Técnica"] == tecnica_info]
if not fila_tec.empty:
    fila = fila_tec.iloc[0]
    st.markdown(f"""
- **Capacidad:** {fila['Capacidad (mg)']} mg  
- **Costo por corrida:** {fila['Costo (USD)']} USD  
- **Recuperación estimada:** {fila['Recuperación (%)']} %  
- **Pureza base esperada:** {fila['Pureza base (%)']} %  
- **Velocidad media:** {fila['Velocidad media (mg/min)']} mg/min  
- **Pureza máxima alcanzable:** {fila['Pureza máxima (%)']} %
""")

# Obtener info de la proteína objetivo
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

# Ciclo por etapas
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

            # Validaciones técnicas
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

            # Cálculos
            mezcla_etapa = recuperacion_anterior / (pureza_inicial / 100)
            carga = carga_por_corrida(mezcla_etapa, corridas)
            fs = factor_saturacion(carga, capacidad)
            recuperacion = recuperacion_proteina(recuperacion_pct, fs, mezcla_etapa, pureza_inicial)
            pureza_estim = calcular_pureza(velocidad, pureza_base, vmax, pmax, pureza_inicial)
            pureza_corr = ajustar_pureza_por_selectividad(tecnica, pureza_estim, df_bandas)
            tiempo_min = calcular_tiempo(carga, velocidad, corridas)
            tiempo_h = tiempo_min / 60
            costo_operativo_str = df_datos[df_datos["Parámetro"] == "Costos fijos operativos (USD/h)"]["Valor"].values[0]
            costo_operativo = float(costo_operativo_str.replace(",", "."))
            costo_total = calcular_costo(costo_columna, corridas) + (tiempo_h * costo_operativo * 2)

            # Acumuladores
            costos_acumulados += costo_total
            tiempo_total_h += tiempo_h

            # Mostrar resultados por etapa (agrupados)
            colres1, colres2, colres3 = st.columns(3)
            with colres1:
                st.info(f"📦 Fs: `{fs:.2f}`")
            with colres2:
                st.success(f"✅ Recuperación: `{recuperacion:.2f}` mg")
            with colres3:
                st.warning(f"💲 Costo etapa: `{costo_total:.2f} USD`")

            colres4, colres5 = st.columns(2)
            with colres4:
                st.info(f"📊 Pureza estimada: `{pureza_estim:.1f}%` → 😎 Ajustada: `{pureza_corr:.1f}%`")
            with colres5:
                st.warning(f"⏱️ Tiempo estimado: `{tiempo_h:.2f}` h")

            # Preparar condiciones para la siguiente etapa
            pureza_inicial = pureza_corr
            recuperacion_anterior = recuperacion

# 💰 Resultados Finales del Proceso
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

    nivel_aplicado = max([n for n in niveles if pureza_inicial >= umbrales[n]], default=None)
    if nivel_aplicado is None:
        st.error("❌ No se alcanzó ningún nivel mínimo de pureza comercial.")
        st.stop()

    valor_unitario_usd_mg = precios[nivel_aplicado]
    costo_operativo_str = df_datos[df_datos["Parámetro"] == "Costos fijos operativos (USD/h)"]["Valor"].values[0]
    costo_operativo = float(costo_operativo_str.replace(",", "."))

    ganancia_bruta = recuperacion_anterior * valor_unitario_usd_mg
    ganancia_neta = ganancia_bruta - costos_acumulados - (costo_operativo * tiempo_total_h)
    rentabilidad = ganancia_neta / tiempo_total_h if tiempo_total_h > 0 else 0

    emoji_ganancia = "😊" if ganancia_neta >= 0 else "😢"

    # Mostrar resultados
    st.markdown(f"- 🧪 **Pureza final alcanzada:** `{pureza_inicial:.2f}%`")
    st.markdown(f"- 📦 **Recuperación final:** `{recuperacion_anterior:.2f}` mg")
    st.markdown(f"- ⏱️ **Tiempo total del proceso:** `{tiempo_total_h:.2f}` horas")
    st.markdown(f"- 💲 **Costo total acumulado:** `{costos_acumulados:.2f} USD`")
    st.markdown(f"- 💰 **Ganancia neta estimada:** `{ganancia_neta:.2f} USD` {emoji_ganancia}")
    st.markdown(f"- 📈 **Rentabilidad:** `{rentabilidad:.2f} USD/h`")
    st.caption(f"Nivel de pureza comercial aplicado: {nivel_aplicado} (≥ {umbrales[nivel_aplicado]}%) → {valor_unitario_usd_mg} USD/mg")

except Exception as e:
    st.error(f"❌ Error al calcular los resultados finales: {e}")

# 📋 Generar código de validación
siglas_manual = {
    "afinidad his-tag": "His",
    "afinidad lectina": "Lec"
}

codigo_etapas = []

for i in range(1, 5):
    tecnica = st.session_state.get(f"tecnica_{i}")
    corridas = st.session_state.get(f"corridas_{i}")
    velocidad = st.session_state.get(f"velocidad_{i}")

    if tecnica and tecnica != "Seleccionar":
        if corridas is not None and velocidad is not None:
            tecnica_sigla = tecnica.strip().lower()
            tecnica_lower = tecnica.lower()
            if "his" in tecnica_lower:
                sigla = "His"
            elif "lectina" in tecnica_lower:
                sigla = "Lec"
            else:
                # Buscar en df_purificacion la sigla entre paréntesis
                fila_tec = df_purificacion[df_purificacion["Técnica"] == tecnica]
                if not fila_tec.empty:
                    tecnica_texto = fila_tec["Técnica"].values[0]
                    if "(" in tecnica_texto and ")" in tecnica_texto:
                        sigla = tecnica_texto.split("(")[-1].split(")")[0].strip()
                    else:
                        sigla = tecnica.split()[0].upper()
                else:
                    sigla = tecnica.split()[0].upper()
            codigo_etapas.append(f"{sigla},{corridas},{velocidad}")

# Mostrar resultado
st.subheader("🔒 Código de Validación")

if codigo_etapas:
    resumen_etapas = "-".join(codigo_etapas)
    resumen_valores = f"{ganancia_neta:.2f},{rentabilidad:.2f}"
    codigo_validacion = f"{resumen_etapas}:{resumen_valores}"

    st.text_input("Código generado (puedes copiarlo):", value=codigo_validacion, key="codigo_generado")
    st.caption("Este código resume tu estrategia completa. Puedes usarlo para validar o comparar resultados.")
else:
    st.info("Primero define al menos una etapa válida para generar el código.")
