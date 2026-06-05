import shutil
import time
from pathlib import Path

# Extensiones válidas
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tiff"}

# Carpetas que no queremos tocar
IGNORED_DIR_NAMES = {".git", "__pycache__"}


# ==========================
# UTILIDADES
# ==========================

def is_image(file_path: Path) -> bool:
    return file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS


def should_ignore_dir(dir_path: Path) -> bool:
    return dir_path.name in IGNORED_DIR_NAMES or dir_path.name.startswith(".")


def get_top_level_folders(root: Path):
    return sorted(
        [p for p in root.iterdir() if p.is_dir() and not should_ignore_dir(p)],
        key=lambda p: p.name.lower()
    )


def get_all_dirs(root: Path):
    """
    Devuelve root + todas sus subcarpetas, excluyendo carpetas ignoradas.
    Se hace una captura fija de la estructura para no interferir mientras movemos archivos.
    """
    dirs = [root]
    for p in root.rglob("*"):
        if p.is_dir() and not should_ignore_dir(p):
            dirs.append(p)
    return sorted(dirs, key=lambda p: (len(p.parts), str(p).lower()))


def direct_images(folder: Path):
    return [f for f in folder.iterdir() if is_image(f)]


def direct_dirs(folder: Path):
    return [d for d in folder.iterdir() if d.is_dir() and not should_ignore_dir(d)]


def unique_file_path(path: Path) -> Path:
    """
    Si ya existe un archivo con ese nombre, agrega _1, _2, etc.
    """
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    parent = path.parent

    counter = 1
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def is_already_organized(folder: Path) -> bool:
    """
    Estructura válida:
        Carpeta/
            Carpeta.png
    """
    images = direct_images(folder)
    subdirs = direct_dirs(folder)

    if len(images) != 1:
        return False

    if subdirs:
        return False

    return images[0].stem == folder.name


# ==========================
# ANÁLISIS
# ==========================

def analyze_tree(folder: Path):
    print(f"\nAnalizando: {folder}\n")

    all_dirs = get_all_dirs(folder)

    organized = []
    loose_with_images = []
    empty_dirs = []

    for d in all_dirs:
        imgs = direct_images(d)
        subs = direct_dirs(d)

        if imgs and is_already_organized(d):
            organized.append(d)
        elif imgs:
            loose_with_images.append((d, len(imgs), len(subs)))
        else:
            if not subs:
                empty_dirs.append(d)

    print("Carpetas ya organizadas:")
    if organized:
        for d in organized:
            print(f"  [OK] {d.relative_to(folder)}")
    else:
        print("  Ninguna")

    print("\nCarpetas con imágenes sueltas:")
    if loose_with_images:
        for d, img_count, sub_count in loose_with_images:
            print(f"  [NO] {d.relative_to(folder)} -> {img_count} imagen(es), {sub_count} subcarpeta(s)")
    else:
        print("  Ninguna")

    print("\nCarpetas vacías:")
    if empty_dirs:
        for d in empty_dirs:
            if d != folder:
                print(f"  [VACÍA] {d.relative_to(folder)}")
    else:
        print("  Ninguna")


# ==========================
# ORGANIZACIÓN
# ==========================

def organize_tree(folder: Path):
    """
    Recorre recursivamente toda la carpeta elegida.
    Si encuentra imágenes sueltas en cualquier nivel, crea una subcarpeta
    con el nombre base de la imagen y mueve el archivo allí.
    """
    start = time.time()
    all_dirs = get_all_dirs(folder)

    moved_files = 0
    created_folders = 0
    skipped_organized = 0

    print(f"\nOrganizando árbol completo en: {folder}\n")

    for current_dir in all_dirs:
        images = direct_images(current_dir)

        if not images:
            continue

        # Si ya está perfectamente organizada, no la tocamos
        if is_already_organized(current_dir):
            skipped_organized += 1
            continue

        for img in images:
            target_folder = current_dir / img.stem
            if not target_folder.exists():
                target_folder.mkdir(parents=True, exist_ok=True)
                created_folders += 1

            target_file = unique_file_path(target_folder / img.name)

            shutil.move(str(img), str(target_file))
            moved_files += 1

            try:
                rel_src = img.relative_to(folder)
            except Exception:
                rel_src = img

            try:
                rel_dst = target_file.relative_to(folder)
            except Exception:
                rel_dst = target_file

            print(f"✓ {rel_src} -> {rel_dst}")

    elapsed = round(time.time() - start, 2)

    print("\n=================================")
    print("RESUMEN")
    print("=================================")
    print(f"Carpeta raíz      : {folder.name}")
    print(f"Carpetas creadas  : {created_folders}")
    print(f"Archivos movidos  : {moved_files}")
    print(f"Ya organizadas    : {skipped_organized}")
    print(f"Tiempo empleado   : {elapsed}s")
    print("=================================\n")


# ==========================
# SELECCIÓN DE CARPETA
# ==========================

def choose_folder(root: Path):
    folders = get_top_level_folders(root)

    print("\n=================================")
    print("CARPETAS DISPONIBLES")
    print("=================================")

    print("0. Usar la raíz completa")
    for i, folder in enumerate(folders, start=1):
        print(f"{i}. {folder.name}")

    while True:
        option = input("\nSeleccione una carpeta: ").strip()

        if option == "0" or option == "":
            return root

        if option.isdigit():
            index = int(option) - 1
            if 0 <= index < len(folders):
                return folders[index]

        print("Opción inválida.")


# ==========================
# MENÚ PRINCIPAL
# ==========================

def main():
    print("=== ORGANIZADOR DE IMÁGENES ===")

    root_input = input("Ruta raíz (Enter para usar la carpeta actual): ").strip()
    root = Path(root_input) if root_input else Path.cwd()

    if not root.exists() or not root.is_dir():
        print(f"\nLa ruta no existe o no es una carpeta: {root}")
        return

    while True:
        print("\n=================================")
        print(" ORGANIZADOR DE IMÁGENES")
        print("=================================")
        print(f"Raíz: {root}")
        print("=================================")
        print("1. Analizar carpeta")
        print("2. Organizar carpeta")
        print("3. Analizar TODAS las carpetas principales")
        print("4. Organizar TODAS las carpetas principales")
        print("5. Salir")
        print("=================================")

        option = input("Seleccione una opción: ").strip()

        if option == "1":
            folder = choose_folder(root)
            analyze_tree(folder)

        elif option == "2":
            folder = choose_folder(root)
            organize_tree(folder)

        elif option == "3":
            analyze_tree(root)

        elif option == "4":
            confirm = input("\n¿Seguro que desea organizar todo? (s/n): ").strip().lower()
            if confirm == "s":
                organize_tree(root)

        elif option == "5":
            print("\nHasta luego.")
            break

        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main()