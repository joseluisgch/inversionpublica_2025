import requests
import json
import os
import time
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    filename='data_updater.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Definir carpeta y archivo de salida
DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "inversiones_data.json")

# Asegurar que la carpeta "data" exista
os.makedirs(DATA_FOLDER, exist_ok=True)

def fetch_data():
    """Obtiene los datos del API de ArcGIS y los guarda en un archivo JSON"""
    base_url = 'https://pportalgis.vivienda.gob.pe/pfdserver/rest/services/OGEI/Mapa_Inversiones_MEF/FeatureServer/2/query'
    
    params = {
        'where': "ano_eje = '2025'",
        'outFields': 'tipo_act_proy_nombre,monto_pim,monto_devengado',
        'returnGeometry': 'false',
        'f': 'json',
        'orderByFields': 'fecha_actualizacion'
    }
    
    all_features = []
    record_count = 1000
    offset = 0
    more_records = True
    
    try:
        while more_records:
            params['resultOffset'] = offset
            params['resultRecordCount'] = record_count
            
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()  # Genera un error si la respuesta no es 200
            
            data = response.json()
            if 'error' in data:
                logging.error(f"Error API: {data['error']}")
                return None
            
            features = data.get('features', [])
            all_features.extend(features)
            
            if not data.get('exceededTransferLimit', False) or len(features) == 0:
                more_records = False
            else:
                offset += record_count
                logging.info(f"Obtenidos {len(all_features)} registros hasta ahora...")
                time.sleep(0.2)  # Reducido para mejorar rendimiento
        
        data['features'] = all_features

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        logging.info(f"Datos actualizados correctamente. Total de registros: {len(all_features)}")
        return data
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Error de conexión: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Error al obtener los datos: {str(e)}")
        return None

if __name__ == "__main__":
    fetch_data()
