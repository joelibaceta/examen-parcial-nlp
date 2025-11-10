
import requests
import time

def generate_clickbait_ollama(titulo, model="llama3.2:3b", max_retries=3):

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
        response = requests.post(
            'http://localhost:11434/api/generate', #ollama port
            json={
                'model': model,
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
            clickbait = clickbait.strip('"\'\'').strip()
            if len(clickbait) > 0 and len(clickbait) < 200:
                return clickbait
    
    return None

 
 