import os
import re

# Configuración del repo
usuario = "JOSHUAKAISER04"
repositorio = "sugoi-posters-assets"
rama = "main"
carpeta_base = "."

# Definición de categorías, precios y descripciones
categorias = {
    "C-a": {"nombre": "Camisa",    "categoria": "Camisas",   "precio": "280", "descripcion": "Camisa de alta calidad inspirada en tu anime favorito. Ideal para el día a día o coleccionar como parte de tu pasión otaku."},
    "S-u": {"nombre": "Suéter",    "categoria": "Sueters",   "precio": "500", "descripcion": "Suéter cómodo y duradero con diseños únicos de tus animes favoritos. Ideal para mantenerte abrigado con estilo otaku."},
    "P-o": {"nombre": "Poster",    "categoria": "Posters",   "precio": "70",  "descripcion": "Poster con impresión premium para dar vida a tus espacios. Perfecto para decorar tu cuarto, oficina o rincón otaku."},
    "S-e": {"nombre": "Separador", "categoria": "Separadores","precio": "25",  "descripcion": "Separador de diseño exclusivo para que nunca pierdas la página en tus mangas y libros. Compacto, resistente y coleccionable."},
    "Pol": {"nombre": "Polaroid",  "categoria": "Polaroids", "precio": "20",  "descripcion": "Polaroid coleccionable con acabado especial. Llévate un recuerdo único de tu anime favorito en formato de bolsillo."},
}

# URL base
base_url = f"https://raw.githubusercontent.com/{usuario}/{repositorio}/{rama}/"

productos = []
contadores = {}

def limpiar_nombre(nombre_archivo):
    nombre = os.path.splitext(nombre_archivo)[0]
    # quitar sufijos tipo (1) o _1 y convertir "Name_1" -> "Name #1" solo para mostrar si fuera necesario
    nombre = re.sub(r"[_\s]*\(?(\d+)\)?$", r" #\1", nombre)
    nombre = re.sub(r"[_]+", " ", nombre)
    nombre = re.sub(r"\s{2,}", " ", nombre).strip()
    return nombre

def formatear_subcategoria(nombre_carpeta):
    """
    Formatea subcategorías conservando acrónimos (todos en mayúscula) y Title Case para el resto.
    Ej: "DC_Comics" -> "DC Comics", "one_piece" -> "One Piece"
    """
    partes = re.split(r'[_\-]+', nombre_carpeta)
    partes_formateadas = []
    for p in partes:
        p_stripped = p.strip()
        if not p_stripped:
            continue
        # si la parte está ya en mayúsculas (ej. "DC"), la dejamos así
        if p_stripped.isupper():
            partes_formateadas.append(p_stripped)
        else:
            partes_formateadas.append(p_stripped.title())
    return " ".join(partes_formateadas)

def extraer_variante(nombre_carpeta):
    match = re.match(r"^(.+?)[_\s]*(\d+)$", nombre_carpeta)
    if match:
        nombre_personaje = match.group(1).replace("_", " ").strip()
        numero_variante = int(match.group(2))
        return nombre_personaje, numero_variante
    return nombre_carpeta.replace("_", " ").strip(), None


