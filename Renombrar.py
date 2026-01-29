import os
import re
from collections import defaultdict

# Extensiones de imagen que se procesarán
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')

def normalize_name(name):
    """Normaliza un nombre reemplazando espacios y # por _"""
    name = re.sub(r'[ #]+', '_', name)
    name = re.sub(r'_+', '_', name)  # Reemplazar múltiples _ consecutivos
    return name.strip('_')

def extract_base_and_number(filename):
    """Extrae el nombre base y número de un archivo o carpeta"""
    # Para archivos, quitar extensión primero
    name, ext = os.path.splitext(filename) if '.' in filename else (filename, '')
    
    # Buscar número al final del nombre
    match = re.search(r'_(\d+)$', name)
    if match:
        base = name[:match.start()]
        number = int(match.group(1))
    else:
        base = name
        number = 0  # 0 significa sin número
    
    return base, number, ext

def analyze_and_plan_changes(root_dir):
    """
    Analiza la estructura de directorios y planifica cambios necesarios
    Retorna: (planificados_archivos, planificadas_carpetas, conflictos_encontrados)
    """
    planificados_archivos = []  # (old_path, new_path)
    planificadas_carpetas = []  # (old_path, new_path)
    conflictos_encontrados = []
    
    # Primero analizamos la estructura actual
    for root, dirs, files in os.walk(root_dir, topdown=False):
        # Para cada directorio, analizar archivos
        archivos_por_base = defaultdict(list)
        
        for file in files:
            if file.lower().endswith(IMAGE_EXTENSIONS):
                base, number, ext = extract_base_and_number(file)
                archivos_por_base[base].append((file, number, ext))
        
        # Analizar conflictos y planificar cambios para archivos
        for base, archivos in archivos_por_base.items():
            if len(archivos) > 1:
                # Ordenar por número actual
                archivos_ordenados = sorted(archivos, key=lambda x: x[1])
                
                # Recolectar información de conflicto
                nombres_actuales = [a[0] for a in archivos_ordenados]
                sugerencias = []
                
                # Planificar nuevos nombres con numeración consecutiva
                for i, (nombre_actual, num_actual, ext) in enumerate(archivos_ordenados, 1):
                    nuevo_nombre = f"{base}_{i}{ext}" if i > 0 else f"{base}{ext}"
                    
                    # Solo planificar cambio si el nombre es diferente
                    if nuevo_nombre != nombre_actual:
                        old_path = os.path.join(root, nombre_actual)
                        new_path = os.path.join(root, nuevo_nombre)
                        planificados_archivos.append((old_path, new_path))
                    
                    sugerencias.append(f"{nombre_actual} -> {nuevo_nombre}")
                
                conflictos_encontrados.append({
                    'ruta': root,
                    'tipo': 'archivos',
                    'base': base,
                    'nombres': nombres_actuales,
                    'sugerencias': sugerencias
                })
        
        # Analizar carpetas
        carpetas_por_base = defaultdict(list)
        for dir_name in dirs:
            base, number, _ = extract_base_and_number(dir_name)
            carpetas_por_base[base].append((dir_name, number))
        
        # Analizar conflictos y planificar cambios para carpetas
        for base, carpetas in carpetas_por_base.items():
            if len(carpetas) > 1:
                # Ordenar por número actual
                carpetas_ordenadas = sorted(carpetas, key=lambda x: x[1])
                
                # Recolectar información de conflicto
                nombres_actuales = [c[0] for c in carpetas_ordenadas]
                sugerencias = []
                
                # Planificar nuevos nombres con numeración consecutiva
                for i, (nombre_actual, num_actual) in enumerate(carpetas_ordenadas, 1):
                    nuevo_nombre = f"{base}_{i}" if i > 0 else base
                    
                    # Solo planificar cambio si el nombre es diferente
                    if nuevo_nombre != nombre_actual:
                        old_path = os.path.join(root, nombre_actual)
                        new_path = os.path.join(root, nuevo_nombre)
                        planificadas_carpetas.append((old_path, new_path))
                    
                    sugerencias.append(f"{nombre_actual} -> {nuevo_nombre}")
                
                conflictos_encontrados.append({
                    'ruta': root,
                    'tipo': 'carpetas',
                    'base': base,
                    'nombres': nombres_actuales,
                    'sugerencias': sugerencias
                })
    
    return planificados_archivos, planificadas_carpetas, conflictos_encontrados

def show_conflicts(conflictos):
    """Muestra los conflictos encontrados"""
    if not conflictos:
        print("\n✅ No se encontraron conflictos que resolver.")
        return
    
    print(f"\n=== SE ENCONTRARON {len(conflictos)} CONFLICTOS ===")
    
    for i, conflicto in enumerate(conflictos, 1):
        print(f"\n{i}. En '{conflicto['ruta']}' se encontraron estos nombres similares:")
        for nombre in conflicto['nombres']:
            print(f"   - {nombre}")
        
        print("   Sugerencias para evitar conflictos:")
        for sugerencia in conflicto['sugerencias']:
            print(f"     {sugerencia}")

