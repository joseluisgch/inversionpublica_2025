import pandas as pd
import plotly.express as px
import plotly.io as pio
import json
import os
from datetime import datetime
import pytz

# Ruta donde se guardará el gráfico y los datos
OUTPUT_FOLDER = "docs" # se guarda los graficos en carpeta docs
DATA_FILE = os.path.join("data", "inversiones_data.json") # Se actualizará desde GitHub Actions

# Asegurar que el directorio de salida existe
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Leer los datos
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Obtener fecha de actualización
utc_time = datetime.fromtimestamp(os.path.getmtime(DATA_FILE), tz=pytz.UTC)
peru_timezone = pytz.timezone('America/Lima')
peru_time = utc_time.astimezone(peru_timezone)
last_update = peru_time.strftime('%d/%m/%Y %H:%M:%S')

# Procesar los datos
if 'features' in data and data['features']:
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

    # Generar el gráfico con colores personalizados
    fig = px.bar(
        grouped,
        y='tipo_act_proy_nombre',
        x=['monto_pim', 'monto_devengado'],
        orientation='h',
        title=f'Montos PIM y Devengado (2025) - Actualizado: {last_update}',
        text_auto=True,
        color_discrete_map={"monto_pim": "#1f77b4", "monto_devengado": "#ff7f0e"}
    )

    # Personalizar títulos de ejes
    fig.update_layout(
        xaxis_title="Monto en soles",
        yaxis_title="Tipo de Actividad o Proyecto"
    )

    # Guardar el gráfico como HTML
    chart_path = os.path.join(OUTPUT_FOLDER, "index.html")
    pio.write_html(fig, chart_path)

    print(f"Gráfico guardado en: {chart_path}")

else:
    print("No se encontraron datos para generar el gráfico.")
