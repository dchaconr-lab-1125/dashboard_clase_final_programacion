# Flight Delay Time Statistics — Dashboard con Dash

## Título y URL pública

**URL:** `https://<COMPLETAR-DESPUES-DE-DESPLEGAR>.onrender.com`

> Reemplaza este enlace por el tuyo una vez publicado en Render (ver sección
> "Cómo ejecutarlo en local" y las instrucciones de despliegue del enunciado).

## Descripción

Este tablero interactivo permite a cualquier persona del área de operaciones
de una aerolínea escribir un **año** y ver, al instante, el **tiempo promedio
de retraso (en minutos) por aerolínea y por mes**, separado en cinco causas:
transportista (*carrier*), clima, sistema aéreo nacional (NAS), seguridad y
aeronave tardía (*late aircraft*). Está pensado para que la dirección lo
consulte por sí misma, sin depender de un analista ni instalar nada.

## Tabla de componentes

| id (`dcc.Graph`) | Qué grafica | Bloque del layout |
|---|---|---|
| `carrier-plot`  | Promedio mensual de retraso por transportista, por aerolínea | Fila 1, columna izquierda |
| `weather-plot`  | Promedio mensual de retraso por clima, por aerolínea | Fila 1, columna derecha |
| `nas-plot`      | Promedio mensual de retraso del sistema aéreo nacional, por aerolínea | Fila 2, columna izquierda |
| `security-plot` | Promedio mensual de retraso por seguridad, por aerolínea | Fila 2, columna derecha |
| `late-plot`     | Promedio mensual de retraso por aeronave tardía, por aerolínea | Fila 3, ancho centrado (65%) |

El control `dcc.Input(id="input-year")` (número, valor por defecto `2010`)
alimenta un único `@app.callback` que recalcula y devuelve las cinco figuras.

## Cómo ejecutarlo en local

```powershell
# 1. Entorno virtual e instalación de librerías
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 2. Ejecutar el dashboard
.\.venv\Scripts\python.exe dashboard.py
```

Abre `http://127.0.0.1:8050` en el navegador. Se detiene con `Ctrl+C`.

En macOS/Linux el intérprete del entorno es `.venv/bin/python`.

## Estructura del proyecto

```text
.
├── dashboard.py          # aplicación Dash: layout + compute_info() + callback (RF1–RF10)
├── airline_data.csv      # datos: vuelos domésticos de EE. UU., 1987–2020
├── requirements.txt      # dependencias (incluye gunicorn)
├── Procfile               # comando de arranque en producción (formato Heroku)
├── render.yaml            # infraestructura como código para Render
├── .python-version        # versión de Python del servidor
├── .gitignore              # excluye .venv/ y basura de Python
└── README.md               # este archivo
```

## Datos

- **Fuente:** Airline Reporting Carrier On-Time Performance Dataset (IBM
  Developer / Data Asset eXchange), muestra del curso.
- **Filas:** 27 000. **Años cubiertos:** 1987–2020. **Aerolíneas:** 33.
- **Transformaciones:** lectura con `encoding="ISO-8859-1"`; las columnas
  `Div1Airport`, `Div1TailNum`, `Div2Airport`, `Div2TailNum` se leen como
  texto para no perder ceros a la izquierda. `compute_info()` filtra por
  año y agrupa por `["Month", "Reporting_Airline"]`, calculando el
  promedio de `CarrierDelay`, `WeatherDelay`, `NASDelay`, `SecurityDelay`
  y `LateAircraftDelay`.

## Decisiones de diseño

- **Gráficos de línea** (`px.line`) porque la variable de interés es una
  serie temporal (mes) comparada entre categorías (aerolínea); una línea
  por aerolínea deja ver la tendencia mensual con más claridad que barras.
- **Color = aerolínea**, con la paleta cualitativa por defecto de Plotly
  (no distingue solo por rojo/verde) y leyenda visible para identificar
  cada serie.
- **Ejes rotulados con unidades** ("minutes") en cada gráfico.
- **Layout en bloques `flex`** (dos columnas por fila) para que los cinco
  gráficos no queden apilados uno debajo de otro.
- **Robustez (RF5):** si el campo de año está vacío o no es numérico, o si
  el año no tiene datos, el tablero no lanza una excepción: muestra
  figuras vacías con un mensaje o gráficos con el aviso "(sin datos)" en
  el título.

## Autoría

Nombre: _completar_
Fecha: 24 de septiembre de 2026
