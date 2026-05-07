import os
import hashlib
import time

def get_scanned_files_list(directory, recursive=True):
    """Obtiene la lista de (nombre, ruta_completa, tamaño) para un archivo o carpeta."""
    found_files = []
    if os.path.isfile(directory):
        try:
            size = os.path.getsize(directory)
            found_files.append((os.path.basename(directory), directory, size))
        except Exception:
            pass
    elif os.path.isdir(directory):
        if recursive:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    full_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(full_path)
                        found_files.append((file, full_path, size))
                    except Exception:
                        continue
        else:
            try:
                for entry in os.scandir(directory):
                    if entry.is_file():
                        try:
                            size = entry.stat().st_size
                            found_files.append((entry.name, entry.path, size))
                        except Exception:
                            continue
            except Exception:
                pass
    return found_files

def calculate_file_hashes_and_metadata(full_path):
    """Calcula los hashes MD5 y SHA-256 y obtiene las fechas de creación y modificación de un archivo."""
    md5_hash = hashlib.md5()
    sha256_hash = hashlib.sha256()
    err = None
    
    try:
        with open(full_path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                md5_hash.update(byte_block)
                sha256_hash.update(byte_block)
        md5 = md5_hash.hexdigest()
        sha256 = sha256_hash.hexdigest()
    except Exception as e:
        md5 = "No disponible"
        sha256 = "No disponible"
        err = str(e)

    try:
        stat = os.stat(full_path)
        created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_ctime))
        modified_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))
    except Exception:
        created_at = "No disponible"
        modified_at = "No disponible"

    return md5, sha256, created_at, modified_at, err
