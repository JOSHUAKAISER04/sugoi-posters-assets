import os
import re

# Extensiones de imagen que se procesarán
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')

def rename_files_and_folders(root_dir):
    # Usamos topdown=False para procesar primero los archivos y luego las carpetas
    for root, dirs, files in os.walk(root_dir, topdown=False):
        # Procesar archivos
        for file in files:
            if file.lower().endswith(IMAGE_EXTENSIONS):
                # Verificar si el archivo tiene caracteres a reemplazar
                if re.search(r'[ #]', file):
                    old_path = os.path.join(root, file)
                    
                    # Reemplazar espacios y # por _
                    new_name = re.sub(r'[ #]+', '_', file)
                    new_path = os.path.join(root, new_name)

                    if not os.path.exists(new_path):
                        os.rename(old_path, new_path)
                        print(f"Archivo renombrado: {old_path} -> {new_path}")
                    else:
                        print(f"Archivo saltado (ya existe): {new_path}")
        
        # Procesar carpetas
        for dir_name in dirs:
            # Verificar si la carpeta tiene caracteres a reemplazar
            if re.search(r'[ #]', dir_name):
                old_dir_path = os.path.join(root, dir_name)
                
                # Reemplazar espacios y # por _
                new_dir_name = re.sub(r'[ #]+', '_', dir_name)
                new_dir_path = os.path.join(root, new_dir_name)
                
                if not os.path.exists(new_dir_path):
                    os.rename(old_dir_path, new_dir_path)
                    print(f"Carpeta renombrada: {old_dir_path} -> {new_dir_path}")
                else:
                    print(f"Carpeta saltada (ya existe): {new_dir_path}")

if __name__ == "__main__":
    root_directory = os.getcwd()
    rename_files_and_folders(root_directory)