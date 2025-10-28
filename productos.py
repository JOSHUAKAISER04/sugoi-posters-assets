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
        "precio": "500",
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
    """Limpia el nombre de un archivo quitando extensiones y formateando texto."""
    nombre = os.path.splitext(nombre_archivo)[0]
    nombre = re.sub(r"[_\s]*\(?(\d+)\)?$", r" #\1", nombre)
    nombre = re.sub(r"[_]+", " ", nombre)
    nombre = re.sub(r"\s{2,}", " ", nombre).strip()
    return nombre

def limpiar_subcategoria(nombre_carpeta):
    """Formatea los nombres de las subcarpetas correctamente."""
    nombre = nombre_carpeta.replace("_", " ")
    nombre = re.sub(r"\s{2,}", " ", nombre).strip()
    return nombre.title()

def extraer_variante(nombre_carpeta):
    """Devuelve (nombre_base, numero_variante o None si no hay número explícito)."""
    match = re.match(r"^(.+?)[_\s]*(\d+)$", nombre_carpeta)
    if match:
        nombre_personaje = match.group(1).replace("_", " ").strip()
        numero_variante = int(match.group(2))
        return nombre_personaje, numero_variante
    return nombre_carpeta.replace("_", " ").strip(), None


# --- RECORRIDO DE CARPETAS ---
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

    # --- CAMISAS Y SUÉTERES ---
    if categoria_dir in ("C-a", "S-u"):
        for subcategoria_dir in sorted(os.listdir(categoria_path)):
            subcategoria_path = os.path.join(categoria_path, subcategoria_dir)
            if not os.path.isdir(subcategoria_path):
                continue

            subcategoria_limpia = limpiar_subcategoria(subcategoria_dir)

            # 🔹 Listamos carpetas internas y ordenamos personalizadas primero
            internas = [v for v in os.listdir(subcategoria_path) if os.path.isdir(os.path.join(subcategoria_path, v))]
            personalizadas = [v for v in internas if "personalizada" in v.lower()]
            otras = [v for v in internas if "personalizada" not in v.lower()]
            orden_final = personalizadas + otras  # siempre primero las personalizadas

            # 🔸 Procesamos cada variante
            for variante_dir in orden_final:
                variante_path = os.path.join(subcategoria_path, variante_dir)
                if not os.path.isdir(variante_path):
                    continue

                es_personalizada = "personalizada" in variante_dir.lower()
                nombre_base, numero = extraer_variante(variante_dir)

                imagenes_variante = [
                    base_url + os.path.relpath(os.path.join(variante_path, file), carpeta_base).replace("\\", "/")
                    for file in sorted(os.listdir(variante_path))
                    if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
                ]
                if not imagenes_variante:
                    continue

                # 🩵 Corrección del nombre
                if es_personalizada:
                    nombre_producto = f"{nombre_categoria} Personalizada #1"
                    subcategoria_final = ""
                else:
                    nombre_producto = f"{nombre_categoria} {nombre_base} #1"
                    subcategoria_final = subcategoria_limpia

                imagenes_dart = "[\n" + ",\n".join([f'      \"{img}\"' for img in imagenes_variante]) + "\n    ]"

                productos.append(f'''  Product(
    nombre: "{nombre_producto}",
    precio: "{precio}",
    descripcion: "{descripcion}",
    categoria: "{categoria_plural}",
    imagenes: {imagenes_dart},
    subcategoria: "{subcategoria_final}",
  ),''')

    # --- OTROS PRODUCTOS ---
    else:
        for subcategoria_dir in os.listdir(categoria_path):
            subcategoria_path = os.path.join(categoria_path, subcategoria_dir)
            if not os.path.isdir(subcategoria_path):
                continue

            subcategoria_limpia = limpiar_subcategoria(subcategoria_dir)

            for file in sorted(os.listdir(subcategoria_path)):
                if not file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    continue

                relative_path = os.path.relpath(os.path.join(subcategoria_path, file), carpeta_base).replace("\\", "/")
                url = base_url + relative_path
                personaje = limpiar_nombre(file)

                if categoria_dir == "Pol":
                    subcategoria_final = personaje if subcategoria_dir.lower() == "anime" else subcategoria_limpia
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

# --- GENERAR ARCHIVO DART ---
with open("products.dart", "w", encoding="utf-8") as f:
    f.write("const List<Product> productos = [\n")
    f.write("\n".join(productos))
    f.write("\n];\n")

print(f"✅ Archivo 'products.dart' generado correctamente con {len(productos)} productos.")
print("\n📁 Estructura procesada:")
print("   - Camisas (C-a) y Sueters (S-u): Categoría → Subcategoría → Variante → Múltiples imágenes")
print("   - Otros productos: Categoría → Subcategoría → Archivos individuales")
print("\n📝 Ejemplo corregido:")
print("   - 1_Personalizada → Camisa Personalizada (sin subcategoría y aparece primero)")
print("   - Tomioka → Camisa Tomioka #1")
print("   - Tomioka_1 → Camisa Tomioka #2")
