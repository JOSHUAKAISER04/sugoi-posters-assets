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
            carpeta = partes[0]  # Ejemplo: C-a, P-o, S-e, Pol

            if carpeta not in categorias:
                continue  # Saltar archivos fuera de categorías definidas

            tipo = categorias[carpeta]
            nombre_categoria = tipo["nombre"]
            categoria_plural = tipo["categoria"]
            precio = tipo["precio"]
            descripcion = tipo["descripcion"]

            # --- Lógica especial para Polaroids ---
            if carpeta == "Pol":
                # Caso especial: Pol/anime/<archivo>
                if len(partes) >= 3 and partes[1].lower() == "anime":
                    subcategoria = limpiar_nombre(file)  # El nombre del archivo es la subcategoría
                    personaje = subcategoria  # Y también el personaje
                else:
                    # Se comporta igual que camisas
                    if len(partes) >= 2:
                        subcategoria = partes[1]
                    else:
                        subcategoria = "General"
                    personaje = limpiar_nombre(file)
            else:
                # --- Lógica general (camisas, posters, separadores, etc.) ---
                if len(partes) >= 2:
                    subcategoria = partes[1]
                else:
                    subcategoria = "General"
                personaje = limpiar_nombre(file)

            # Contador único por categoría + subcategoría + personaje
            clave = f"{carpeta}-{subcategoria.lower()}-{personaje.lower()}"
            contadores[clave] = contadores.get(clave, 0) + 1
            numero = contadores[clave]

            # Nombre del producto con #n si hay repetidos
            if numero > 1:
                nombre_producto = f"{nombre_categoria} {personaje} #{numero}"
            else:
                nombre_producto = f"{nombre_categoria} {personaje}"

            # Generar entrada del producto
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

print("✅ Archivo 'products.dart' generado correctamente con subcategorías y nombres según las reglas definidas.")
