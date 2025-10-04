import os
import json

# Configura tus datos
usuario = "JOSHUAKAISER04"          # Usuario de GitHub (dueño del repo)
repositorio = "sugoi-posters-assets"  # Nombre del repo
rama = "main"                   # Rama donde subes las imágenes
carpeta_base = "."              # "." = raíz del repositorio clonado

# URL base
base_url = f"https://raw.githubusercontent.com/{usuario}/{repositorio}/{rama}/"

# Lista de resultados
urls = []

# Recorre todas las carpetas y subcarpetas
for root, dirs, files in os.walk(carpeta_base):
    for file in files:
        # Solo tomar imágenes comunes
        if file.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")):
            relative_path = os.path.relpath(os.path.join(root, file), carpeta_base)
            relative_path = relative_path.replace("\\", "/")
            url = base_url + relative_path
            urls.append({
                "nombre": file,
                "ruta": relative_path,
                "url": url
            })

# Guardar en JSON
with open("imagenes.json", "w", encoding="utf-8") as f:
    json.dump(urls, f, indent=4, ensure_ascii=False)

print("✅ Archivo 'imagenes.json' generado con todas las carpetas.")