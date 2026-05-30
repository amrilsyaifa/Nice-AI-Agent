import os
from pathlib import Path

def read_file(path: str) -> str:
    """Baca isi file."""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File '{path}' not found."
    except Exception as e:
        return f"Error: {str(e)}"
    
def write_file(path: str, content: str) -> str:
    """Tulis content ke file. Buat file baru kalau belum ada."""
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)  # Pastikan direktori ada
        with open(path, 'w') as f:
            f.write(content)
        return f"✅ File '{path}' berhasil ditulis ({len(content)} karakter)"
    except Exception as e:
        return f"Error: {str(e)}"

def list_directory(path: str) -> str:
    """List isi direktori."""
    try:
        items = os.listdir(path)
        if not items:
            return f"📂 Direktori '{path}' kosong."
        
        result = f"📂 Isi direktori '{path}':\n"
        for item in sorted(items):
            full = os.path.join(path, item)
            icon = "📁" if os.path.isdir(full) else "📄"
            result += f"  {icon} {item}\n"
        return result.strip()
    except FileNotFoundError:
        return f"Error: Direktori '{path}' tidak ditemukan."
    except Exception as e:
        return f"Error: {str(e)}"
