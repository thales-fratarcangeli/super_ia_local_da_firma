import unicodedata

def slugify(text: str) -> str:
    # Normaliza o texto para remover acentos
    normalized = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    # Converte para minúsculas
    normalized = normalized.lower()
    # Substitui sequências de caracteres não alfanuméricos por "-"
    slug = ''.join(char if char.isalnum() else '-' for char in normalized)
    # Remove '-' no início e no fim
    slug = slug.strip('-')
    return slug
