import pandas as pd
import plotly.express as px
import plotly.io as pio
from flask import Flask, render_template
import json
import os
from datetime import datetime
import pytz

app = Flask(__name__)

# Ruta al archivo de datos
DATA_FILE = 'data\inversiones_data.json'  # Cambiar para GitHub

@app.route('/')
def index():
    if not os.path.exists(DATA_FILE):
        return "Error: No se encontró el archivo de datos. Ejecuta el actualizador primero."

    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        utc_time = datetime.fromtimestamp(os.path.getmtime(DATA_FILE), tz=pytz.UTC)
        peru_timezone = pytz.timezone('America/Lima')
        peru_time = utc_time.astimezone(peru_timezone)
        last_update = peru_time.strftime('%d/%m/%Y %H:%M:%S')

    except Exception as e:
        return f"Error al leer el archivo de datos: {str(e)}"

    if 'features' not in data or not data['features']:
        plot_html = 'No se encontraron datos para el año 2025.'
    else:
        records = [
            {
                'tipo_act_proy_nombre': feature['attributes']['tipo_act_proy_nombre'],
                'monto_pim': feature['attributes']['monto_pim'] or 0,
                'monto_devengado': feature['attributes']['monto_devengado'] or 0
            }
            for feature in data['features']
        ]
        df = pd.DataFrame(records)
        grouped = df.groupby('tipo_act_proy_nombre').sum().reset_index()
        grouped = grouped.sort_values(by="monto_pim", ascending=True)

        fig = px.bar(
            grouped,
            y='tipo_act_proy_nombre',
            x=['monto_pim', 'monto_devengado'],
            orientation='h',
            title=f'Montos PIM y Devengado (2025) - Actualizado: {last_update}',
            text_auto=True,
            labels={
                "value": "Monto en soles (S/.)",
                "tipo_act_proy_nombre": "Tipo de Actividad o Proyecto",
                "variable": "Tipo de Monto"
            },
            color_discrete_map={
                "monto_pim": "#1f77b4",
                "monto_devengado": "#ff7f0e"
            }
        )

        plot_html = pio.to_html(fig, full_html=False)

    return render_template('index.html', plot=plot_html)

if __name__ == '__main__':
    app.run(debug=True)
