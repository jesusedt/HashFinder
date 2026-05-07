import csv
import json
import time

def save_to_csv(filename, filtered_data):
    """Guarda los detalles de los archivos filtrados en un archivo CSV (compatible con Excel usando UTF-8 BOM)."""
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["ID", "Nombre de Archivo", "Ruta Relativa", "Tamaño (Bytes)", "MD5", "SHA-256", "Fecha Creación", "Fecha Modificación", "Error"])
        for i, file in enumerate(filtered_data):
            writer.writerow([
                i + 1,
                file['nombre'],
                file['ruta_relativa'],
                file['tamano'],
                file['md5'],
                file['sha256'],
                file['fecha_creacion'],
                file['fecha_modificacion'],
                file['error'] or ""
            ])

def save_to_json(filename, filtered_data, scan_directory):
    """Guarda los detalles de los archivos filtrados en un archivo JSON estructurado."""
    export_data = {
        'directorio_escaneado': scan_directory,
        'total_archivos': len(filtered_data),
        'fecha_exportacion': time.strftime('%d/%m/%Y %H:%M:%S'),
        'archivos': filtered_data
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
