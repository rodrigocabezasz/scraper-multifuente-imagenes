# 🚀 Scraper Multi-Fuente de Imágenes

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?style=for-the-badge&logo=mysql)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

Este proyecto es un scraper de datos robusto desarrollado en Python. Su principal función es extraer información e imágenes de múltiples APIs públicas (Bing, Pexels, Unsplash y NASA), procesar los datos, incluyendo la traducción de textos al español, y almacenarlos de forma persistente en una base de datos MySQL.


<!-- ![Demo del Scraper]([https://ruta/a/tu/gif.gif](https://ibb.co/Ps6PmZrM)) -->

---

## 🎯 Características Principales

*   **Extracción Multi-Fuente:** Conexión concurrente a 4 APIs de imágenes distintas.
*   **Procesamiento de Datos:** Limpieza y estructuración de la información obtenida.
*   **Traducción Automática:** Utiliza `deep-translator` para traducir títulos y descripciones al español.
*   **Manejo Robusto de Errores:** Implementa reintentos (`Retry`) en las peticiones HTTP y un sistema de logging detallado para depuración.
*   **Almacenamiento Persistente:** Guarda los datos procesados en una base de datos MySQL, gestionando duplicados.
*   **Gestión de Credenciales Segura:** Carga de claves de API y credenciales de la base de datos desde un archivo `.env` para no exponer información sensible.
*   **Descarga de Archivos:** Descarga las imágenes obtenidas y las almacena localmente.

---

## 🛠️ Stack Tecnológico

*   **Lenguaje:** Python
*   **Bases de Datos:** MySQL
*   **Librerías Principales:**
    *   `requests`: Para realizar las peticiones a las APIs.
    *   `mysql-connector-python`: Para la conexión con la base de datos.
    *   `python-dotenv`: Para la gestión de variables de entorno.
    *   `deep-translator`: Para la traducción de textos.

---

## ⚙️ Configuración y Uso

Para ejecutar este proyecto localmente, sigue estos pasos:

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/tu-usuario/scraper-multifuente-imagenes.git
    cd scraper-multifuente-imagenes
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    python -m venv venv
    # En Windows
    .\venv\Scripts\activate
    # En Mac/Linux
    source venv/bin/activate
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configura las variables de entorno:**
    Crea un archivo `.env` en la raíz del proyecto y añade tus credenciales. Puedes usar el archivo `.env.example` como plantilla (si decides crear uno).
    ```env
    DB_HOST="tu_host"
    DB_USER="tu_usuario"
    DB_PASSWORD="tu_contraseña"
    DB_DATABASE="tu_base_de_datos"
    DB_PORT="tu_puerto"
    PEXELS_API_KEY="tu_clave_de_pexels"
    UNSPLASH_ACCESS_KEY="tu_clave_de_unsplash"
    NASA_API_KEY="tu_clave_de_nasa"
    ```

5.  **Ejecuta el script:**
    ```bash
    python src/main.py
    ```

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.