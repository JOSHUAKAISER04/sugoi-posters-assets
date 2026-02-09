import os
import re
import shutil
from pathlib import Path
from collections import defaultdict

# ============================================================================
# PASO 1: NORMALIZACIÓN DE NOMBRES (COMPATIBLE CON PRODUCTOS.PY)
# ============================================================================

def normalize_name(name):
    """
    Normaliza un nombre eliminando separadores múltiples
    Compatible con la lógica de productos.py
    """
    # Reemplazar múltiples guiones bajos consecutivos por uno solo
    name = re.sub(r'_+', '_', name)
    # Reemplazar múltiples # consecutivos por uno solo
    name = re.sub(r'#+', '#', name)
    # Eliminar guiones bajos o # al final
    name = re.sub(r'[_#]+$', '', name)
    # Eliminar guiones bajos o # al inicio
    name = re.sub(r'^[_#]+', '', name)
    return name


def extract_base_name_and_number(name):
    """
    Extrae el nombre base y número de una carpeta/archivo
    Compatible con extraer_variante() de productos.py
    """
    normalized = normalize_name(name)
    match = re.match(r'^(.+?)[_#](\d+)$', normalized)
    if match:
        return match.group(1), int(match.group(2))
    return normalized, None


def analyze_normalization(directory_path):
    """
    Analiza qué archivos y carpetas necesitan normalización
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'}
    folder_changes = []
    image_changes = []
    
    # Analizar carpetas
    for root, dirs, files in os.walk(directory_path, topdown=False):
        folder_groups = defaultdict(list)
        
        for folder_name in dirs:
            folder_path = os.path.join(root, folder_name)
            base_name, number = extract_base_name_and_number(folder_name)
            
            folder_groups[base_name].append({
                'original_name': folder_name,
                'base_name': base_name,
                'number': number,
                'path': folder_path
            })
        
        # Procesar grupos de carpetas
        for base_name, folders in folder_groups.items():
            if len(folders) > 1 or (len(folders) == 1 and folders[0]['original_name'] != base_name):
                folders.sort(key=lambda f: (0, f['number']) if f['number'] is not None else (-1, 0))
                
                for i, folder in enumerate(folders, 1):
                    if len(folders) == 1:
                        new_name = base_name
                    else:
                        new_name = f"{base_name}_{i}"
                    
                    if folder['original_name'] != new_name:
                        folder_changes.append({
                            'directory': root,
                            'old_name': folder['original_name'],
                            'new_name': new_name,
                            'old_path': folder['path'],
                            'new_path': os.path.join(root, new_name)
                        })
    
    # Analizar imágenes
    for root, dirs, files in os.walk(directory_path):
        image_files = [f for f in files if Path(f).suffix.lower() in image_extensions]
        
        if image_files:
            image_groups = defaultdict(list)
            
            for image_file in image_files:
                name_without_ext = Path(image_file).stem
                extension = Path(image_file).suffix
                base_name, number = extract_base_name_and_number(name_without_ext)
                
                image_groups[base_name].append({
                    'original_name': image_file,
                    'name_without_ext': name_without_ext,
                    'base_name': base_name,
                    'number': number,
                    'extension': extension,
                    'full_path': os.path.join(root, image_file)
                })
            
            for base_name, images in image_groups.items():
                if len(images) > 1 or (len(images) == 1 and images[0]['name_without_ext'] != base_name):
                    images.sort(key=lambda i: (0, i['number']) if i['number'] is not None else (-1, 0))
                    
                    for i, image in enumerate(images, 1):
                        if len(images) == 1:
                            new_name = f"{base_name}{image['extension']}"
                        else:
                            new_name = f"{base_name}_{i}{image['extension']}"
                        
                        if image['original_name'] != new_name:
                            image_changes.append({
                                'directory': root,
                                'old_name': image['original_name'],
                                'new_name': new_name,
                                'old_path': image['full_path'],
                                'new_path': os.path.join(root, new_name)
                            })
    
    return folder_changes, image_changes


def execute_normalization(folder_changes, image_changes):
    """
    Ejecuta la normalización de nombres
    """
    renamed_folders = 0
    renamed_images = 0
    
    # Renombrar carpetas
    if folder_changes:
        print("\n📁 Normalizando nombres de carpetas...")
        temp_mappings = {}
        
        for change in folder_changes:
            temp_name = f"TEMP_{change['old_name']}_{hash(change['old_path']) % 10000}"
            temp_path = os.path.join(change['directory'], temp_name)
            
            try:
                os.rename(change['old_path'], temp_path)
                temp_mappings[temp_path] = change['new_path']
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        for temp_path, final_path in temp_mappings.items():
            try:
                os.rename(temp_path, final_path)
                print(f"   ✅ {os.path.basename(temp_path)} → {os.path.basename(final_path)}")
                renamed_folders += 1
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    # Renombrar imágenes
    if image_changes:
        print("\n🖼️  Normalizando nombres de imágenes...")
        changes_by_dir = defaultdict(list)
        for change in image_changes:
            changes_by_dir[change['directory']].append(change)
        
        for directory, dir_changes in changes_by_dir.items():
            temp_mappings = {}
            
            for change in dir_changes:
                temp_name = f"TEMP_{hash(change['old_path']) % 10000}{Path(change['old_name']).suffix}"
                temp_path = os.path.join(directory, temp_name)
                
                try:
                    os.rename(change['old_path'], temp_path)
                    temp_mappings[temp_path] = change['new_path']
                except Exception as e:
                    print(f"      ❌ Error: {e}")
            
            for temp_path, final_path in temp_mappings.items():
                try:
                    os.rename(temp_path, final_path)
                    renamed_images += 1
                except Exception as e:
                    print(f"      ❌ Error: {e}")
    
    return renamed_images, renamed_folders


# ============================================================================
# PASO 2: ORGANIZACIÓN DE IMÁGENES EN CARPETAS
# ============================================================================

def analyze_organization(carpeta_trabajo):
    """
    Analiza qué imágenes necesitan ser organizadas en carpetas
    """
    extensiones = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
    
    archivos = [f for f in os.listdir(carpeta_trabajo)
                if f.lower().endswith(extensiones) and os.path.isfile(os.path.join(carpeta_trabajo, f))]
    
    if not archivos:
        return []
    
    changes = []
    for archivo in archivos:
        nombre, _ = os.path.splitext(archivo)
        ruta_carpeta = os.path.join(carpeta_trabajo, nombre)
        
        changes.append({
            'file': archivo,
            'folder': nombre,
            'source': os.path.join(carpeta_trabajo, archivo),
            'dest_folder': ruta_carpeta,
            'dest_file': os.path.join(ruta_carpeta, archivo)
        })
    
    return changes


def execute_organization(changes):
    """
    Ejecuta la organización de imágenes
    """
    organized = 0
    
    if changes:
        print("\n📂 Organizando imágenes en carpetas...")
        
        for change in changes:
            if not os.path.exists(change['dest_folder']):
                os.makedirs(change['dest_folder'])
            
            try:
                shutil.move(change['source'], change['dest_file'])
                print(f"   ✅ {change['file']} → {change['folder']}/")
                organized += 1
            except Exception as e:
                print(f"   ❌ Error moviendo {change['file']}: {e}")
    
    return organized


# ============================================================================
# PASO 3: GENERACIÓN DE PRODUCTOS (COMPATIBLE CON PRODUCTOS.PY)
# ============================================================================

# Configuración del repo
usuario = "JOSHUAKAISER04"
repositorio = "sugoi-posters-assets"
rama = "main"

categorias = {
    "C-a": {"nombre": "Camisa", "categoria": "Camisas", "precio": "280", "descripcion": "Camisa de alta calidad inspirada en tu anime favorito."},
    "S-u": {"nombre": "Suéter", "categoria": "Sueters", "precio": "500", "descripcion": "Suéter cómodo y duradero con diseños únicos."},
    "P-o": {"nombre": "Poster", "categoria": "Posters", "precio": "70", "descripcion": "Poster con impresión premium."},
    "S-e": {"nombre": "Separador", "categoria": "Separadores", "precio": "25", "descripcion": "Separador de diseño exclusivo."},
    "Pol": {"nombre": "Polaroid", "categoria": "Polaroids", "precio": "20", "descripcion": "Polaroid coleccionable con acabado especial."},
}


def limpiar_nombre(nombre_archivo):
    """Limpia el nombre de archivo para mostrar (de productos.py)"""
    nombre = os.path.splitext(nombre_archivo)[0]
    nombre = re.sub(r"[_\s]*\(?(\d+)\)?$", r" #\1", nombre)
    nombre = re.sub(r"[_]+", " ", nombre)
    nombre = re.sub(r"\s{2,}", " ", nombre).strip()
    return nombre


def normalize_hashes(name):
    """Normaliza hashes en nombres (de productos.py)"""
    s = name
    s = re.sub(r"#\s+#", "#", s)
    s = re.sub(r"#(?!\d)", "", s)
    s = re.sub(r"\s{2,}", " ", s).strip()
    return s


def formatear_subcategoria(nombre_carpeta):
    """Formatea subcategorías (de productos.py)"""
    partes = re.split(r'[_\-]+', nombre_carpeta)
    partes_formateadas = []
    for p in partes:
        p_stripped = p.strip()
        if not p_stripped:
            continue
        if p_stripped.isupper():
            partes_formateadas.append(p_stripped)
        else:
            partes_formateadas.append(p_stripped.title())
    return " ".join(partes_formateadas)


def extraer_variante(nombre_carpeta):
    """Extrae variante de carpeta (de productos.py)"""
    match = re.match(r"^(.+?)[_\s]*(\d+)$", nombre_carpeta)
    if match:
        nombre_personaje = match.group(1).replace("_", " ").strip()
        numero_variante = int(match.group(2))
        return nombre_personaje, numero_variante
    return nombre_carpeta.replace("_", " ").strip(), 0


def generar_productos(carpeta_base):
    """
    Genera el archivo products.dart basado en la estructura de carpetas
    """
    base_url = f"https://raw.githubusercontent.com/{usuario}/{repositorio}/{rama}/"
    productos = []
    contadores = {}
    
    print("\n📦 Generando productos...")
    
    for categoria_dir in sorted(os.listdir(carpeta_base)):
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
                
                # Carpetas internas
                if internas:
                    for variante_dir in internas:
                        variante_path = os.path.join(subcategoria_path, variante_dir)
                        if not os.path.isdir(variante_path):
                            continue
                        
                        archivos_variante = [f for f in sorted(os.listdir(variante_path)) if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
                        if archivos_variante:
                            nombre_base, numero_carpeta = extraer_variante(variante_dir)
                            nombre_base = normalize_hashes(nombre_base)
                            
                            imagenes_variante = [
                                base_url + os.path.relpath(os.path.join(variante_path, f), carpeta_base).replace("\\", "/")
                                for f in archivos_variante
                            ]
                            
                            if categoria_dir in ("C-a", "S-u"):
                                numero_display = numero_carpeta + 1
                            else:
                                numero_display = numero_carpeta if numero_carpeta > 0 else 1
                            
                            nombre_producto = f"{nombre_categoria} {nombre_base} #{numero_display}"
                            imagenes_dart = "[\n" + ",\n".join([f'      "{img}"' for img in imagenes_variante]) + "\n    ]"
                            productos.append(f'''  Product(
    nombre: "{nombre_producto}",
    precio: "{precio}",
    descripcion: "{descripcion}",
    categoria: "{categoria_plural}",
    imagenes: {imagenes_dart},
    subcategoria: "{subcategoria_limpia}",
  ),''')
                
                # Archivos directos
                if archivos_directos:
                    if categoria_dir == "Pol":
                        for file in archivos_directos:
                            relative_path = os.path.relpath(os.path.join(subcategoria_path, file), carpeta_base).replace("\\", "/")
                            url = base_url + relative_path
                            personaje = limpiar_nombre(file)
                            personaje = normalize_hashes(personaje)
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
                        for file in archivos_directos:
                            relative_path = os.path.relpath(os.path.join(subcategoria_path, file), carpeta_base).replace("\\", "/")
                            url = base_url + relative_path
                            personaje = limpiar_nombre(file)
                            personaje = normalize_hashes(personaje)
                            subcategoria_final = subcategoria_limpia
                            
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
                    personaje = normalize_hashes(personaje)
                    
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
    
    return productos


# ============================================================================
# FUNCIÓN PRINCIPAL - WORKFLOW INTEGRADO
# ============================================================================

def main():
    print("=" * 80)
    print("🚀 WORKFLOW COMPLETO DE PREPARACIÓN Y GENERACIÓN DE PRODUCTOS")
    print("=" * 80)
    print("Este script realizará 3 pasos:")
    print("  1️⃣  Normalización de nombres (elimina __, ##, renumera)")
    print("  2️⃣  Organización de imágenes (crea carpetas por imagen)")
    print("  3️⃣  Generación de products.dart (sin duplicados)")
    print("=" * 80)
    
    # Solicitar directorio
    while True:
        directory = input("\n📂 Ingresa la ruta del directorio: ").strip()
        
        if not directory:
            print("❌ Por favor, ingresa una ruta válida.")
            continue
        
        dir_path = Path(directory)
        
        if not dir_path.exists():
            print("❌ El directorio no existe.")
            continue
        
        if not dir_path.is_dir():
            print("❌ La ruta no es un directorio.")
            continue
        
        break
    
    print(f"\n📁 Directorio: {dir_path.absolute()}")
    
    # ========================================================================
    # PASO 1: NORMALIZACIÓN
    # ========================================================================
    print("\n" + "=" * 80)
    print("PASO 1: ANÁLISIS DE NORMALIZACIÓN")
    print("=" * 80)
    
    folder_changes, image_changes = analyze_normalization(str(dir_path))
    
    if folder_changes or image_changes:
        print(f"\n📊 Cambios detectados:")
        print(f"   • Carpetas a normalizar: {len(folder_changes)}")
        print(f"   • Imágenes a normalizar: {len(image_changes)}")
        
        if folder_changes:
            print("\n📁 Vista previa de carpetas:")
            for i, change in enumerate(folder_changes[:5], 1):
                print(f"   {i}. {change['old_name']} → {change['new_name']}")
            if len(folder_changes) > 5:
                print(f"   ... y {len(folder_changes) - 5} más")
        
        if image_changes:
            print("\n🖼️  Vista previa de imágenes:")
            for i, change in enumerate(image_changes[:5], 1):
                print(f"   {i}. {change['old_name']} → {change['new_name']}")
            if len(image_changes) > 5:
                print(f"   ... y {len(image_changes) - 5} más")
        
        confirm = input("\n¿Ejecutar normalización? (s/n): ").strip().lower()
        if confirm in ['s', 'si', 'sí', 'y', 'yes']:
            renamed_images, renamed_folders = execute_normalization(folder_changes, image_changes)
            print(f"\n✅ Normalización completada: {renamed_folders} carpetas, {renamed_images} imágenes")
        else:
            print("⏭️  Normalización omitida")
    else:
        print("\n✅ No se requiere normalización")
    
    # ========================================================================
    # PASO 2: ORGANIZACIÓN
    # ========================================================================
    print("\n" + "=" * 80)
    print("PASO 2: ORGANIZACIÓN DE IMÁGENES")
    print("=" * 80)
    
    org_mode = input("\n¿Organizar imágenes en carpetas individuales? (s/n): ").strip().lower()
    
    if org_mode in ['s', 'si', 'sí', 'y', 'yes']:
        # Preguntar si organizar todo o una subcarpeta específica
        print("\nOpciones:")
        print("  1. Organizar todo el directorio recursivamente")
        print("  2. Seleccionar una carpeta específica")
        
        opcion = input("\nSelecciona una opción (1/2): ").strip()
        
        if opcion == "2":
            subcarpetas = [f for f in os.listdir(str(dir_path)) if os.path.isdir(os.path.join(str(dir_path), f))]
            if subcarpetas:
                print("\nSubcarpetas disponibles:")
                for i, sub in enumerate(subcarpetas, 1):
                    print(f"  {i}. {sub}")
                
                sel = input("\nSelecciona el número: ").strip()
                if sel.isdigit() and 1 <= int(sel) <= len(subcarpetas):
                    carpeta_trabajo = os.path.join(str(dir_path), subcarpetas[int(sel) - 1])
                else:
                    carpeta_trabajo = str(dir_path)
            else:
                carpeta_trabajo = str(dir_path)
        else:
            carpeta_trabajo = str(dir_path)
        
        org_changes = analyze_organization(carpeta_trabajo)
        
        if org_changes:
            print(f"\n📊 Se organizarán {len(org_changes)} imágenes")
            print("\nVista previa:")
            for i, change in enumerate(org_changes[:5], 1):
                print(f"   {i}. {change['file']} → {change['folder']}/")
            if len(org_changes) > 5:
                print(f"   ... y {len(org_changes) - 5} más")
            
            confirm = input("\n¿Ejecutar organización? (s/n): ").strip().lower()
            if confirm in ['s', 'si', 'sí', 'y', 'yes']:
                organized = execute_organization(org_changes)
                print(f"\n✅ Organización completada: {organized} imágenes")
            else:
                print("⏭️  Organización omitida")
        else:
            print("\n✅ No hay imágenes sueltas para organizar")
    else:
        print("⏭️  Organización omitida")
    
    # ========================================================================
    # PASO 3: GENERACIÓN DE PRODUCTOS
    # ========================================================================
    print("\n" + "=" * 80)
    print("PASO 3: GENERACIÓN DE PRODUCTOS")
    print("=" * 80)
    
    generate = input("\n¿Generar archivo products.dart? (s/n): ").strip().lower()
    
    if generate in ['s', 'si', 'sí', 'y', 'yes']:
        try:
            productos = generar_productos(str(dir_path))
            
            output_file = os.path.join(str(dir_path), "products.dart")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("const List<Product> productos = [\n")
                f.write("\n".join(productos))
                f.write("\n];\n")
            
            print(f"\n✅ Archivo generado: {output_file}")
            print(f"📦 Total de productos: {len(productos)}")
            
            # Detectar posibles duplicados
            nombres_productos = [p.split('nombre: "')[1].split('"')[0] for p in productos if 'nombre: "' in p]
            duplicados = [n for n in nombres_productos if nombres_productos.count(n) > 1]
            
            if duplicados:
                print(f"\n⚠️  ADVERTENCIA: Se detectaron {len(set(duplicados))} nombres duplicados:")
                for dup in set(duplicados)[:5]:
                    print(f"   • {dup}")
            else:
                print("\n✅ No se detectaron productos duplicados")
                
        except Exception as e:
            print(f"\n❌ Error generando productos: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("⏭️  Generación de productos omitida")
    
    # ========================================================================
    # RESUMEN FINAL
    # ========================================================================
    print("\n" + "=" * 80)
    print("✅ WORKFLOW COMPLETADO")
    print("=" * 80)
    print("Tus archivos están listos para ser usados con productos.py")
    print("=" * 80)


if __name__ == "__main__":
    main()
