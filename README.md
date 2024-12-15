# Scraper de Reseñas Trustpilot

Este proyecto forma parte de la entrega para la unidad de ETL (Extract, Transform, Load) del Máster en Data Science de la Universidad Europea.

## Descripción

Este es un scraper automatizado diseñado para extraer reseñas de Trustpilot utilizando Selenium WebDriver. El proyecto demuestra la implementación práctica de técnicas de extracción de datos web como parte del proceso ETL.

## Características

- Extrae reseñas de páginas de Trustpilot de forma automatizada
- Guarda las reseñas en formato CSV
- Mantiene un registro de la última fecha procesada para evitar duplicados
- Ordena las reseñas por las más recientes
- Funciona en modo headless (sin interfaz gráfica)

## Requisitos

- Python 3.x
- Chrome WebDriver
- Bibliotecas Python:
  - selenium
  - time
  - csv
  - json

## Instalación

1. Clona este repositorio
2. Instala las dependencias usando el archivo requirements.txt: 

```bash
pip install -r requirements.txt
```

## Uso

1. Modifica la URL en el archivo `scraper.py` según la página de Trustpilot que desees analizar:

```python
url = "https://es.trustpilot.com/review/tu-pagina-aqui"
```

2. Ejecuta el script:

```bash
python scraper.py
```

## Estructura de datos

El scraper extrae la siguiente información de cada reseña:
- Fecha
- Calificación (1-5 estrellas)
- Título de la reseña
- Contenido de la reseña

## Archivos generados

- `trustpilot_reviews.csv`: Archivo CSV que contiene todas las reseñas extraídas con sus respectivos campos
- `ultima_fecha.json`: Archivo que almacena la fecha de la última reseña procesada para evitar duplicados

## Limitaciones

- El script respeta los límites de paginación configurados
- Por defecto, está configurado para procesar hasta 10 páginas
- Incluye delays para evitar sobrecarga del servidor
- Funciona específicamente con la estructura actual de Trustpilot (2024)

## Notas

- El script funciona en modo headless por defecto para mayor eficiencia
- Se recomienda usar de manera responsable y respetando los términos de servicio de Trustpilot
- Es posible que necesites actualizar el ChromeDriver según tu versión de Chrome
