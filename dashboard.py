"""Dashboard interactivo de retrasos de vuelos (tarea).

Ejecutar en desarrollo:
    python dashboard.py        ->  http://127.0.0.1:8050

Ejecutar en produccion (lo hace la plataforma de despliegue):
    gunicorn dashboard:server  ->  usa el objeto WSGI `server` de este modulo
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure
from dash import Dash, Input, Output, dcc, html

# --------------------------------------------------------------------- datos
# Los datos viajan CON el repositorio y se leen desde la carpeta del archivo.
# NO uses rutas absolutas: en el servidor las rutas son distintas.
DATA_FILE = Path(__file__).with_name("airline_data.csv")

df = pd.read_csv(
    DATA_FILE,
    encoding="ISO-8859-1",
    # Estos campos traen ceros a la izquierda: deben leerse como texto.
    dtype={
        "Div1Airport": str,
        "Div1TailNum": str,
        "Div2Airport": str,
        "Div2TailNum": str,
    },
)

app = Dash(__name__)

# -------------------------------------------------------------------- layout
# RF1 - RF3 - RF10: titulo, control de entrada y cinco graficos en bloques
app.layout = html.Div(
    children=[
        html.H1(
            "Flight Delay Time Statistics",
            style={"textAlign": "center", "color": "#503D36", "font-size": 30},
        ),
        html.Div(
            ["Input Year: ", dcc.Input(id="input-year", type="number", value=2010,
                                        style={"height": "35px", "font-size": 30})],
            style={"font-size": 30, "textAlign": "center"},
        ),
        html.Br(),
        html.Br(),
        # Bloque 1: carrier + weather
        html.Div(
            [
                html.Div(dcc.Graph(id="carrier-plot"), style={"width": "50%"}),
                html.Div(dcc.Graph(id="weather-plot"), style={"width": "50%"}),
            ],
            style={"display": "flex"},
        ),
        # Bloque 2: nas + security
        html.Div(
            [
                html.Div(dcc.Graph(id="nas-plot"), style={"width": "50%"}),
                html.Div(dcc.Graph(id="security-plot"), style={"width": "50%"}),
            ],
            style={"display": "flex"},
        ),
        # Bloque 3: late aircraft (ocupa el ancho central, como pide la plantilla)
        html.Div(dcc.Graph(id="late-plot"), style={"width": "65%", "margin": "0 auto"}),
    ]
)


# ------------------------------------------------------------------ calculos
def compute_info(datos, entered_year):
    """Devuelve 5 tablas (una por causa de retraso) para el ano pedido.

    Cada tabla tiene las columnas: Month, Reporting_Airline y el promedio
    de la causa correspondiente. Si el ano no tiene filas, las tablas
    salen vacias (pero con las columnas correctas).
    """
    filtrado = datos[datos["Year"] == int(entered_year)]

    avg_carrier = (
        filtrado.groupby(["Month", "Reporting_Airline"])["CarrierDelay"]
        .mean()
        .reset_index()
    )
    avg_weather = (
        filtrado.groupby(["Month", "Reporting_Airline"])["WeatherDelay"]
        .mean()
        .reset_index()
    )
    avg_nas = (
        filtrado.groupby(["Month", "Reporting_Airline"])["NASDelay"]
        .mean()
        .reset_index()
    )
    avg_security = (
        filtrado.groupby(["Month", "Reporting_Airline"])["SecurityDelay"]
        .mean()
        .reset_index()
    )
    avg_late = (
        filtrado.groupby(["Month", "Reporting_Airline"])["LateAircraftDelay"]
        .mean()
        .reset_index()
    )

    return avg_carrier, avg_weather, avg_nas, avg_security, avg_late


def empty_figure(mensaje):
    """RF5: figura vacia con un mensaje claro, sin lanzar excepcion."""
    fig = Figure()
    fig.update_layout(
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[{
            "text": mensaje,
            "xref": "paper", "yref": "paper",
            "showarrow": False,
            "font": {"size": 18},
        }],
    )
    return fig


# ------------------------------------------------------------------ callback
@app.callback(
    [
        Output("carrier-plot", "figure"),
        Output("weather-plot", "figure"),
        Output("nas-plot", "figure"),
        Output("security-plot", "figure"),
        Output("late-plot", "figure"),
    ],
    Input("input-year", "value"),
)
def get_graph(entered_year):
    # RF5: robustez ante entrada vacia o no numerica
    if entered_year is None:
        vacio = empty_figure("Ingresa un año para ver los gráficos")
        return vacio, vacio, vacio, vacio, vacio

    try:
        anio = int(entered_year)
    except (ValueError, TypeError):
        vacio = empty_figure("Año no válido")
        return vacio, vacio, vacio, vacio, vacio

    avg_carrier, avg_weather, avg_nas, avg_security, avg_late = compute_info(df, anio)

    # RF5: si el ano no tiene datos, se avisa en el titulo en vez de fallar
    sin_datos = avg_carrier.empty

    carrier_fig = px.line(
        avg_carrier, x="Month", y="CarrierDelay", color="Reporting_Airline",
        title=f"Average carrier delay time (minutes) by airline - {anio}"
        + (" (sin datos)" if sin_datos else ""),
        labels={"CarrierDelay": "Carrier delay (minutes)", "Month": "Month",
                "Reporting_Airline": "Airline"},
    )
    weather_fig = px.line(
        avg_weather, x="Month", y="WeatherDelay", color="Reporting_Airline",
        title=f"Average weather delay time (minutes) by airline - {anio}"
        + (" (sin datos)" if sin_datos else ""),
        labels={"WeatherDelay": "Weather delay (minutes)", "Month": "Month",
                "Reporting_Airline": "Airline"},
    )
    nas_fig = px.line(
        avg_nas, x="Month", y="NASDelay", color="Reporting_Airline",
        title=f"Average NAS delay time (minutes) by airline - {anio}"
        + (" (sin datos)" if sin_datos else ""),
        labels={"NASDelay": "NAS delay (minutes)", "Month": "Month",
                "Reporting_Airline": "Airline"},
    )
    security_fig = px.line(
        avg_security, x="Month", y="SecurityDelay", color="Reporting_Airline",
        title=f"Average security delay time (minutes) by airline - {anio}"
        + (" (sin datos)" if sin_datos else ""),
        labels={"SecurityDelay": "Security delay (minutes)", "Month": "Month",
                "Reporting_Airline": "Airline"},
    )
    late_fig = px.line(
        avg_late, x="Month", y="LateAircraftDelay", color="Reporting_Airline",
        title=f"Average late aircraft delay time (minutes) by airline - {anio}"
        + (" (sin datos)" if sin_datos else ""),
        labels={"LateAircraftDelay": "Late aircraft delay (minutes)", "Month": "Month",
                "Reporting_Airline": "Airline"},
    )

    return carrier_fig, weather_fig, nas_fig, security_fig, late_fig


# --------------------------------------------------------------- produccion
# RF9: objeto WSGI que consumira gunicorn. gunicorn IMPORTA este modulo y
# busca una variable llamada `server`; nunca ejecuta el bloque __main__.
server = app.server

if __name__ == "__main__":
    # debug=True recarga el servidor al guardar: comodo en desarrollo,
    # y NUNCA se usa en produccion.
    app.run(debug=True, port=8050)
