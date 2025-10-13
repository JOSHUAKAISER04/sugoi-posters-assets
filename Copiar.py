import os
import shutil

def copiar_estructura(origen, destino, nuevo_nombre):
    """
    Copia solo la estructura de carpetas (sin archivos) de 'origen' a 'destino'
    creando una nueva carpeta con nombre 'nuevo_nombre'.
    """
    # Crear la carpeta destino principal
    nueva_ruta = os.path.join(destino, nuevo_nombre)
    os.makedirs(nueva_ruta, exist_ok=True)

    # Recorrer todas las carpetas dentro del origen
    for carpeta_actual, subcarpetas, archivos in os.walk(origen):
        # Obtener la ruta relativa desde el origen
        ruta_relativa = os.path.relpath(carpeta_actual, origen)

        # Crear la ruta equivalente en el nuevo destino
        nueva_carpeta = os.path.join(nueva_ruta, ruta_relativa)
        os.makedirs(nueva_carpeta, exist_ok=True)

    print(f"Estructura de carpetas copiada correctamente en: {nueva_ruta}")

# ==== EJEMPLO DE USO ====
if __name__ == "__main__":
    origen = input("Ruta de la carpeta original: ").strip()
    destino = input("Ruta donde quieres crear la copia: ").strip()
    nuevo_nombre = input("Nombre de la nueva carpeta: ").strip()

    copiar_estructura(origen, destino, nuevo_nombre)
