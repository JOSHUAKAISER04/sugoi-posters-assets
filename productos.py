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

# Contadores por personaje/anime
contadores = {}

def limpiar_nombre(nombre_archivo):
    """Limpia el nombre del archivo quitando extensión, guiones bajos y numeraciones."""
    nombre = os.path.splitext(nombre_archivo)[0]
    # Quita "_2", "(3)", " 1", etc.
    nombre = re.sub(r"[_\s]*\(?\d+\)?$", "", nombre)
    # Elimina guiones y espacios sobrantes
    return nombre.strip()

for root, dirs, files in os.walk(carpeta_base):
    for file in sorted(files):
        if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            relative_path = os.path.relpath(os.path.join(root, file), carpeta_base)
            relative_path = relative_path.replace("\\", "/")
            url = base_url + relative_path

            partes = relative_path.split("/")
            carpeta = partes[0]  # Ejemplo: C-a, P-o, etc.

            if carpeta not in categorias:
                continue  # Saltar archivos fuera de categorías definidas

            tipo = categorias[carpeta]
            nombre_categoria = tipo["nombre"]
            categoria_plural = tipo["categoria"]
            precio = tipo["precio"]
            descripcion = tipo["descripcion"]

            # Lógica especial para Polaroids
            if carpeta == "Pol":
                # Ruta esperada: Pol/anime/Naruto.png
                if len(partes) >= 3 and partes[1].lower() == "anime":
                    subcategoria = limpiar_nombre(file)
                    personaje = subcategoria  # en Polaroids, el personaje = subcategoria
                else:
                    subcategoria = "Desconocido"
                    personaje = limpiar_nombre(file)
            else:
                # Ejemplo: C-a/Jujutsu Kaisen/Toji_2.png
                if len(partes) >= 2:
                    subcategoria = partes[1]  # nombre del anime
                else:
                    subcategoria = "General"
                personaje = limpiar_nombre(file)

            clave = f"{carpeta}-{subcategoria}-{personaje}"
            contadores[clave] = contadores.get(clave, 0) + 1
            numero = contadores[clave]

            # Nombre final del producto
            if numero > 1:
                nombre_producto = f"{nombre_categoria} {personaje} #{numero}"
            else:
                nombre_producto = f"{nombre_categoria} {personaje}"

            productos.append(f'''  Product(
    nombre: "{nombre_producto}",
    precio: "{precio}",
    descripcion: "{descripcion}",
    categoria: "{categoria_plural}",
    imagen: "{url}",
    subcategoria: "{subcategoria}",
  ),''')

# Generar archivo Dart
with open("products.dart", "w", encoding="utf-8") as f:
    f.write("const List<Product> productos = [\n")
    f.write("\n".join(productos))
    f.write("\n];\n")

print("✅ Archivo 'products.dart' generado con nombres y subcategorías correctamente asignados.")
