# 📥 Cromatografía.py - Bloque 1: Carga de datos desde Google Sheets (sin API externa), TXT y Excel (todo público)

import pandas as pd
import requests
import io

# --- 1. Google Sheets (sin API externa, desde CSV export) ---
# Exportar cada hoja como CSV directamente desde el enlace público

def cargar_csv_desde_google(sheet_id, gid):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    return pd.read_csv(url).dropna()

sheet_id = "1Rqk1GZ3Y5KKNT5VjTXI-pbFhlVZ-c-XcCCjmXAM6DiQ"

# Cargar las hojas específicas (usa el GID de cada hoja)
hoja_proteinas = cargar_csv_desde_google(sheet_id, "0")  # VariablesEjercicio
hoja_columnas = cargar_csv_desde_google(sheet_id, "830674505")  # ColumnasPurificación
hoja_fijos = cargar_csv_desde_google(sheet_id, "1578172910")  # DatosFijos

# Convertir a diccionario de parámetros
parametros_fijos = dict(zip(hoja_fijos["Parámetro"], hoja_fijos["Valor"]))

# --- 2. TXT de Estudiantes desde GitHub (público raw) ---
estudiantes_url = "https://raw.githubusercontent.com/kakuro83/BQ/3698fd9da17043e75779d8897fd0fe622229dfba/Estudiantes.txt"
lista_estudiantes = pd.read_csv(estudiantes_url, header=None)[0].dropna().tolist()

# --- 3. Excel para registro de respuestas desde GitHub (público raw) ---
url_excel = "https://raw.githubusercontent.com/kakuro83/BQ/3698fd9da17043e75779d8897fd0fe622229dfba/Respuestas.xlsx"
response = requests.get(url_excel)
df_respuestas = pd.read_excel(io.BytesIO(response.content))

# Verificación (opcional)
print("✅ Datos cargados correctamente (sin APIs externas):")
print(f"- Proteínas: {len(hoja_proteinas)} entradas")
print(f"- Columnas: {len(hoja_columnas)} técnicas")
print(f"- Parámetros fijos: {len(parametros_fijos)}")
print(f"- Estudiantes: {len(lista_estudiantes)}")
print(f"- Respuestas cargadas: {df_respuestas.shape[0]} filas")
