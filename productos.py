import os
import re

# Configuración del repo
usuario = "JOSHUAKAISER04"
repositorio = "sugoi-posters-assets"
rama = "main"
carpeta_base = "."

# Definición de categorías, precios y descripciones
categorias = {
    "C-a": {
        "nombre": "Camisa",
        "categoria": "Camisas",
        "precio": "280",
        "descripcion": "Camisa de alta calidad inspirada en tu anime favorito. Ideal para el día a día o coleccionar como parte de tu pasión otaku."
    },
    "S-u": {
        "nombre": "Suéter",
        "categoria": "Sueters",
        "precio": "350",
        "descripcion": "Suéter cómodo y duradero con diseños únicos de tus animes favoritos. Ideal para mantenerte abrigado con estilo otaku."
    },
    "P-o": {
        "nombre": "Poster",
        "categoria": "Posters",
        "precio": "70",
        "descripcion": "Poster con impresión premium para dar vida a tus espacios. Perfecto para decorar tu cuarto, oficina o rincón otaku."
    },
    "S-e": {
        "nombre": "Separador",
        "categoria": "Separadores",
        "precio": "25",
        "descripcion": "Separador de diseño exclusivo para que nunca pierdas la página en tus mangas y libros. Compacto, resistente y coleccionable."
    },
    "Pol": {
        "nombre": "Polaroid",
        "categoria": "Polaroids",
        "precio": "20",
        "descripcion": "Polaroid coleccionable con acabado especial. Llévate un recuerdo único de tu anime favorito en formato de bolsillo."
    },
}

# URL base
base_url = f"https://raw.githubusercontent.com/{usuario}/{repositorio}/{rama}/"

productos = []
contadores = {}

def limpiar_nombre(nombre_archivo):
    nombre = os.path.splitext(nombre_archivo)[0]
    nombre = re.sub(r"[_\s]*\(?(\d+)\)?$", r" #\1", nombre)
    nombre = re.sub(r"_(?!#?\d+)", " ", nombre)
    nombre = re.sub(r"\s*&\s*", " & ", nombre)
    nombre = re.sub(r"\s{2,}", " ", nombre).strip()
    return nombre

def limpiar_subcategoria(nombre_carpeta):
    nombre = nombre_carpeta.replace("_", " ")
    nombre = re.sub(r"\s*&\s*", " & ", nombre)
    nombre = re.sub(r"\s{2,}", " ", nombre).strip()
    return nombre

def extraer_variante(nombre_carpeta):
    match = re.match(r"^(.+?)[_\s]*(\d+)$", nombre_carpeta)
    if match:
        nombre_personaje = match.group(1).replace("_", " ").strip()
        numero_variante = match.group(2)
        return nombre_personaje, numero_variante
    else:
        return nombre_carpeta.replace("_", " ").strip(), "1"

# Recorremos la estructura de directorios
for categoria_dir in os.listdir(carpeta_base):
    if categoria_dir not in categorias:
        continue

    categoria_path = os.path.join(carpeta_base, categoria_dir)
    if not os.path.isdir(categoria_path):
        continue

    tipo = categorias[categoria_dir]
    nombre_categoria = tipo["nombre"]
    categoria_plural = tipo["categoria"]
    precio = tipo["precio"]
    descripcion = tipo["descripcion"]

    # --- LÓGICA ESPECIAL PARA CAMISAS Y SUÉTERS ---
    if categoria_dir in ("C-a", "S-u"):
        for subcategoria_dir in os.listdir(categoria_path):
            subcategoria_path = os.path.join(categoria_path, subcategoria_dir)
            if not os.path.isdir(subcategoria_path):
                continue

            subcategoria_limpia = limpiar_subcategoria(subcategoria_dir)

            for variante_dir in os.listdir(subcategoria_path):
                variante_path = os.path.join(subcategoria_path, variante_dir)
                if not os.path.isdir(variante_path):
                    continue

                nombre_personaje, numero_variante = extraer_variante(variante_dir)

                imagenes_variante = []
                for file in sorted(os.listdir(variante_path)):
                    if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                        relative_path = os.path.relpath(os.path.join(variante_path, file), carpeta_base)
                        relative_path = relative_path.replace("\\", "/")
                        url = base_url + relative_path
                        imagenes_variante.append(url)

                if not imagenes_variante:
                    continue

                nombre_producto = f"{nombre_categoria} {nombre_personaje} #{numero_variante}"

                imagenes_dart = "[\n" + ",\n".join([f'      "{img_url}"' for img_url in imagenes_variante]) + "\n    ]"

                productos.append(f'''  Product(
    nombre: "{nombre_producto}",
    precio: "{precio}",
    descripcion: "{descripcion}",
    categoria: "{categoria_plural}",
    imagenes: {imagenes_dart},
    subcategoria: "{subcategoria_limpia}",
  ),''')

    # --- LÓGICA PARA LOS DEMÁS PRODUCTOS ---
    else:
        for subcategoria_dir in os.listdir(categoria_path):
            subcategoria_path = os.path.join(categoria_path, subcategoria_dir)
            if not os.path.isdir(subcategoria_path):
                continue

            subcategoria_limpia = limpiar_subcategoria(subcategoria_dir)

            for file in sorted(os.listdir(subcategoria_path)):
                if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    relative_path = os.path.relpath(os.path.join(subcategoria_path, file), carpeta_base)
                    relative_path = relative_path.replace("\\", "/")
                    url = base_url + relative_path

                    personaje = limpiar_nombre(file)

                    if categoria_dir == "Pol":
                        if subcategoria_dir.lower() == "anime":
                            subcategoria_final = personaje
                            personaje_final = personaje
                        else:
                            subcategoria_final = subcategoria_limpia
                            personaje_final = personaje
                    else:
                        subcategoria_final = subcategoria_limpia
                        personaje_final = personaje

                    clave = f"{categoria_dir}-{subcategoria_final.lower()}-{personaje_final.lower()}"
                    contadores[clave] = contadores.get(clave, 0) + 1
                    numero = contadores[clave]

                    if numero > 1 and f"#{numero}" not in personaje_final:
                        nombre_producto = f"{nombre_categoria} {personaje_final} #{numero}"
                    else:
                        nombre_producto = f"{nombre_categoria} {personaje_final}"

                    imagenes_dart = f'["{url}"]'

                    productos.append(f'''  Product(
    nombre: "{nombre_producto}",
    precio: "{precio}",
    descripcion: "{descripcion}",
    categoria: "{categoria_plural}",
    imagenes: {imagenes_dart},
    subcategoria: "{subcategoria_final}",
  ),''')

# Generar archivo Dart
with open("products.dart", "w", encoding="utf-8") as f:
    f.write("const List<Product> productos = [\n")
    f.write("\n".join(productos))
    f.write("\n];\n")

print(f"✅ Archivo 'products.dart' generado correctamente con {len(productos)} productos.")
print("\n📁 Estructura procesada:")
print("   - Camisas (C-a) y Sueters (S-u): Categoría → Subcategoría → Variante_Personaje → Múltiples imágenes")
print("   - Otros productos: Categoría → Subcategoría → Archivos individuales")
print("\n📝 Ejemplos de productos generados:")
print("   - Camisa Gojo #1 (con múltiples imágenes)")
print("   - Sueter Luffy #1 (con múltiples imágenes)")
print("   - Poster Naruto (una sola imagen)")
print("   - Separador Tanjiro (una sola imagen)")
print("   - Polaroid Anime (una sola imagen)")
