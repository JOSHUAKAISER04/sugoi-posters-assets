import os

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

# Diccionario de índices por subcarpeta
indices = {}

for root, dirs, files in os.walk(carpeta_base):
    for file in sorted(files):  # sorted para consistencia
        if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            relative_path = os.path.relpath(os.path.join(root, file), carpeta_base)
            relative_path = relative_path.replace("\\", "/")

            url = base_url + relative_path

            partes = relative_path.split("/")
            carpeta = partes[0]  # C-a, P-o, S-e, Pol

            tipo = categorias.get(carpeta, {
                "nombre": "Producto",
                "categoria": "Productos",
                "precio": "0",
                "descripcion": "Producto de colección inspirado en tus animes favoritos."
            })

            nombre_base = tipo["nombre"]
            categoria_plural = tipo["categoria"]
            precio_base = tipo["precio"]
            descripcion = tipo["descripcion"]

            # Todos los tipos tendrán subcarpetas para el anime
            if len(partes) > 1:
                anime = partes[1]
                clave = f"{carpeta}-{anime}"
                indice = indices.get(clave, 0) + 1
                indices[clave] = indice
                nombre = f"{nombre_base} {anime} #{indice}"
            else:
                nombre = nombre_base

            # Generar producto en Dart
            productos.append(f'''  Product(
    nombre: "{nombre}",
    precio: "{precio_base}",
    descripcion: "{descripcion}",
    categoria: "{categoria_plural}",
    imagen: "{url}",
  ),''')

# Generar archivo Dart
with open("products.dart", "w", encoding="utf-8") as f:
    f.write("const List<Product> productos = [\n")
    f.write("\n".join(productos))
    f.write("\n];\n")

print("✅ Archivo 'products.dart' generado con subcarpetas en todas las categorías.")
