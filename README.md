# 🧪 Estrategia de Purificación de Proteínas – Olimpiada de Bioquímica

Esta aplicación desarrollada en Streamlit permite simular estrategias de purificación de proteínas utilizando técnicas cromatográficas reales, considerando restricciones técnicas, costos, recuperación, pureza y rentabilidad.

## 🎯 Objetivo

Permitir a los estudiantes diseñar estrategias de purificación multietapa a partir de un perfil SDS-PAGE, visualizando resultados en tiempo real y generando un código de validación para evaluación.

## 📂 Estructura de la Aplicación

- **Selección de estudiante y proteína objetivo**: a partir de hojas en línea.
- **Visualización del perfil SDS-PAGE**: recorrido, carga neta, abundancia y propiedades.
- **Visualización de parámetros fijos y niveles de pureza comercial.**
- **Selección de técnicas cromatográficas por etapa (hasta 4)**, con advertencias técnicas.
- **Cálculos automáticos por etapa**:
  - Factor de saturación
  - Recuperación
  - Pureza estimada y ajustada
  - Costo por etapa
  - Tiempo requerido
- **Resultados finales**:
  - Pureza y recuperación final
  - Costo total
  - Ganancia neta
  - Rentabilidad (USD/h)
- **Generación automática de un código de validación**.

## 💡 Tecnologías usadas

- Python + Streamlit
- Pandas para análisis de datos
- Google Sheets y GitHub como fuentes de datos externas

## 🧾 Código de Validación

El sistema genera automáticamente un código compacto que resume la estrategia:
```
CIEX,2,1.5-SEC,1,0.8:157.34,32.14
```
Formato:  
`Sigla,Técnica,Corridas,Velocidad` (por etapa) `:Ganancia,Rentabilidad`

## 🔗 Enlaces

- Datos de entrada desde:
  - Google Sheets: perfiles de ejercicio
  - GitHub: parámetros y técnicas
- Repositorio del proyecto: _pendiente de enlace_

## 🛠️ Requisitos

- Python 3.10+
- Streamlit
- Pandas

Instalación:

```bash
pip install streamlit pandas
```

Ejecución:

```bash
streamlit run Cromatografía.py
```

## 🧑‍💻 Autor

Desarrollado en colaboración con docentes e investigadores del área de Bioquímica y Biotecnología, con enfoque en formación práctica en estrategias de purificación de proteínas.
