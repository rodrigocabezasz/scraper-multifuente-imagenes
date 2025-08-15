# src/main.py
from typing import List, Dict, Any
import requests
import mysql.connector
import os
from datetime import datetime, date
from urllib.parse import urljoin, quote
import time
import logging
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from deep_translator import GoogleTranslator

# --- 1. CONFIGURACIÓN ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log', mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

session = requests.Session()
retry = Retry(connect=5, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount('https://', adapter)
session.mount('http://', adapter)

load_dotenv()

DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_DATABASE"),
    'port': os.getenv("DB_PORT")
    }

# --- AJUSTE DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(os.path.dirname(BASE_DIR), "data", "images")
os.makedirs(IMAGE_DIR, exist_ok=True)

BING_API_URL = "https://www.bing.com/HPImageArchive.aspx"
PEXELS_API_URL = "https://api.pexels.com/v1"
UNSPLASH_API_URL = "https://api.unsplash.com"
NASA_APOD_URL = "https://api.nasa.gov/planetary/apod"

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
UNSPLASH_API_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
NASA_API_KEY = os.getenv("NASA_API_KEY")

PEXELS_HEADERS = {'Authorization': PEXELS_API_KEY}
UNSPLASH_HEADERS = {'Authorization': f'Client-ID {UNSPLASH_API_KEY}'}

# --- FUNCIÓN DE TRADUCCIÓN ---
def translate_text(text: str, source: str = 'auto', target: str = 'es') -> str:
    if not text or not isinstance(text, str):
        return text
    try:
        time.sleep(0.1)  # Pausa para no saturar la API de traducción
        return GoogleTranslator(source=source, target=target).translate(text)
    except Exception as e:
        logger.warning(f"Error de traducción para el texto '{text[:30]}...': {e}")
        return text

