# Examen Parcial - Procesamiento de Lenguaje Natural

## Pregunta 1 de 1 (20 Puntos)

## Parte 1: Web Scraping + Regex (5 puntos)

Elija una de las siguientes páginas de noticias:
- Gestion.pe
- Peru21
- Expreso.pe

Extraiga al menos noticias del dos meses (título, contenido y fecha, link de la noticia) de diferentes tópicos (al menos 7 tópicos, deben de incluir tópicos como deportes, internacionales, economía).

Limpie el texto aplicando regex para:
- Eliminar caracteres especiales, URLs o hashtags.
- Normalizar espacios en blanco y saltos de línea.

**Respuesta:** [Parte 1 - Web Scraping y Regex](notebook.ipynb)

## Parte 2: Análisis de Texto con Técnicas de PLN (15 puntos)

Aplique las siguientes técnicas al corpus de noticias obtenido:

### 1. N-gramas (3 puntos)

- Crear un generador de noticias usando un modelo trigramas usando el contenido de las noticias.
- Identifique las combinaciones más frecuentes e interprételas.

**Respuesta:** [Parte 2.1 - N-gramas](parte_2_2_notebook.ipynb)

### 2. Modelado de Temas con LDA (2 puntos)

- Aplique LDA (Latent Dirichlet Allocation) para identificar 7 tópicos principales en las noticias.
- Muestre los resultados del modelo con 3 noticias ejemplos.

**Respuesta:** [Parte 2.2 - LDA](parte_2_2_notebook.ipynb)

### 3. TF-IDF (2 puntos)

- Calcule la matriz TF-IDF para el corpus y muestre las palabras más relevantes.
- Aplique LDA + TF-IDF para identificar 7 tópicos principales en las noticias.
- Muestre los resultados del modelo con 3 noticias ejemplo.

**Respuesta:** [Parte 2.3 - TF-IDF](parte_2_3_notebook.ipynb)

### 4. Word Embeddings: CBOW y Skip-Gram (3 puntos)

- Entrene un modelo de Word2Vec (usando gensim) con CBOW o Skip-Gram.
- Busque las palabras similares a: elecciones, chancay, delincuencia.
- Usando el modelo entrenado mostrar en un espacio de dos dimensiones 10 noticias de dos tópicos diferentes (5 de cada uno) donde los ubica (probar con T-SNE y PCA).

**Respuesta:** [Parte 2.4 - Word Embeddings](parte_2_4_notebook.ipynb)

### 5. Generador de Clickbaits con Seq2Seq (5 puntos)

- Preparar dataset: titular normal → titular clickbait
- Entrenar modelo Seq2Seq encoder-decoder para generar títulos con estilo clickbait automáticamente a partir del titular, es decir sin revelar el contenido y fomentar el click a abrir la noticia.

**Respuesta:** [Parte 2.5 - Generador de Clickbaits](parte_2_5_notebook.ipynb)

