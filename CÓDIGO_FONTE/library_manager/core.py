from pathlib import Path
SUPPORTED = ['.pdf', '.epub', '.docx']
def find_documents(root):
    p = Path(root)
    return [str(f) for f in p.rglob('*') if f.suffix.lower() in SUPPORTED]
