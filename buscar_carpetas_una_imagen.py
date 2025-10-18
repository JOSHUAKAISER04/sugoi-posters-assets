import os
import tkinter as tk
from tkinter import filedialog

# Tipos de archivos considerados imágenes
EXTENSIONES_IMAGENES = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}

def es_imagen(archivo):
    _, extension = os.path.splitext(archivo.lower())
    return extension in EXTENSIONES_IMAGENES

def buscar_carpetas_con_una_imagen(directorio_base):
    carpetas_con_una_imagen = []

    for carpeta_actual, _, archivos in os.walk(directorio_base):
        imagenes = [f for f in archivos if es_imagen(f)]
        if len(imagenes) == 1:
            # Solo guardamos el nombre de la carpeta, no la ruta completa
            nombre_carpeta = os.path.basename(carpeta_actual)
            carpetas_con_una_imagen.append(nombre_carpeta)

    return carpetas_con_una_imagen

def main():
    # Interfaz para seleccionar el directorio
    root = tk.Tk()
    root.withdraw()
    print("Selecciona el directorio que deseas analizar...")
    directorio = filedialog.askdirectory(title="Selecciona el directorio base")

    if not directorio:
        print("No se seleccionó ningún directorio. Saliendo...")
        return

    print(f"\nAnalizando directorio: {directorio}\n")

    carpetas = buscar_carpetas_con_una_imagen(directorio)

    # El archivo se guarda en la raíz donde se ejecute el script
    ruta_salida = os.path.join(os.getcwd(), "carpetas_con_una_imagen.txt")

    if carpetas:
        print("📁 Carpetas con SOLO UNA imagen:\n")
        for c in carpetas:
            print(c)

        with open(ruta_salida, "w", encoding="utf-8") as f:
            for c in carpetas:
                f.write(c + "\n")

        print(f"\n✅ Se encontraron {len(carpetas)} carpetas con una sola imagen.")
        print(f"📄 Resultado guardado en: {ruta_salida}")
    else:
        print("❌ No se encontraron carpetas con solo una imagen.")

if __name__ == "__main__":
    main()
