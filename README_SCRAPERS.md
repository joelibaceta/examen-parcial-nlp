# 📰 Scrapers de Noticias - Documentación

## 🎯 Mejoras Implementadas

### 1. **Resiliencia ante Errores de Conexión**
- ✅ Sistema de **reintentos automáticos** con espera exponencial
- ✅ Configuración de `max_retries` (por defecto: 3 intentos)
- ✅ Espera exponencial: 5s → 10s → 20s
- ✅ No se detiene ante fallos temporales de red

### 2. **Reanudación Automática**
- ✅ **Detecta automáticamente** si ya existe un archivo TSV
- ✅ **Lee la última fecha** procesada del archivo
- ✅ **Continúa desde un día anterior** a la última fecha
- ✅ **Modo append** para no perder datos previos

### 3. **Manejo de Interrupciones**
- ✅ Captura `Ctrl+C` (KeyboardInterrupt)
- ✅ Guarda el progreso actual antes de salir
- ✅ Permite reanudar en la próxima ejecución

## 🚀 Uso

### Scraper de Peru21

```python
from scrapper_peru21 import Peru21Scrapper
from datetime import datetime

# Uso básico (con reanudación automática)
scraper = Peru21Scrapper()
scraper.extract_historical(
    output_file='noticias_peru21.tsv',
    resume=True  # Continúa desde última fecha si existe el archivo
)

# Configuración personalizada
scraper = Peru21Scrapper(
    max_workers=20,      # Hilos paralelos
    verbose=True,        # Mostrar progreso
    max_retries=5,       # Aumentar reintentos
    retry_delay=10       # Espera base más larga
)

scraper.extract_historical(
    start_date=datetime(2025, 1, 1),  # Fecha específica
    output_file='noticias_peru21.tsv',
    max_empty_attempts=10,
    resume=True
)
```

### Scraper de Diario Correo

```python
from scrapper import NewsScrapper
from datetime import datetime

# Uso básico (con reanudación automática)
scraper = NewsScrapper()
scraper.extract_historical(
    output_file='noticias.tsv',
    resume=True
)

# Configuración personalizada
scraper = NewsScrapper(
    max_workers=10,
    verbose=True,
    max_retries=3,
    retry_delay=5
)

scraper.extract_historical(
    start_date=datetime(2025, 1, 1),
    output_file='noticias.tsv',
    max_empty_attempts=10,
    resume=True
)
```

## 📊 Parámetros Configurables

| Parámetro | Descripción | Valor por defecto |
|-----------|-------------|-------------------|
| `max_workers` | Hilos paralelos para descargar noticias | Peru21: 20, Correo: 10 |
| `verbose` | Mostrar progreso en consola | `True` |
| `max_retries` | Reintentos por cada request fallido | `3` |
| `retry_delay` | Segundos de espera base (se duplica cada intento) | `5` |
| `start_date` | Fecha desde donde empezar (si `None`, usa hoy) | `None` |
| `output_file` | Archivo de salida TSV | `'noticias_*.tsv'` |
| `max_empty_attempts` | Días consecutivos sin noticias antes de parar | `10` |
| `resume` | Continuar desde última fecha del archivo | `True` |

## 🔄 Flujo de Reanudación

```
1. Script inicia
   ↓
2. ¿Existe archivo TSV y resume=True?
   │
   ├─ Sí → Lee última fecha del archivo
   │        Continúa desde (última_fecha - 1 día)
   │        Modo: APPEND
   │
   └─ No → Comienza desde start_date (o hoy)
           Modo: WRITE
```

## 💡 Ejemplos de Uso

### Escenario 1: Primera ejecución
```python
# El script descarga desde hoy hacia atrás
scraper = Peru21Scrapper()
scraper.extract_historical(output_file='noticias.tsv')
```

### Escenario 2: Interrupción y reanudación
```bash
# Primera ejecución (procesa hasta 2025-11-05)
$ python scrapper_peru21.py
📰 Descargadas: 150 noticias | Fecha actual: 2025-11-05
^C
⏸️ Proceso interrumpido. Total: 150 noticias guardadas

# Segunda ejecución (continúa automáticamente desde 2025-11-04)
$ python scrapper_peru21.py
📅 Última noticia encontrada: 2025-11-05
🔄 Reanudando desde: 2025-11-04
📰 Descargadas: 180 noticias | Fecha actual: 2025-11-04
```

### Escenario 3: Error de conexión
```python
# El script reintenta automáticamente
⚠️ Error de conexión (intento 1/3). Esperando 5s...
⚠️ Error de conexión (intento 2/3). Esperando 10s...
✅ Conexión recuperada
📰 Descargadas: 200 noticias | Fecha actual: 2025-11-03
```

## 📝 Notas Importantes

1. **Pandas requerido**: Ahora se necesita `pandas` para leer fechas del archivo
   ```bash
   pip install pandas
   ```

2. **Archivos existentes**: Si quieres comenzar de cero, elimina el archivo `.tsv`
   ```bash
   rm noticias_peru21.tsv
   ```

3. **Interrupción segura**: Usa `Ctrl+C` para detener de forma segura
   - Los datos se guardan incrementalmente
   - Puedes reanudar en cualquier momento

4. **Reintentos inteligentes**: 
   - Espera exponencial: 5s, 10s, 20s
   - Solo se aplica a errores de conexión
   - Otros errores se registran y el script continúa

## 🐛 Solución de Problemas

### Problema: El script no detecta la última fecha
**Solución**: Verifica que el archivo TSV tenga el header correcto:
```tsv
fecha	titular	contenido	seccion	url
```

### Problema: Muchos errores de conexión
**Solución**: Aumenta los parámetros de reintento:
```python
scraper = Peru21Scrapper(
    max_retries=5,
    retry_delay=10
)
```

### Problema: Quiero empezar de cero
**Solución**: 
```python
# Opción 1: Eliminar el archivo
import os
os.remove('noticias.tsv')

# Opción 2: Deshabilitar reanudación
scraper.extract_historical(resume=False)
```

## 📈 Rendimiento

- **Peru21**: ~20 hilos paralelos, ~1-2 noticias/segundo
- **Diario Correo**: ~10 hilos paralelos, ~0.5-1 noticias/segundo
- **Consumo de memoria**: Mínimo (procesamiento incremental)
- **Almacenamiento**: ~1-2 KB por noticia

## ✅ Checklist de Validación

- ✅ Reintentos automáticos funcionando
- ✅ Reanudación desde última fecha
- ✅ Manejo de Ctrl+C
- ✅ Modo append preserva datos anteriores
- ✅ Espera exponencial implementada
- ✅ Mensajes informativos en consola
