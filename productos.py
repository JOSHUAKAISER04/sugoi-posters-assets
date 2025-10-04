import os

# Configuración del repo
# Configura tus datos
usuario = "JOSHUAKAISER04"          # Usuario de GitHub (dueño del repo)
repositorio = "sugoi-posters-assets"  # Nombre del repo
rama = "main"                   # Rama donde subes las imágenes
carpeta_base = "."              # "." = raíz del repositorio clonado

# Definición de categorías, precios y descripciones
categorias = {
    "C-a": {
        "nombre": "Camisa",
        "precio": "280",
        "descripcion": "Camisa de alta calidad inspirada en tu anime favorito. Ideal para el día a día o coleccionar como parte de tu pasión otaku."
    },
    "P-o": {
        "nombre": "Poster",
        "precio": "70",
        "descripcion": "Poster con impresión premium para dar vida a tus espacios. Perfecto para decorar tu cuarto, oficina o rincón otaku."
    },
    "S-e": {
        "nombre": "Separador",
        "precio": "25",
        "descripcion": "Separador de diseño exclusivo para que nunca pierdas la página en tus mangas y libros. Compacto, resistente y coleccionable."
    },
    "Pol": {
        "nombre": "Polaroid",
        "precio": "20",
        "descripcion": "Polaroid coleccionable con acabado especial. Llévate un recuerdo único de tu anime favorito en formato de bolsillo."
    },
}

# URL base
base_url = f"https://raw.githubusercontent.com/{usuario}/{repositorio}/{rama}/"

productos = []

# Contadores globales para Polaroids y Separadores
contador_polaroid = 1
contador_separador = 1

# Diccionarios para llevar índices por subcarpeta
indices = {}

for root, dirs, files in os.walk(carpeta_base):
    for file in sorted(files):  # sorted para que el orden sea consistente
        if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            relative_path = os.path.relpath(os.path.join(root, file), carpeta_base)
            relative_path = relative_path.replace("\\", "/")

            url = base_url + relative_path

            partes = relative_path.split("/")
            carpeta = partes[0]  # C-a, P-o, etc.

            tipo = categorias.get(carpeta, {"nombre": "Producto", "precio": "0", "descripcion": "Producto de colección inspirado en tus animes favoritos."})
            nombre_base = tipo["nombre"]
            precio_base = tipo["precio"]
            descripcion = tipo["descripcion"]

            # --- Camisas y Posters (con subcarpetas por anime) ---
            if carpeta in ["C-a", "P-o"] and len(partes) > 1:
                anime = partes[1]
                clave = f"{carpeta}-{anime}"
                indice = indices.get(clave, 0) + 1
                indices[clave] = indice
                nombre = f"{nombre_base} {anime} #{indice}"

            # --- Polaroids ---
            elif carpeta == "Pol":
                nombre = f"{nombre_base} {contador_polaroid:02d}"
                contador_polaroid += 1

            # --- Separadores ---
            elif carpeta == "S-e":
                nombre = f"{nombre_base} {contador_separador:02d}"
                contador_separador += 1

            else:
                nombre = nombre_base

            # Generar producto en Dart
            productos.append(f'''  Product(
    nombre: "{nombre}",
    precio: "{precio_base}",
    descripcion: "{descripcion}",
    categoria: "{tipo['nombre']}",
    imagen: "{url}",
  ),''')

# Generar archivo Dart
with open("products.dart", "w", encoding="utf-8") as f:
    f.write("const List<Product> productos = [\n")
    f.write("\n".join(productos))
    f.write("\n];\n")

print("✅ Archivo 'products.dart' generado con nombres numerados por anime y tipo.")
