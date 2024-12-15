from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import json


# Configuración inicial
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    return driver

def ordenar_por_mas_recientes(driver):
    try:
        # Hacer click en el botón de ordenamiento
        sort_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-sort-button='true']"))
        )
        driver.execute_script("arguments[0].click();", sort_button)
        recency_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input#recency"))
        )
        driver.execute_script("arguments[0].click();", recency_option)
        
        # Esperar a que se actualice la página
        time.sleep(3)
        return True
    except Exception as e:
        print(f"Error al ordenar por más recientes: {str(e)}")
        return False

def cargar_ultima_fecha():
    try:
        with open('ultima_fecha.json', 'r') as f:
            data = json.load(f)
            return data.get('ultima_fecha')
    except FileNotFoundError:
        return None

def guardar_ultima_fecha(fecha):
    with open('ultima_fecha.json', 'w') as f:
        json.dump({'ultima_fecha': fecha}, f)

# Función para extraer las reseñas
def scrape_reviews(url, driver, max_pages=None):
    driver.get(url)
    reviews = []
    page = 1
    
    # Cargar la última fecha procesada
    ultima_fecha_procesada = cargar_ultima_fecha()
    
    # Ordenar por más recientes
    if not ordenar_por_mas_recientes(driver):
        print("No se pudo ordenar por más recientes. Continuando con el orden actual...")
    
    while True:
        if max_pages and page > max_pages:
            print(f"Se alcanzó el límite de {max_pages} páginas")
            break
        try:
            print(f"Procesando página {page}...")
            
            # Esperar a que las reseñas carguen
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".styles_reviewContentwrapper__zH_9M"))
            )
            
            # Extraer las reseñas en la página actual
            review_elements = driver.find_elements(By.CSS_SELECTOR, ".styles_reviewContentwrapper__zH_9M")
            
            if not review_elements:
                print("No se encontraron más reseñas")
                break
                
            for review in review_elements:
                fecha_actual = review.find_element(By.CSS_SELECTOR, "time").get_attribute("datetime")
                
                # Si encontramos una reseña ya procesada, terminamos
                if ultima_fecha_procesada and fecha_actual <= ultima_fecha_procesada:
                    print("Se alcanzaron las reseñas ya procesadas")
                    # Guardamos la fecha más reciente antes de salir
                    if reviews:
                        print(f"Guardando última fecha: {reviews[0]['fecha']}")
                        guardar_ultima_fecha(reviews[0]['fecha'])
                    return reviews
                
                review_data = {
                    "fecha": fecha_actual,  
                    "calificacion": "0",
                    "titulo": "Sin título",
                    "contenido": "Sin contenido"
                }

                try:
                    # Fecha
                    review_data["fecha"] = review.find_element(By.CSS_SELECTOR, "time").get_attribute("datetime")
                except:
                    pass

                try:
                    # Calificación
                    review_data["calificacion"] = review.find_element(By.CSS_SELECTOR, "[data-service-review-rating]").get_attribute("data-service-review-rating")
                except:
                    pass

                try:
                    # Título y contenido
                    contenido_completo = review.find_element(By.CSS_SELECTOR, ".styles_reviewContent__0Q2Tg").text
                    partes = contenido_completo.split('\n', 1)
                    
                    if len(partes) > 1:
                        review_data["titulo"] = partes[0]
                        review_data["contenido"] = partes[1]
                    else:
                        review_data["titulo"] = "Sin título"
                        review_data["contenido"] = partes[0]
                    
                    # Limpiar el contenido de la fecha de experiencia
                    if "Fecha de la experiencia:" in review_data["contenido"]:
                        review_data["contenido"] = review_data["contenido"].split("Fecha de la experiencia:")[0].strip()
                except:
                    pass

                reviews.append(review_data)
            
            # Buscar el botón de siguiente página
            try:
                time.sleep(3)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Esperar a que el botón esté presente
                next_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-pagination-button-next-link='true']"))
                )
                
                # Verificar si el botón está deshabilitado
                if 'link_disabled__mIxH1' in next_button.get_attribute('class'):
                    print("Llegamos a la última página")
                    break
                
                # Asegurarnos que el botón sea clickeable
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-pagination-button-next-link='true']"))
                )
                
                # Hacer click
                driver.execute_script("arguments[0].click();", next_button)
                
                # Esperar a que la nueva página cargue
                time.sleep(3)
                page += 1
                
            except Exception as e:
                print(f"Error en la paginación: {str(e)}")
                break
                
        except Exception as e:
            print(f"Error procesando la página {page}: {str(e)}")
            break
    
    print(f"Total de reseñas recopiladas: {len(reviews)}")
    # Guardar la fecha más reciente al finalizar
    if reviews:
        print(f"Guardando última fecha: {reviews[0]['fecha']}")
        guardar_ultima_fecha(reviews[0]['fecha'])
    
    return reviews

# Guardar en CSV
def save_to_csv(reviews, filename="trustpilot_reviews.csv"):
    fieldnames = [
        "fecha",
        "calificacion",
        "titulo",
        "contenido"
    ]
    
    mode = "a" if reviews else "w"  # append si hay nuevas reseñas
    
    with open(filename, mode=mode, newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if mode == "w":  # Solo escribir encabezados si es archivo nuevo
            writer.writeheader()
        writer.writerows(reviews)


if __name__ == "__main__":
    url = "https://es.trustpilot.com/review/seguros.elcorteingles.es"
    driver = setup_driver()
    try:
        reviews = scrape_reviews(url, driver, max_pages=10)
        save_to_csv(reviews)
        print(f"Se han guardado {len(reviews)} reseñas en el archivo 'trustpilot_reviews.csv'")
    finally:
        driver.quit()