# --- FUNCIONES DE OBTENCIÓN DE DATOS ---
def get_photos_from_bing() -> List[Dict[str, Any]]:
    photos = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        params = {'format': 'js', 'idx': 0, 'n': 8, 'mkt': 'en-US'}
        response = session.get(BING_API_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        for image in data.get('images', []):
            title = image.get('title', '')
            photos.append({'url': f"https://www.bing.com/search?q={quote(title)}", 'image_url': f"https://www.bing.com{image['url']}", 'titulo': title, 'descripcion': image.get('copyright', ''), 'categoria': 'Paisaje', 'autor': 'Bing', 'fuente': 'Bing', 'tags': 'paisaje,naturaleza,fotografía del día', 'date': datetime.now().strftime('%Y-%m-%d'), 'width': 1920, 'height': 1080, 'color_dominante': '#000000'})
    except Exception as e:
        logger.error(f"Error fetching Bing photos: {e}")
    return photos

def get_photos_from_pexels() -> List[Dict[str, Any]]:
    photos = []
    queries = ['parking', 'garage', 'cars', 'urban', 'city']
    try:
        for query in queries:
            params = {'query': query, 'per_page': 5}
            response = session.get(f"{PEXELS_API_URL}/search", headers=PEXELS_HEADERS, params=params)
            response.raise_for_status()
            data = response.json()
            for photo in data.get('photos', []):
                photos.append({'url': photo['url'], 'image_url': photo['src']['original'], 'titulo': photo.get('alt') or f"Fotografía de {query}", 'descripcion': f"Fotografía de {query} por {photo['photographer']}", 'categoria': query.title(), 'autor': photo['photographer'], 'fuente': 'Pexels', 'tags': f"{query},fotografía", 'date': datetime.now().strftime('%Y-%m-%d'), 'width': photo['width'], 'height': photo['height'], 'color_dominante': photo.get('avg_color', '#000000')})
    except Exception as e:
        logger.error(f"Error fetching Pexels photos: {e}")
    return photos

def get_photos_from_unsplash() -> List[Dict[str, Any]]:
    photos = []
    queries = ['nature', 'landscape', 'wildlife', 'astronomy']
    try:
        for query in queries:
            params = {'query': query, 'per_page': 5}
            response = session.get(f"{UNSPLASH_API_URL}/search/photos", headers=UNSPLASH_HEADERS, params=params)
            response.raise_for_status()
            data = response.json()
            for photo in data.get('results', []):
                photos.append({'url': photo['links']['html'], 'image_url': photo['urls']['full'], 'titulo': photo.get('alt_description') or f"Fotografía de {query}", 'descripcion': photo.get('description') or f"Fotografía de {query} por {photo['user']['name']}", 'categoria': query.title(), 'autor': photo['user']['name'], 'fuente': 'Unsplash', 'tags': ','.join([tag['title'] for tag in photo.get('tags', [])]) or query, 'date': datetime.now().strftime('%Y-%m-%d'), 'width': photo['width'], 'height': photo['height'], 'color_dominante': photo.get('color', '#000000')})
    except Exception as e:
        logger.error(f"Error fetching Unsplash photos: {e}")
    return photos

def get_photos_from_nasa() -> List[Dict[str, Any]]:
    photos = []
    try:
        params = {'api_key': NASA_API_KEY, 'count': 10}
        response = session.get(NASA_APOD_URL, params=params)
        response.raise_for_status()
        data = response.json()
        for item in data:
            if item.get('media_type') == 'image':
                photos.append({'url': item.get('hdurl', item['url']), 'image_url': item.get('hdurl', item['url']), 'titulo': item['title'], 'descripcion': item['explanation'], 'categoria': 'Astronomía', 'autor': item.get('copyright', 'NASA'), 'fuente': 'NASA', 'tags': 'astronomía,espacio,ciencia,nasa', 'date': item.get('date', datetime.now().strftime('%Y-%m-%d')), 'width': 2000, 'height': 1500, 'color_dominante': '#000000'})
    except Exception as e:
        logger.error(f"Error fetching NASA photos: {e}")
    return photos

# --- FUNCIÓN DE DESCARGA ---
def download_image(url, filepath):
    try:
        response = session.get(url, stream=True, timeout=30)
        response.raise_for_status()
        content_type = response.headers.get('content-type', '')
        if 'image' not in content_type:
            logger.warning(f"URL no es una imagen: {url} (tipo: {content_type})")
            return False
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        logger.error(f"Error al descargar imagen {url}: {e}")
        return False

# --- FUNCIÓN DE GUARDADO EN BD ---
def save_photos_to_db(photos: List[Dict[str, Any]]) -> None:
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        processed_count = 0
        for i, photo in enumerate(photos):
            try:
                original_title = photo.get('titulo', 'Sin título')
                logger.info(f"Procesando [{i + 1}/{len(photos)}]: {original_title[:60]}")
                titulo_es = translate_text(original_title)
                descripcion_es = translate_text(photo.get('descripcion', ''))
                date_str = photo.get('date', datetime.now().strftime('%Y-%m-%d'))
                filename_base = f"{photo.get('fuente', 'unknown')}_{date_str}_{i}"
                image_filename = f"{filename_base}.jpg"
                image_filepath = os.path.join(IMAGE_DIR, image_filename)
                if download_image(photo['image_url'], image_filepath):
                    path_imagen_db = image_filename
                else:
                    logger.warning(f"No se pudo descargar la imagen. Saltando registro.")
                    continue
                sql = """INSERT INTO RECURSOS_DIARIOS (fecha, titulo, titulo_display, descripcion, categoria, autor, fuente, tags, url_fuente, path_imagen, width, height, color_dominante) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE descripcion=VALUES(descripcion), path_imagen=VALUES(path_imagen);"""
                values = (date_str, titulo_es, titulo_es[:200], descripcion_es, photo.get('categoria', 'General'), photo.get('autor', 'Desconocido'), photo.get('fuente', 'N/A'), photo.get('tags', ''), photo.get('url', ''), path_imagen_db, photo.get('width', 0), photo.get('height', 0), photo.get('color_dominante', '#000000'))
                cursor.execute(sql, values)
                processed_count += 1
            except Exception as e:
                logger.error(f"Error procesando una foto: {original_title}. Error: {e}")
                connection.rollback()
                continue
        connection.commit()
        cursor.close()
        connection.close()
        logger.info(f"\nProceso de guardado finalizado. Total de fotos guardadas: {processed_count}")
    except mysql.connector.Error as err:
        logger.error(f"Error de base de datos en save_photos_to_db: {err}")

# --- FUNCIÓN PRINCIPAL ---
def main():
    logger.info("=== INICIO DEL SCRAPER MULTI-FUENTE CON TRADUCCIÓN ===")
    try:
        logger.info("Limpiando registros antiguos y archivos de imágenes...")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute("TRUNCATE TABLE RECURSOS_DIARIOS;")
        connection.commit()
        cursor.close()
        connection.close()
        logger.info("Tabla RECURSOS_DIARIOS vaciada exitosamente.")
        for filename in os.listdir(IMAGE_DIR):
            file_path = os.path.join(IMAGE_DIR, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        logger.info("Carpeta de recursos de imágenes vaciada exitosamente.")
    except Exception as err:
        logger.error(f"No se pudo limpiar el entorno: {err}. Saliendo del script.")
        return
    all_photos = []
    photo_sources = [('Bing', get_photos_from_bing), ('Pexels', get_photos_from_pexels), ('Unsplash', get_photos_from_unsplash), ('NASA', get_photos_from_nasa)]
    for source_name, get_photos_func in photo_sources:
        try:
            logger.info(f"\nObteniendo fotos de {source_name}...")
            photos = get_photos_func()
            if photos:
                all_photos.extend(photos)
                logger.info(f"Se obtuvieron {len(photos)} fotos de {source_name}")
            else:
                logger.warning(f"No se obtuvieron fotos de {source_name}")
        except Exception as e:
            logger.error(f"Error crítico obteniendo fotos de {source_name}: {e}")
            continue
    if all_photos:
        save_photos_to_db(all_photos)
    else:
        logger.warning("No se obtuvieron fotos de ninguna fuente.")

if __name__ == "__main__":
    main()