# --- RECORRIDO DE CARPETAS ---
for categoria_dir in sorted(os.listdir(carpeta_base)):
    if categoria_dir not in categorias:
        continue

    categoria_path = os.path.join(carpeta_base, categoria_dir)
    if not os.path.isdir(categoria_path):
        continue

    tipo = categorias[categoria_dir]
    nombre_categoria = tipo["nombre"]       # "Camisa", "Suéter", "Poster", "Polaroid", ...
    categoria_plural = tipo["categoria"]   # "Camisas", "Sueters", ...
    precio = tipo["precio"]
    descripcion = tipo["descripcion"]

    # Aplicar la lógica de 'personalizados' a C-a, S-u, P-o y Pol
    if categoria_dir in ("C-a", "S-u", "P-o", "Pol"):
        subcarpetas = sorted(os.listdir(categoria_path))
        personales = [s for s in subcarpetas if s.lower().startswith("1_") or "personaliz" in s.lower()]
        normales = [s for s in subcarpetas if s not in personales]
        orden_final = personales + normales

        for subcategoria_dir in orden_final:
            subcategoria_path = os.path.join(categoria_path, subcategoria_dir)
            if not os.path.isdir(subcategoria_path):
                continue

            es_personalizada_directa = subcategoria_dir.lower().startswith("1_") or "personaliz" in subcategoria_dir.lower()

            if es_personalizada_directa:
                imagenes = [
                    base_url + os.path.relpath(os.path.join(subcategoria_path, f), carpeta_base).replace("\\", "/")
                    for f in sorted(os.listdir(subcategoria_path))
                    if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
                ]
                if not imagenes:
                    continue

                adj = "Personalizada" if categoria_dir == "C-a" else "Personalizado"
                nombre_producto = f"{nombre_categoria} {adj} #1"
                imagenes_dart = "[\n" + ",\n".join([f'      "{img}"' for img in imagenes]) + "\n    ]"
                productos.append(f'''  Product(
    nombre: "{nombre_producto}",
    precio: "{precio}",
    descripcion: "{descripcion}",
    categoria: "{categoria_plural}",
    imagenes: {imagenes_dart},
    subcategoria: "",
  ),''')
                continue

            subcategoria_limpia = formatear_subcategoria(subcategoria_dir)

            internas = [v for v in sorted(os.listdir(subcategoria_path)) if os.path.isdir(os.path.join(subcategoria_path, v))]
            archivos_directos = [f for f in sorted(os.listdir(subcategoria_path))
                                 if os.path.isfile(os.path.join(subcategoria_path, f)) and f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]

            # 1) Carpetas internas (ej. One_Piece/Brook Wanted)
            if internas:
                for variante_dir in internas:
                    variante_path = os.path.join(subcategoria_path, variante_dir)
                    if not os.path.isdir(variante_path):
                        continue

                    archivos_variante = [f for f in sorted(os.listdir(variante_path)) if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
                    if archivos_variante:
                        nombre_base, numero = extraer_variante(variante_dir)
                        imagenes_variante = [
                            base_url + os.path.relpath(os.path.join(variante_path, f), carpeta_base).replace("\\", "/")
                            for f in archivos_variante
                        ]
                        sufijo = f" #{numero}" if numero else " #1"
                        nombre_producto = f"{nombre_categoria} {nombre_base}{sufijo}"
                        imagenes_dart = "[\n" + ",\n".join([f'      "{img}"' for img in imagenes_variante]) + "\n    ]"
                        productos.append(f'''  Product(
    nombre: "{nombre_producto}",
    precio: "{precio}",
    descripcion: "{descripcion}",
    categoria: "{categoria_plural}",
    imagenes: {imagenes_dart},
    subcategoria: "{subcategoria_limpia}",
  ),''')

            # 2) Archivos directos en la subcategoria
            if archivos_directos:
                if categoria_dir == "Pol":
                    # Polaroids: 1 product por archivo; si la carpeta es 'anime', subcategoria = personaje
                    for file in archivos_directos:
                        relative_path = os.path.relpath(os.path.join(subcategoria_path, file), carpeta_base).replace("\\", "/")
                        url = base_url + relative_path
                        personaje = limpiar_nombre(file)
                        subcategoria_final = personaje if subcategoria_dir.lower() == "anime" else subcategoria_limpia

                        clave = f"{categoria_dir}-{subcategoria_final.lower()}-{personaje.lower()}"
                        contadores[clave] = contadores.get(clave, 0) + 1
                        numero = contadores[clave]
                        if numero > 1 and f"#{numero}" not in personaje:
                            nombre_producto = f"{nombre_categoria} {personaje} #{numero}"
                        else:
                            nombre_producto = f"{nombre_categoria} {personaje}"

                        imagenes_dart = "[\n" + f'      "{url}"' + "\n    ]"
                        productos.append(f'''  Product(
    nombre: "{nombre_producto}",
    precio: "{precio}",
    descripcion: "{descripcion}",
    categoria: "{categoria_plural}",
    imagenes: {imagenes_dart},
    subcategoria: "{subcategoria_final}",
  ),''')

                elif categoria_dir == "P-o":
                    # Posters: UN producto por archivo directo; subcategoria = carpeta padre (formateada)
                    for file in archivos_directos:
                        relative_path = os.path.relpath(os.path.join(subcategoria_path, file), carpeta_base).replace("\\", "/")
                        url = base_url + relative_path
                        personaje = limpiar_nombre(file)               # e.g. "Superman"
                        subcategoria_final = subcategoria_limpia       # e.g. "DC Comics"

                        clave = f"{categoria_dir}-{subcategoria_final.lower()}-{personaje.lower()}"
                        contadores[clave] = contadores.get(clave, 0) + 1
                        numero = contadores[clave]
                        if numero > 1 and f"#{numero}" not in personaje:
                            nombre_producto = f"{nombre_categoria} {personaje} #{numero}"
                        else:
                            nombre_producto = f"{nombre_categoria} {personaje}"

                        imagenes_dart = "[\n" + f'      "{url}"' + "\n    ]"
                        productos.append(f'''  Product(
    nombre: "{nombre_producto}",
    precio: "{precio}",
    descripcion: "{descripcion}",
    categoria: "{categoria_plural}",
    imagenes: {imagenes_dart},
    subcategoria: "{subcategoria_final}",
  ),''')

                else:
                    # Camisas/Suéters: agrupar archivos directos en UN producto por subcategoria
                    imagenes = [
                        base_url + os.path.relpath(os.path.join(subcategoria_path, f), carpeta_base).replace("\\", "/")
                        for f in archivos_directos
                    ]
                    nombre_producto = f"{nombre_categoria} {subcategoria_limpia} #1"
                    imagenes_dart = "[\n" + ",\n".join([f'      "{img}"' for img in imagenes]) + "\n    ]"
                    productos.append(f'''  Product(
    nombre: "{nombre_producto}",
    precio: "{precio}",
    descripcion: "{descripcion}",
    categoria: "{categoria_plural}",
    imagenes: {imagenes_dart},
    subcategoria: "{subcategoria_limpia}",
  ),''')

    # Resto de categorías (S-e, etc.) mantienen su lógica original
    else:
        for subcategoria_dir in sorted(os.listdir(categoria_path)):
            subcategoria_path = os.path.join(categoria_path, subcategoria_dir)
            if not os.path.isdir(subcategoria_path):
                continue

            subcategoria_limpia = formatear_subcategoria(subcategoria_dir)

            for file in sorted(os.listdir(subcategoria_path)):
                if not file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    continue

                relative_path = os.path.relpath(os.path.join(subcategoria_path, file), carpeta_base).replace("\\", "/")
                url = base_url + relative_path
                personaje = limpiar_nombre(file)

                subcategoria_final = subcategoria_limpia
                personaje_final = personaje

                clave = f"{categoria_dir}-{subcategoria_final.lower()}-{personaje_final.lower()}"
                contadores[clave] = contadores.get(clave, 0) + 1
                numero = contadores[clave]
                if numero > 1 and f"#{numero}" not in personaje_final:
                    nombre_producto = f"{nombre_categoria} {personaje_final} #{numero}"
                else:
                    nombre_producto = f"{nombre_categoria} {personaje_final}"

                imagenes_dart = "[\n" + f'      "{url}"' + "\n    ]"
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
