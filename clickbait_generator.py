"""
Generador de dataset de clickbaits usando Ollama
Optimizado para uso en notebooks de TensorFlow/Keras
"""

import pandas as pd
import requests
import time
import os
from typing import Optional, List, Tuple
from tqdm import tqdm


class ClickbaitGenerator:
    """Generador de clickbaits usando Ollama API"""
    
    def __init__(self, model_name: str = "llama3.2:3b", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        
    def generate_single_clickbait(self, titulo: str, max_retries: int = 3) -> Optional[str]:
        """
        Genera versión clickbait de un titular usando Ollama
        
        Args:
            titulo: Titular original
            max_retries: Número máximo de reintentos
            
        Returns:
            Titular clickbait o None si falla
        """
        prompt = f"""Convierte este titular de noticia en un clickbait en español.
El clickbait debe:
- Ser sensacionalista y crear curiosidad
- Usar números cuando sea posible
- No revelar toda la información
- Usar palabras emocionales
- Ser corto (máximo 100 caracteres)

Titular original: {titulo}

Responde SOLO con el titular clickbait, sin explicaciones."""
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    json={
                        'model': self.model_name,
                        'prompt': prompt,
                        'stream': False,
                        'options': {
                            'temperature': 0.8,
                            'top_p': 0.9
                        }
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    clickbait = result['response'].strip()
                    # Limpiar posibles comillas o prefijos
                    clickbait = clickbait.strip('"\'\'').strip()
                    if len(clickbait) > 0 and len(clickbait) < 200:
                        return clickbait
            
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    print(f"❌ Error generando clickbait: {e}")
                    return None
        
        return None
    
    def generate_dataset(self, 
                        df: pd.DataFrame, 
                        titulo_col: str = 'titulo',
                        output_file: str = 'dataset_clickbaits.csv',
                        max_samples: Optional[int] = None,
                        save_every: int = 10) -> pd.DataFrame:
        """
        Genera dataset de clickbaits desde un DataFrame
        
        Args:
            df: DataFrame con titulares originales
            titulo_col: Nombre de la columna con titulares
            output_file: Archivo donde guardar resultados
            max_samples: Máximo número de muestras a procesar
            save_every: Guardar cada N muestras
            
        Returns:
            DataFrame con pares (titular_original, clickbait)
        """
        if max_samples:
            df_sample = df.sample(n=min(max_samples, len(df))).reset_index(drop=True)
        else:
            df_sample = df.copy()
        
        results = []
        file_exists = os.path.exists(output_file)
        
        print(f"🚀 Generando clickbaits para {len(df_sample)} titulares...")
        print(f"💾 Guardando en: {output_file}")
        
        try:
            for idx, row in tqdm(df_sample.iterrows(), total=len(df_sample), desc="Generando clickbaits"):
                titulo_original = row[titulo_col]
                
                if not titulo_original or pd.isna(titulo_original):
                    continue
                
                # Generar clickbait
                clickbait = self.generate_single_clickbait(titulo_original)
                
                if clickbait:
                    result_row = {
                        'titular_original': titulo_original,
                        'clickbait': clickbait
                    }
                    results.append(result_row)
                    
                    # Guardar progresivamente
                    if len(results) % save_every == 0:
                        self._save_results(results, output_file, file_exists)
                        file_exists = True
                        print(f"✅ Progreso: {len(results)}/{len(df_sample)} guardado")
            
            # Guardar resultados finales
            if results:
                self._save_results(results, output_file, file_exists)
                print(f"🎉 Completado: {len(results)} clickbaits generados")
            
        except KeyboardInterrupt:
            print(f"\n⚠️ Interrumpido por usuario. Guardando {len(results)} clickbaits generados...")
            if results:
                self._save_results(results, output_file, file_exists)
        
        return pd.DataFrame(results)
    
    def _save_results(self, results: List[dict], output_file: str, file_exists: bool):
        """Guarda resultados en CSV de forma incremental"""
        df_results = pd.DataFrame(results)
        
        if file_exists:
            # Append mode - sin headers
            df_results.to_csv(output_file, mode='a', header=False, index=False, encoding='utf-8')
        else:
            # Write mode - con headers
            df_results.to_csv(output_file, mode='w', header=True, index=False, encoding='utf-8')
    
    def test_connection(self) -> bool:
        """Prueba la conexión con Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [m['name'] for m in models]
                
                if self.model_name in available_models:
                    print(f"✅ Conectado a Ollama - Modelo {self.model_name} disponible")
                    return True
                else:
                    print(f"⚠️ Modelo {self.model_name} no encontrado")
                    print(f"Modelos disponibles: {available_models}")
                    return False
            else:
                print(f"❌ Error conectando a Ollama: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ No se puede conectar a Ollama: {e}")
            print("Asegúrate de que Ollama esté corriendo en http://localhost:11434")
            return False


# Funciones de conveniencia para notebooks
def quick_generate_clickbaits(df: pd.DataFrame, 
                             max_samples: int = 100,
                             titulo_col: str = 'titulo',
                             output_file: str = 'dataset_clickbaits.csv') -> pd.DataFrame:
    """
    Función rápida para generar clickbaits desde un notebook
    
    Args:
        df: DataFrame con titulares
        max_samples: Máximo número de muestras
        titulo_col: Columna con titulares
        output_file: Archivo de salida
        
    Returns:
        DataFrame con clickbaits generados
    """
    generator = ClickbaitGenerator()
    
    # Probar conexión
    if not generator.test_connection():
        print("❌ No se puede continuar sin conexión a Ollama")
        return pd.DataFrame()
    
    # Generar dataset
    return generator.generate_dataset(
        df=df,
        titulo_col=titulo_col,
        output_file=output_file,
        max_samples=max_samples,
        save_every=5  # Guardar cada 5 para notebooks
    )


def load_dataset_for_training(csv_file: str = 'dataset_clickbaits.csv') -> Tuple[List[str], List[str]]:
    """
    Carga el dataset generado y lo prepara para entrenamiento con TensorFlow
    
    Args:
        csv_file: Archivo CSV con el dataset
        
    Returns:
        Tupla (titulares_originales, clickbaits) como listas
    """
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')
        
        # Limpiar datos vacíos
        df = df.dropna()
        df = df[df['titular_original'].str.len() > 0]
        df = df[df['clickbait'].str.len() > 0]
        
        print(f"📊 Dataset cargado: {len(df)} pares (titular, clickbait)")
        
        return df['titular_original'].tolist(), df['clickbait'].tolist()
        
    except FileNotFoundError:
        print(f"❌ Archivo {csv_file} no encontrado")
        return [], []
    except Exception as e:
        print(f"❌ Error cargando dataset: {e}")
        return [], []


if __name__ == "__main__":
    # Ejemplo de uso
    print("🔧 Clickbait Generator - Ejemplo de uso")
    
    # Probar conexión
    generator = ClickbaitGenerator()
    generator.test_connection()
    
    # Ejemplo con un titular
    titulo_test = "El presidente anunció nuevas medidas económicas para el próximo año"
    clickbait = generator.generate_single_clickbait(titulo_test)
    
    if clickbait:
        print(f"\n📰 Original: {titulo_test}")
        print(f"🎯 Clickbait: {clickbait}")
    else:
        print("❌ No se pudo generar clickbait de prueba")