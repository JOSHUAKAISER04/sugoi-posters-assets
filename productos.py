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
    """Limpia el nombre del archivo para uso en el nombre del producto."""
    nombre = os.path.splitext(nombre_archivo)[0]

    # Convierte patrones _1, (2), etc. → #1, #2
    nombre = re.sub(r"[_\s]*\(?(\d+)\)?$", r" #\1", nombre)

    # Sustituye guiones bajos por espacios, pero solo si no son parte del patrón numérico
    nombre = re.sub(r"_(?!#?\d+)", " ", nombre)

    # Asegura espacios alrededor del símbolo &
    nombre = re.sub(r"\s*&\s*", " & ", nombre)

    # Limpieza final de dobles espacios
    nombre = re.sub(r"\s{2,}", " ", nombre).strip()
    return nombre

def limpiar_subcategoria(nombre_carpeta):
    """Limpia el nombre de la carpeta para uso en subcategoría."""
    # Reemplaza guiones bajos por espacios
    nombre = nombre_carpeta.replace("_", " ")
    
    # Asegura espacios alrededor del símbolo &
    nombre = re.sub(r"\s*&\s*", " & ", nombre)
    
    # Limpieza final de dobles espacios
    nombre = re.sub(r"\s{2,}", " ", nombre).strip()
    return nombre

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
                if len(partes) >= 3 and partes[1].lower() == "anime":
                    subcategoria = limpiar_nombre(file)
                    personaje = subcategoria
                else:
                    # Aplicar limpieza a la subcategoría para Polaroids
                    subcategoria = limpiar_subcategoria(partes[1]) if len(partes) >= 2 else "General"
                    personaje = limpiar_nombre(file)
            else:
                # --- Lógica general (camisas, posters, separadores, etc.) ---
                # Aplicar limpieza a la subcategoría
                subcategoria = limpiar_subcategoria(partes[1]) if len(partes) >= 2 else "General"
                personaje = limpiar_nombre(file)

            # Contador único por categoría + subcategoría + personaje
            clave = f"{carpeta}-{subcategoria.lower()}-{personaje.lower()}"
            contadores[clave] = contadores.get(clave, 0) + 1
            numero = contadores[clave]

            # Nombre del producto con #n si hay repetidos
            if numero > 1 and f"#{numero}" not in personaje:
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

print("✅ Archivo 'products.dart' generado correctamente con las reglas de nombres aplicadas.")