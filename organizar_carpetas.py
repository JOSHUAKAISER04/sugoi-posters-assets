import os
import shutil

def listar_subcarpetas(carpeta):
    """Devuelve una lista con las subcarpetas de una ruta dada."""
    return [f for f in os.listdir(carpeta) if os.path.isdir(os.path.join(carpeta, f))]

def organizar_imagenes(carpeta_trabajo):
    """Crea carpetas con el nombre de cada imagen y las mueve dentro."""
    extensiones = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')

    archivos = [f for f in os.listdir(carpeta_trabajo)
                if f.lower().endswith(extensiones) and os.path.isfile(os.path.join(carpeta_trabajo, f))]

    if not archivos:
        print("No se encontraron imágenes en esta carpeta.")
        return

    for archivo in archivos:
        nombre, _ = os.path.splitext(archivo)
        ruta_carpeta = os.path.join(carpeta_trabajo, nombre)

        # Crear carpeta si no existe
        if not os.path.exists(ruta_carpeta):
            os.makedirs(ruta_carpeta)

        # Mover la imagen dentro de su carpeta
        origen = os.path.join(carpeta_trabajo, archivo)
        destino = os.path.join(ruta_carpeta, archivo)

        shutil.move(origen, destino)
        print(f"✔ Imagen '{archivo}' movida a '{ruta_carpeta}'")

def main():
    carpeta_principal = input("Ingrese la ruta de la carpeta principal: ").strip()

    if not os.path.isdir(carpeta_principal):
        print("❌ La ruta especificada no es válida.")
        return

    subcarpetas = listar_subcarpetas(carpeta_principal)

    if subcarpetas:
        print("\nSubcarpetas encontradas:")
        for i, sub in enumerate(subcarpetas, 1):
            print(f"{i}. {sub}")

        seleccion = input("\nSeleccione el número de la carpeta a trabajar (o presione Enter para usar la principal): ").strip()

        if seleccion.isdigit() and 1 <= int(seleccion) <= len(subcarpetas):
            carpeta_trabajo = os.path.join(carpeta_principal, subcarpetas[int(seleccion) - 1])
        else:
            carpeta_trabajo = carpeta_principal
    else:
        print("No se encontraron subcarpetas. Se usará la carpeta principal.")
        carpeta_trabajo = carpeta_principal

    print(f"\n🔹 Trabajando en: {carpeta_trabajo}\n")
    organizar_imagenes(carpeta_trabajo)

    print("\n✅ Proceso completado.")

if __name__ == "__main__":
    main()
