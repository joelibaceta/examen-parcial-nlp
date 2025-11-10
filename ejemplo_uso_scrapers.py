#!/usr/bin/env python3
"""
Ejemplo de uso de los scrapers mejorados con resiliencia
"""

from scrapper import NewsScrapper
from scrapper_peru21 import Peru21Scrapper
from datetime import datetime

def ejemplo_basico():
    """Uso básico con reanudación automática"""
    print("=" * 60)
    print("EJEMPLO 1: Uso Básico con Reanudación Automática")
    print("=" * 60)
    
    # Diario Correo
    print("\n🔹 Scraper de Diario Correo:")
    scraper_correo = NewsScrapper()
    scraper_correo.extract_historical(
        output_file='noticias.tsv',
        resume=True  # Continúa automáticamente si existe el archivo
    )
    
    # Peru21
    print("\n🔹 Scraper de Peru21:")
    scraper_peru21 = Peru21Scrapper()
    scraper_peru21.extract_historical(
        output_file='noticias_peru21.tsv',
        resume=True
    )

def ejemplo_personalizado():
    """Configuración personalizada con más reintentos"""
    print("=" * 60)
    print("EJEMPLO 2: Configuración Personalizada")
    print("=" * 60)
    
    # Configuración robusta para conexiones lentas
    scraper = Peru21Scrapper(
        max_workers=15,         # Menos hilos para conexión lenta
        verbose=True,           
        max_retries=5,          # Más reintentos
        retry_delay=10          # Mayor espera entre reintentos
    )
    
    scraper.extract_historical(
        output_file='noticias_peru21.tsv',
        max_empty_attempts=15,  # Más intentos antes de parar
        resume=True
    )

def ejemplo_fecha_especifica():
    """Comenzar desde una fecha específica"""
    print("=" * 60)
    print("EJEMPLO 3: Desde Fecha Específica")
    print("=" * 60)
    
    scraper = NewsScrapper()
    
    # Comenzar desde el 1 de enero de 2025
    scraper.extract_historical(
        start_date=datetime(2025, 1, 1),
        output_file='noticias_enero_2025.tsv',
        resume=False  # No reanudar, comenzar de cero
    )

def ejemplo_sin_reanudacion():
    """Forzar inicio desde cero (sobrescribe archivo existente)"""
    print("=" * 60)
    print("EJEMPLO 4: Sin Reanudación (Sobrescribir)")
    print("=" * 60)
    
    scraper = Peru21Scrapper()
    scraper.extract_historical(
        output_file='noticias_peru21.tsv',
        resume=False  # Comenzar desde cero, ignorar archivo existente
    )

def ejemplo_paralelo():
    """Ejecutar ambos scrapers (ejemplo conceptual)"""
    print("=" * 60)
    print("EJEMPLO 5: Ambos Scrapers")
    print("=" * 60)
    print("Nota: Para ejecución realmente paralela, usar multiprocessing")
    
    # Diario Correo
    print("\n📰 Descargando de Diario Correo...")
    scraper1 = NewsScrapper(max_workers=10, max_retries=3)
    scraper1.extract_historical(
        output_file='noticias.tsv',
        resume=True
    )
    
    # Peru21
    print("\n📰 Descargando de Peru21...")
    scraper2 = Peru21Scrapper(max_workers=20, max_retries=3)
    scraper2.extract_historical(
        output_file='noticias_peru21.tsv',
        resume=True
    )

def verificar_progreso():
    """Verificar el progreso actual de los archivos"""
    import pandas as pd
    import os
    
    print("=" * 60)
    print("VERIFICACIÓN DE PROGRESO")
    print("=" * 60)
    
    archivos = ['noticias.tsv', 'noticias_peru21.tsv']
    
    for archivo in archivos:
        if os.path.exists(archivo):
            try:
                df = pd.read_csv(archivo, sep='\t', encoding='utf-8')
                print(f"\n📊 {archivo}:")
                print(f"   Total de noticias: {len(df)}")
                print(f"   Última fecha: {df['fecha'].iloc[0]}")
                print(f"   Primera fecha: {df['fecha'].iloc[-1]}")
                print(f"   Secciones: {df['seccion'].nunique()}")
            except Exception as e:
                print(f"\n⚠️  Error al leer {archivo}: {str(e)}")
        else:
            print(f"\n❌ {archivo}: No existe")

if __name__ == "__main__":
    import sys
    
    print("""
╔═══════════════════════════════════════════════════════════╗
║         EJEMPLOS DE USO - SCRAPERS DE NOTICIAS           ║
║                   (Versión Resiliente)                    ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    print("\nOpciones disponibles:")
    print("  1. Uso básico con reanudación automática")
    print("  2. Configuración personalizada (más reintentos)")
    print("  3. Desde fecha específica")
    print("  4. Sin reanudación (comenzar de cero)")
    print("  5. Ambos scrapers secuencialmente")
    print("  6. Verificar progreso actual")
    print("  0. Ejecutar ejemplo básico por defecto")
    
    try:
        opcion = input("\nSelecciona una opción (0-6): ").strip()
        
        if opcion == "1" or opcion == "0" or opcion == "":
            ejemplo_basico()
        elif opcion == "2":
            ejemplo_personalizado()
        elif opcion == "3":
            ejemplo_fecha_especifica()
        elif opcion == "4":
            ejemplo_sin_reanudacion()
        elif opcion == "5":
            ejemplo_paralelo()
        elif opcion == "6":
            verificar_progreso()
        else:
            print("❌ Opción no válida")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏸️  Proceso interrumpido por el usuario")
        print("💡 Tip: Puedes reanudar ejecutando el script nuevamente")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
