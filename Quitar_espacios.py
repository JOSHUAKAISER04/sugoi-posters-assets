import os

# Extensiones de imagen que se procesarán
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')

def rename_images(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(IMAGE_EXTENSIONS):
                # Verificar si el archivo tiene espacios o #
                if " " in file or "#" in file:
                    old_path = os.path.join(root, file)
                    
                    # Reemplazar espacios y # por _
                    new_name = file.replace(" ", "_").replace("#", "_")
                    new_path = os.path.join(root, new_name)

                    # Evitar sobrescribir archivos existentes
                    if not os.path.exists(new_path):
                        os.rename(old_path, new_path)
                        print(f"Renombrado: {old_path} -> {new_path}")
                    else:
                        print(f"Saltado (ya existe): {new_path}")

if __name__ == "__main__":
    root_directory = os.getcwd()  # Ejecuta desde la raíz
    rename_images(root_directory)