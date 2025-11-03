"""
Módulo principal responsável por manipular e listar documentos digitais.
"""
from pathlib import Path

# Extensões de arquivos suportadas
SUPPORTED = ['.pdf', '.epub', '.docx', '.txt', '.mobi', '.azw']

def find_documents(root):
    """
    Percorre recursivamente um diretório e retorna todos os arquivos suportados.
    """
    p = Path(root)
    return [str(f) for f in p.rglob('*') if f.suffix.lower() in SUPPORTED]
