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

def extraer_variante(nombre_carpeta):
    """Extrae el nombre del personaje y el número de variante de una carpeta como 'Gojo_1'."""
    # Busca patrones como: Gojo_1, Gojo_2, Luffy_1, etc.
    match = re.match(r"^(.+?)[_\s]*(\d+)$", nombre_carpeta)
    if match:
        nombre_personaje = match.group(1).replace("_", " ").strip()
        numero_variante = match.group(2)
        return nombre_personaje, numero_variante
    else:
        # Si no hay número, se considera variante 1
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
    
    # Recorremos las subcategorías (animes/series)
    for subcategoria_dir in os.listdir(categoria_path):
        subcategoria_path = os.path.join(categoria_path, subcategoria_dir)
        if not os.path.isdir(subcategoria_path):
            continue
            
        subcategoria_limpia = limpiar_subcategoria(subcategoria_dir)
        
        # Recorremos las carpetas de variantes de personajes
        for variante_dir in os.listdir(subcategoria_path):
            variante_path = os.path.join(subcategoria_path, variante_dir)
            if not os.path.isdir(variante_path):
                continue
                
            # Extraemos el nombre del personaje y el número de variante
            nombre_personaje, numero_variante = extraer_variante(variante_dir)
            
            # Buscamos todas las imágenes en la carpeta de variante
            imagenes_variante = []
            for file in sorted(os.listdir(variante_path)):
                if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    relative_path = os.path.relpath(os.path.join(variante_path, file), carpeta_base)
                    relative_path = relative_path.replace("\\", "/")
                    url = base_url + relative_path
                    imagenes_variante.append(url)
            
            # Si no hay imágenes, saltamos esta variante
            if not imagenes_variante:
                continue
                
            # Generamos el nombre del producto
            nombre_producto = f"{nombre_categoria} {nombre_personaje} #{numero_variante}"
            
            # Para Polaroids, lógica especial
            if categoria_dir == "Pol":
                if subcategoria_dir.lower() == "anime":
                    subcategoria_final = limpiar_nombre(file)
                    personaje_final = subcategoria_final
                else:
                    subcategoria_final = subcategoria_limpia
                    personaje_final = nombre_personaje
            else:
                subcategoria_final = subcategoria_limpia
                personaje_final = nombre_personaje
            
            # Generamos la lista de imágenes en formato Dart
            imagenes_dart = "[\n" + ",\n".join([f'      "{img_url}"' for img_url in imagenes_variante]) + "\n    ]"
            
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
print("📁 Estructura procesada: Categoría → Subcategoría → Variante_Personaje → Múltiples imágenes")