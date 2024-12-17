from googleapiclient import discovery
from google.oauth2 import service_account
import pandas as pd
import csv
import time

# Ruta al archivo JSON de la clave de cuenta de servicio
SERVICE_ACCOUNT_FILE = 'perspective.json'

# Cargar las credenciales
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)

# Inicializar el cliente
client = discovery.build(
    "commentanalyzer",
    "v1alpha1",
    credentials=credentials,
    discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
    static_discovery=False,
)

# Leer el archivo CSV de reviews
df = pd.read_csv('trustpilot_reviews.csv', header=None, 
                 names=['fecha', 'puntuacion', 'titulo', 'texto'])

# Crear archivo CSV para resultados
with open('resultados_toxicidad.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['fecha', 'puntuacion', 'titulo', 'texto', 'toxicidad', 'identity_attack', 'insult', 'threat'])

    # Procesar cada review
    for index, row in df.iterrows():
        try:
            # Preparar el texto (título + review)
            texto_completo = f"{row['titulo']} {row['texto']}"

            print(row['titulo'])
            
            # Definir el análisis
            analyze_request = {
                'comment': {'text': texto_completo},
                'requestedAttributes': {
                    'TOXICITY': {},
                    'IDENTITY_ATTACK': {},
                    'INSULT': {},
                    'THREAT': {}
                }
            }

            # Llamar a la API
            response = client.comments().analyze(body=analyze_request).execute()
            
            # Extraer el valor de toxicidad
            toxicidad = response['attributeScores']['TOXICITY']['summaryScore']['value']
            
            # Escribir resultados
            writer.writerow([
                row['fecha'],
                row['puntuacion'],
                row['titulo'],
                row['texto'],
                response['attributeScores']['TOXICITY']['summaryScore']['value'],
                response['attributeScores']['IDENTITY_ATTACK']['summaryScore']['value'],
                response['attributeScores']['INSULT']['summaryScore']['value'],
                response['attributeScores']['THREAT']['summaryScore']['value']
            ])
            
            time.sleep(1)
            
        except Exception as e:
            print(f"Error procesando review {index}: {str(e)}")
            continue

print("Proceso completado. Resultados guardados en 'resultados_toxicidad.csv'")
