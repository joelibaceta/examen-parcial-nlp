import requests
from bs4 import BeautifulSoup
import csv
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import demoji
import sys
import time
import os
import pandas as pd


class Peru21Scrapper:
    def __init__(self, max_workers=20, verbose=True, max_retries=3, retry_delay=5):
        self.base_url = "https://peru21.pe"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.max_workers = max_workers
        self.write_lock = Lock()
        self.verbose = verbose
        self.is_jupyter = self._is_jupyter()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def _is_jupyter(self):
        """Detecta si el código se está ejecutando en Jupyter"""
        try:
            from IPython import get_ipython
            return get_ipython() is not None
        except:
            return False
    
    def _print_progress(self, message, overwrite=False):
        """Imprime mensajes según el contexto (Jupyter o terminal)"""
        if not self.verbose:
            return
        
        if self.is_jupyter and overwrite:
            try:
                from IPython.display import clear_output
                clear_output(wait=True)
                print(message)
            except:
                print(message)
        else:
            print(message)
    
    def clean_text(self, text):
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', '', text)
        text = demoji.replace(text, '')
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _retry_request(self, func, *args, **kwargs):
        """
        Intenta ejecutar una función con reintentos y espera exponencial
        """
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    self._print_progress(f"⚠️  Error de conexión (intento {attempt + 1}/{self.max_retries}). Esperando {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    self._print_progress(f"❌ Error después de {self.max_retries} intentos: {str(e)}")
                    raise
            except Exception as e:
                self._print_progress(f"❌ Error inesperado: {str(e)}")
                raise
        return None
    
    def _get_last_date_from_file(self, output_file):
        """
        Lee el archivo TSV y obtiene la fecha más reciente
        Retorna datetime object o None si no hay datos
        """
        if not os.path.exists(output_file):
            return None
        
        try:
            # Leer solo la primera línea de datos (después del header)
            df = pd.read_csv(
                output_file,
                sep='\t',
                encoding='utf-8',
                nrows=1,
                parse_dates=['fecha']
            )
            
            if len(df) == 0:
                return None
            
            # Obtener la fecha más reciente
            last_date_str = str(df['fecha'].iloc[0])
            
            # Parsear la fecha (puede venir en varios formatos)
            try:
                last_date = datetime.strptime(last_date_str.split()[0], '%Y-%m-%d')
            except:
                # Si falla, intentar con el formato completo
                last_date = pd.to_datetime(last_date_str).to_pydatetime()
            
            self._print_progress(f"📅 Última noticia encontrada: {last_date.strftime('%Y-%m-%d')}")
            return last_date
        except Exception as e:
            self._print_progress(f"⚠️  No se pudo leer la última fecha del archivo: {str(e)}")
            return None
    
    def get_news_list(self, date):
        """
        Obtiene todas las noticias de una fecha, incluyendo paginación
        Con reintentos automáticos en caso de error de conexión
        """
        all_news = []
        page = 1
        
        while True:
            if page == 1:
                url = f"{self.base_url}/archivo/todas/{date.strftime('%Y-%m-%d')}/"
            else:
                url = f"{self.base_url}/archivo/todas/{date.strftime('%Y-%m-%d')}/{page}/"
            
            try:
                def fetch_page():
                    response = self.session.get(url, timeout=10)
                    response.raise_for_status()
                    return response
                
                response = self._retry_request(fetch_page)
                if response is None:
                    return None if page == 1 else all_news
                
                soup = BeautifulSoup(response.content, 'lxml')
                
                # Buscar artículos
                articles = soup.find_all('article', {'data-history-node-id': True})
                
                if not articles:
                    break
                
                for article in articles:
                    # Extraer URL
                    link_element = article.find('a', href=True)
                    if not link_element:
                        continue
                    
                    article_url = urljoin(self.base_url, str(link_element['href']))
                    
                    # Extraer título
                    title_element = article.find('h2')
                    if not title_element:
                        continue
                    
                    title = self.clean_text(title_element.get_text())
                    
                    # Extraer sección
                    section_element = article.find('div', class_='field--name-field-seccion')
                    if section_element:
                        section_link = section_element.find('a')
                        section = self.clean_text(section_link.get_text()) if section_link else "General"
                    else:
                        section = "General"
                    
                    # Extraer fecha (aunque ya la tenemos)
                    fecha_element = article.find('div', class_='field--name-field-fecha-actualizacion')
                    if fecha_element:
                        fecha_text = fecha_element.get_text().strip()
                        # Formato: "2025-11-01 12:08"
                        fecha = fecha_text.split()[0] if fecha_text else date.strftime('%Y-%m-%d')
                    else:
                        fecha = date.strftime('%Y-%m-%d')
                    
                    if title and article_url:
                        all_news.append({
                            'fecha': fecha,
                            'seccion': section,
                            'titular': title,
                            'url': article_url
                        })
                
                # Verificar si hay página siguiente
                next_page = soup.find('a', {'rel': 'next'})
                if not next_page:
                    break
                
                page += 1
                
            except requests.exceptions.RequestException:
                return None if page == 1 else all_news
            except Exception:
                break
        
        return all_news
    
    def get_article_content(self, url):
        """
        Extrae el contenido completo de un artículo con reintentos
        """
        def fetch_content():
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Buscar el contenido en el campo body
            content_div = soup.find('div', class_='field--name-body')
            
            if content_div:
                # Remover scripts, estilos y artículos embebidos
                for unwanted in content_div(['script', 'style', 'article']):
                    unwanted.decompose()
                
                # Obtener todo el texto
                content = self.clean_text(content_div.get_text())
                return content
            
            return ""
        
        try:
            return self._retry_request(fetch_content)
        except Exception:
            return ""
    
    def process_article(self, news, output_file):
        content = self.get_article_content(news['url'])
        if content:
            with self.write_lock:
                with open(output_file, 'a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file, delimiter='\t')
                    writer.writerow([news['fecha'], news['titular'], content, news['seccion'], news['url']])
        return bool(content)
    
    def extract_historical(self, start_date=None, output_file='noticias_peru21.tsv', max_empty_attempts=10, resume=True):
        """
        Extrae noticias históricas desde start_date hacia atrás
        
        Args:
            start_date: Fecha de inicio (si None, usa fecha actual)
            output_file: Archivo de salida
            max_empty_attempts: Intentos máximos consecutivos sin encontrar noticias
            resume: Si True, intenta continuar desde la última fecha en el archivo
        """
        # Verificar si debemos reanudar desde un archivo existente
        if resume and os.path.exists(output_file):
            last_date = self._get_last_date_from_file(output_file)
            if last_date:
                # Continuar desde un día antes de la última fecha
                start_date = last_date - timedelta(days=1)
                self._print_progress(f"🔄 Reanudando desde: {start_date.strftime('%Y-%m-%d')}")
                mode = 'a'  # Modo append
            else:
                if start_date is None:
                    start_date = datetime.now()
                mode = 'w'  # Modo escritura
        else:
            if start_date is None:
                start_date = datetime.now()
            mode = 'w'
        
        current_date = start_date
        empty_attempts = 0
        total_news = 0
        days_processed = 0
        
        # Escribir header solo si es archivo nuevo
        if mode == 'w':
            with open(output_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter='\t')
                writer.writerow(['fecha', 'titular', 'contenido', 'seccion', 'url'])
        
        self._print_progress(f"🚀 Iniciando scraping desde {current_date.strftime('%Y-%m-%d')}...")
        
        while empty_attempts < max_empty_attempts:
            date_str = current_date.strftime('%Y-%m-%d')
            
            try:
                news_list = self.get_news_list(current_date)
                
                if news_list is None:
                    self._print_progress(f"⚠️  Error de conexión para fecha {date_str}. Total hasta ahora: {total_news} noticias")
                    # Esperar antes de continuar
                    time.sleep(self.retry_delay)
                    continue
                
                if not news_list:
                    empty_attempts += 1
                    if empty_attempts >= max_empty_attempts:
                        self._print_progress(f"🏁 Finalizando. No hay más noticias disponibles.", overwrite=True)
                else:
                    empty_attempts = 0
                    successful = 0
                    with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                        futures = {executor.submit(self.process_article, news, output_file): news for news in news_list}
                        for future in as_completed(futures):
                            if future.result():
                                successful += 1
                                total_news += 1
                                self._print_progress(f"📰 Descargadas: {total_news} noticias | Fecha actual: {date_str}", overwrite=True)
                
                days_processed += 1
                current_date -= timedelta(days=1)
                
            except KeyboardInterrupt:
                self._print_progress(f"\n⏸️  Proceso interrumpido por el usuario. Total: {total_news} noticias guardadas")
                self._print_progress(f"💾 Puedes reanudar ejecutando el script nuevamente (automáticamente continuará desde la última fecha)")
                break
            except Exception as e:
                self._print_progress(f"❌ Error inesperado en fecha {date_str}: {str(e)}")
                time.sleep(self.retry_delay)
                continue
        
        self._print_progress(f"\n✅ Proceso completado: {total_news} noticias guardadas en {days_processed} días", overwrite=False)
    
    def extract(self, date, output_file='noticias_peru21.tsv'):
        news_list = self.get_news_list(date)
        
        if news_list is None or not news_list:
            self._print_progress("⚠️  No se encontraron noticias para esta fecha")
            return

        with open(output_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow(['fecha', 'titular', 'contenido', 'seccion', 'url'])
        
        successful = 0
        total = len(news_list)
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.process_article, news, output_file): news for news in news_list}
            for future in as_completed(futures):
                if future.result():
                    successful += 1
                    self._print_progress(f"📰 Procesando: {successful}/{total} noticias", overwrite=True)
        
        self._print_progress(f"\n✅ Completado: {successful}/{total} noticias guardadas", overwrite=False)

def main():
    """
    Función principal que inicia el scraper
    """
    scraper = Peru21Scrapper(
        max_workers=20,         # Hilos paralelos
        verbose=True,           # Mostrar progreso
        max_retries=3,          # Reintentos por request
        retry_delay=5           # Segundos de espera base
    )
    
    scraper.extract_historical(
        start_date=None,        # None = hoy, o especifica datetime(2025, 1, 1)
        output_file='noticias_peru21.tsv',
        max_empty_attempts=10,  # Días consecutivos sin noticias antes de parar
        resume=True             # True = continuar desde última fecha si existe archivo
    )

if __name__ == "__main__":
    main()