def apply_changes(archivos_planificados, carpetas_planificadas):
    """Aplica los cambios planificados"""
    cambios_exitosos = 0
    cambios_fallidos = 0
    
    print("\n=== APLICANDO CAMBIOS ===")
    
    # Aplicar cambios en archivos primero
    if archivos_planificados:
        print("\n📁 Renombrando archivos:")
        for old_path, new_path in archivos_planificados:
            try:
                # Verificar que el archivo aún existe
                if os.path.exists(old_path):
                    # Verificar que no estamos creando un duplicado
                    if not os.path.exists(new_path):
                        os.rename(old_path, new_path)
                        print(f"   ✅ {os.path.basename(old_path)} -> {os.path.basename(new_path)}")
                        cambios_exitosos += 1
                    else:
                        print(f"   ⚠️  {os.path.basename(old_path)} -> {os.path.basename(new_path)} (el destino ya existe, se omite)")
                        cambios_fallidos += 1
                else:
                    print(f"   ❌ {old_path} (el archivo ya no existe)")
                    cambios_fallidos += 1
            except Exception as e:
                print(f"   ❌ Error al renombrar {old_path}: {e}")
                cambios_fallidos += 1
    
    # Aplicar cambios en carpetas (ordenar por profundidad primero)
    if carpetas_planificadas:
        print("\n📂 Renombrando carpetas:")
        # Ordenar por profundidad (rutas más largas primero)
        carpetas_planificadas.sort(key=lambda x: len(x[0]), reverse=True)
        
        for old_path, new_path in carpetas_planificadas:
            try:
                # Verificar que la carpeta aún existe
                if os.path.exists(old_path):
                    # Verificar que no estamos creando un duplicado
                    if not os.path.exists(new_path):
                        os.rename(old_path, new_path)
                        print(f"   ✅ {os.path.basename(old_path)} -> {os.path.basename(new_path)}")
                        cambios_exitosos += 1
                    else:
                        print(f"   ⚠️  {os.path.basename(old_path)} -> {os.path.basename(new_path)} (el destino ya existe, se omite)")
                        cambios_fallidos += 1
                else:
                    print(f"   ❌ {old_path} (la carpeta ya no existe)")
                    cambios_fallidos += 1
            except Exception as e:
                print(f"   ❌ Error al renombrar {old_path}: {e}")
                cambios_fallidos += 1
    
    return cambios_exitosos, cambios_fallidos

def show_summary(conflictos, cambios_exitosos, cambios_fallidos):
    """Muestra un resumen del proceso"""
    print("\n" + "="*50)
    print("📊 RESUMEN DEL PROCESO")
    print("="*50)
    
    total_conflictos = len(conflictos)
    total_cambios = cambios_exitosos + cambios_fallidos
    
    print(f"\n📈 Conflictos detectados: {total_conflictos}")
    print(f"✅ Cambios aplicados exitosamente: {cambios_exitosos}")
    print(f"⚠️  Cambios fallidos/omitidos: {cambios_fallidos}")
    
    if cambios_fallidos > 0:
        print("\n💡 Nota: Algunos cambios no se pudieron aplicar porque:")
        print("   - El archivo/carpeta ya no existe")
        print("   - Ya existe un archivo/carpeta con el nuevo nombre")
        print("   - Error de permisos")
    
    print("\n" + "="*50)

def main():
    print("="*50)
    print("🔄 SCRIPT DE REORGANIZACIÓN DE NOMBRES")
    print("="*50)
    print("\nEste script analiza y reorganiza nombres para evitar conflictos.")
    print("Ejemplo: Ace, Ace_1, Ace_2, Ace_3 -> Ace_1, Ace_2, Ace_3, Ace_4")
    
    root_directory = os.getcwd()
    print(f"\n📂 Directorio actual: {root_directory}")
    
    # Fase 1: Análisis
    print("\n" + "-"*50)
    print("🔍 ANALIZANDO ESTRUCTURA DE DIRECTORIOS...")
    print("-"*50)
    
    archivos_planificados, carpetas_planificadas, conflictos = analyze_and_plan_changes(root_directory)
    
    total_cambios = len(archivos_planificados) + len(carpetas_planificadas)
    
    if total_cambios == 0:
        print("\n🎉 No se necesitan cambios. La estructura ya está organizada.")
        return
    
    # Mostrar conflictos encontrados
    show_conflicts(conflictos)
    
    # Resumen de cambios planificados
    print(f"\n📋 RESUMEN DE CAMBIOS PLANIFICADOS:")
    print(f"   Archivos a renombrar: {len(archivos_planificados)}")
    print(f"   Carpetas a renombrar: {len(carpetas_planificadas)}")
    print(f"   Total de cambios: {total_cambios}")
    
    # Preguntar confirmación
    print("\n" + "="*50)
    confirmacion = input("\n¿Deseas aplicar estos cambios? (s/n): ").strip().lower()
    
    if confirmacion != 's':
        print("\n❌ Operación cancelada por el usuario.")
        return
    
    # Fase 2: Aplicación
    print("\n" + "-"*50)
    print("⚡ APLICANDO CAMBIOS...")
    print("-"*50)
    
    cambios_exitosos, cambios_fallidos = apply_changes(archivos_planificados, carpetas_planificadas)
    
    # Mostrar resumen final
    show_summary(conflictos, cambios_exitosos, cambios_fallidos)
    
    if cambios_exitosos > 0:
        print("\n🎉 ¡Proceso completado exitosamente!")
    else:
        print("\n⚠️  No se realizaron cambios. Revisa los mensajes anteriores.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Proceso interrumpido por el usuario.")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")