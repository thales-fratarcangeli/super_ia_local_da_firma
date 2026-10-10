import unicodedata
import re

def slugify(text: str) -> str:
    # Converter para minúsculas
    text = text.lower()
    # Remover acentos usando unicodedata
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    # Substituir qualquer sequência de caracteres não alfanuméricos por um único "-"
    text = re.sub(r'[^\w\s-]', '-', text)
    # Substituir espaços por "-"
    text = re.sub(r'\s+', '-', text)
    # Remover "-" no início e no fim
    text = text.strip('-')
    return text
