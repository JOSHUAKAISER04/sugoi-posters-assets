import os
import re
import tempfile
import shutil
from pathlib import Path
from collections import defaultdict

def normalize_name(name):
    """
    Normaliza un nombre eliminando separadores múltiples y caracteres problemáticos
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
    Extrae el nombre base y número de un nombre que puede tener varios formatos
    Ejemplos:
    - foto__1 -> (foto, 1)
    - foto_#_3 -> (foto, 3)
    - foto___2 -> (foto, 2)
    - foto -> (foto, None)
    """
    # Primero normalizar el nombre
    normalized = normalize_name(name)
    
    # Intentar extraer número al final (después de _ o #)
    match = re.match(r'^(.+?)[_#](\d+)$', normalized)
    if match:
        return match.group(1), int(match.group(2))
    
    # Si no hay número, devolver el nombre normalizado
    return normalized, None


def analyze_changes(directory_path):
    """
    Analiza y retorna todos los cambios que se harían sin ejecutarlos
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'}
    
    folder_changes = []
    image_changes = []
    
    # Analizar cambios en carpetas
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
                # Ordenar carpetas
                def sort_folder_key(folder):
                    if folder['number'] is not None:
                        return (0, folder['number'])
                    else:
                        return (-1, 0)
                
                folders.sort(key=sort_folder_key)
                
                # Generar nuevos nombres
                for i, folder in enumerate(folders, 1):
                    if len(folders) == 1:
                        # Si solo hay una carpeta, normalizarla sin número
                        new_name = base_name
                    else:
                        # Si hay múltiples, agregar número
                        new_name = f"{base_name}_{i}"
                    
                    if folder['original_name'] != new_name:
                        folder_changes.append({
                            'type': 'folder',
                            'directory': root,
                            'old_name': folder['original_name'],
                            'new_name': new_name,
                            'old_path': folder['path'],
                            'new_path': os.path.join(root, new_name),
                            'reason': 'normalización' if '__' in folder['original_name'] or '##' in folder['original_name'] else 'renumeración'
                        })
    
    # Analizar cambios en imágenes
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
            
            # Procesar grupos de imágenes
            for base_name, images in image_groups.items():
                if len(images) > 1 or (len(images) == 1 and images[0]['name_without_ext'] != base_name):
                    # Ordenar imágenes
                    def sort_key(image):
                        if image['number'] is not None:
                            return (0, image['number'])
                        else:
                            return (-1, 0)
                    
                    images.sort(key=sort_key)
                    
                    # Generar nuevos nombres
                    for i, image in enumerate(images, 1):
                        if len(images) == 1:
                            # Si solo hay una imagen, normalizarla sin número
                            new_name = f"{base_name}{image['extension']}"
                        else:
                            # Si hay múltiples, agregar número
                            new_name = f"{base_name}_{i}{image['extension']}"
                        
                        if image['original_name'] != new_name:
                            image_changes.append({
                                'type': 'image',
                                'directory': root,
                                'old_name': image['original_name'],
                                'new_name': new_name,
                                'old_path': image['full_path'],
                                'new_path': os.path.join(root, new_name),
                                'base_name': base_name,
                                'reason': 'normalización' if '__' in image['original_name'] or '##' in image['original_name'] else 'renumeración'
                            })
    
    return folder_changes, image_changes


def print_analysis(folder_changes, image_changes):
    """
    Imprime el análisis de cambios de forma organizada
    """
    print("\n" + "=" * 70)
    print("🔍 ANÁLISIS COMPLETO DE CAMBIOS")
    print("=" * 70)
    
    # Mostrar cambios en carpetas
    print("\n📁 CARPETAS A RENOMBRAR:")
    if folder_changes:
        current_dir = None
        normalization_count = 0
        renumbering_count = 0
        
        for change in folder_changes:
            if current_dir != change['directory']:
                current_dir = change['directory']
                print(f"\n   📂 En: {current_dir}")
            
            # Indicador especial para normalizaciones
            indicator = "🔧" if change['reason'] == 'normalización' else "🔢"
            print(f"      {indicator} {change['old_name']} → {change['new_name']}")
            
            if change['reason'] == 'normalización':
                normalization_count += 1
            else:
                renumbering_count += 1
        
        print(f"\n   📊 Total de carpetas a renombrar: {len(folder_changes)}")
        if normalization_count > 0:
            print(f"      🔧 Por normalización (__, ##, etc.): {normalization_count}")
        if renumbering_count > 0:
            print(f"      🔢 Por renumeración: {renumbering_count}")
    else:
        print("   ✅ No se requieren cambios en carpetas")
    
    # Mostrar cambios en imágenes
    print("\n🖼️  IMÁGENES A RENOMBRAR:")
    if image_changes:
        current_dir = None
        current_group = None
        normalization_count = 0
        renumbering_count = 0
        
        for change in image_changes:
            if current_dir != change['directory']:
                current_dir = change['directory']
                print(f"\n   📁 En: {current_dir}")
                current_group = None
            
            if current_group != change['base_name']:
                current_group = change['base_name']
                group_count = sum(1 for c in image_changes 
                                if c['directory'] == current_dir 
                                and c['base_name'] == current_group)
                print(f"      🖼️  Grupo '{current_group}' ({group_count} imágenes):")
            
            # Indicador especial para normalizaciones
            indicator = "🔧" if change['reason'] == 'normalización' else "🔢"
            print(f"         {indicator} {change['old_name']} → {change['new_name']}")
            
            if change['reason'] == 'normalización':
                normalization_count += 1
            else:
                renumbering_count += 1
        
        print(f"\n   📊 Total de imágenes a renombrar: {len(image_changes)}")
        if normalization_count > 0:
            print(f"      🔧 Por normalización (__, ##, etc.): {normalization_count}")
        if renumbering_count > 0:
            print(f"      🔢 Por renumeración: {renumbering_count}")
    else:
        print("   ✅ No se requieren cambios en imágenes")
    
    # Resumen total
    print("\n" + "=" * 70)
    print("📊 RESUMEN:")
    print(f"   • Carpetas a renombrar: {len(folder_changes)}")
    print(f"   • Imágenes a renombrar: {len(image_changes)}")
    print(f"   • Total de cambios: {len(folder_changes) + len(image_changes)}")
    print("\n   ℹ️  Leyenda:")
    print("      🔧 = Normalización de separadores (__, ##, etc.)")
    print("      🔢 = Renumeración consecutiva")
    print("=" * 70)


def execute_renaming(folder_changes, image_changes):
    """
    Ejecuta el renombrado basado en los cambios analizados
    """
    total_renamed_folders = 0
    total_renamed_images = 0
    
    # Renombrar carpetas
    if folder_changes:
        print("\n📁 Renombrando carpetas...")
        temp_mappings = {}
        
        # Paso 1: Renombrar a nombres temporales
        for change in folder_changes:
            temp_name = f"TEMP_{change['old_name']}_{hash(change['old_path']) % 10000}"
            temp_path = os.path.join(change['directory'], temp_name)
            
            try:
                os.rename(change['old_path'], temp_path)
                temp_mappings[temp_path] = change['new_path']
                print(f"   🔄 {change['old_name']} → {temp_name} (temporal)")
            except Exception as e:
                print(f"   ❌ Error renombrando carpeta {change['old_path']}: {e}")
        
        # Paso 2: Renombrar de temporales a nombres finales
        for temp_path, final_path in temp_mappings.items():
            try:
                os.rename(temp_path, final_path)
                print(f"   ✅ {os.path.basename(temp_path)} → {os.path.basename(final_path)}")
                total_renamed_folders += 1
            except Exception as e:
                print(f"   ❌ Error en renombrado final {temp_path}: {e}")
    
    # Renombrar imágenes
    if image_changes:
        print("\n🖼️  Renombrando imágenes...")
        
        # Agrupar cambios por directorio
        changes_by_dir = defaultdict(list)
        for change in image_changes:
            changes_by_dir[change['directory']].append(change)
        
        for directory, dir_changes in changes_by_dir.items():
            print(f"\n   📁 Procesando: {directory}")
            temp_mappings = {}
            
            # Paso 1: Renombrar a archivos temporales
            for change in dir_changes:
                temp_name = f"TEMP_{hash(change['old_path']) % 10000}{Path(change['old_name']).suffix}"
                temp_path = os.path.join(directory, temp_name)
                
                try:
                    os.rename(change['old_path'], temp_path)
                    temp_mappings[temp_path] = change['new_path']
                except Exception as e:
                    print(f"      ❌ Error en renombrado temporal: {e}")
            
            # Paso 2: Renombrar de temporales a nombres finales
            for temp_path, final_path in temp_mappings.items():
                try:
                    os.rename(temp_path, final_path)
                    print(f"      ✅ {os.path.basename(temp_path)} → {os.path.basename(final_path)}")
                    total_renamed_images += 1
                except Exception as e:
                    print(f"      ❌ Error en renombrado final: {e}")
    
    return total_renamed_images, total_renamed_folders


def main():
    print("🚀 NORMALIZADOR COMPLETO - CARPETAS E IMÁGENES v5.0")
    print("=" * 70)
    print("✨ Renombra carpetas E imágenes con numeración consecutiva")
    print("🛡️  Usa renombrado seguro para evitar conflictos")
    print("🔧 Maneja separadores problemáticos: __, ##, _#, etc.")
    print("🔍 Detecta y normaliza separadores múltiples")
    print("📋 Análisis previo obligatorio antes de cualquier cambio\n")
    
    # Solicitar directorio
    while True:
        directory = input("📂 Ingresa la ruta del directorio: ").strip()
        
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
    
    print(f"\n📁 Directorio seleccionado: {dir_path.absolute()}")
    
    # PASO 1: Analizar cambios
    print("\n⏳ Analizando archivos y carpetas...")
    try:
        folder_changes, image_changes = analyze_changes(str(dir_path))
    except Exception as e:
        print(f"\n❌ Error durante el análisis: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # PASO 2: Mostrar análisis
    print_analysis(folder_changes, image_changes)
    
    # Si no hay cambios, terminar
    if not folder_changes and not image_changes:
        print("\n✅ No se requieren cambios. ¡Todo está normalizado!")
        return
    
    # PASO 3: Confirmar ejecución
    print("\n" + "⚠️ " * 35)
    confirm = input("¿Deseas EJECUTAR el proceso de renombrado? (s/n): ").strip().lower()
    print("⚠️ " * 35)
    
    if confirm not in ['s', 'si', 'sí', 'y', 'yes']:
        print("\n❌ Operación cancelada. No se realizaron cambios.")
        return
    
    # PASO 4: Ejecutar renombrado
    print("\n🔄 Iniciando proceso de renombrado...")
    
    try:
        renamed_images, renamed_folders = execute_renaming(folder_changes, image_changes)
        
        print("\n" + "=" * 70)
        print("✅ ¡PROCESO COMPLETADO EXITOSAMENTE!")
        print("=" * 70)
        print(f"📊 Carpetas renombradas: {renamed_folders}")
        print(f"📊 Imágenes renombradas: {renamed_images}")
        print("🎉 Todo normalizado con numeración consecutiva (_1, _2, _3...)")
        print("🔧 Separadores múltiples (__, ##) normalizados correctamente")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error durante el renombrado: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
