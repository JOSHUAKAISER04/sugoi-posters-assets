import os
from PIL import Image, ImageDraw, ImageFont

def generar_estructura(directorio, prefijo=""):
    """
    Recorre el directorio recursivamente y devuelve un string con la estructura tipo árbol.
    """
    estructura = ""
    archivos = sorted(os.listdir(directorio))
    for i, nombre in enumerate(archivos):
        ruta = os.path.join(directorio, nombre)
        conector = "┗━ " if i == len(archivos) - 1 else "┣━ "
        estructura += f"{prefijo}{conector}{nombre}\n"
        if os.path.isdir(ruta):
            nuevo_prefijo = f"{prefijo}{'   ' if i == len(archivos) - 1 else '┃  '}"
            estructura += generar_estructura(ruta, nuevo_prefijo)
    return estructura


def guardar_texto(estructura, archivo_salida="estructura.txt"):
    """
    Guarda la estructura en un archivo de texto.
    """
    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write(estructura)
    print(f"✅ Estructura guardada en: {archivo_salida}")


def generar_imagen(estructura, archivo_salida="estructura.png"):
    """
    Crea una imagen tipo 'impresión de pantalla' con la estructura de texto.
    """
    lineas = estructura.splitlines()
    ancho = max(len(linea) for linea in lineas) * 10
    alto = len(lineas) * 20 + 20

    # Crear la imagen blanca
    img = Image.new("RGB", (ancho, alto), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Fuente (puedes cambiarla si tienes otra instalada)
    try:
        font = ImageFont.truetype("consola.ttf", 16)
    except:
        font = ImageFont.load_default()

    # Escribir el texto línea por línea
    y = 10
    for linea in lineas:
        draw.text((10, y), linea, fill=(0, 0, 0), font=font)
        y += 20

    img.save(archivo_salida)
    print(f"🖼️ Imagen generada: {archivo_salida}")


def main():
    carpeta_objetivo = input("📂 Ingresa la ruta de la carpeta a escanear: ").strip()

    if not os.path.exists(carpeta_objetivo):
        print("❌ La carpeta no existe.")
        return

    print("🔍 Generando estructura...")
    estructura = f"📁 {os.path.basename(carpeta_objetivo)}\n"
    estructura += generar_estructura(carpeta_objetivo)

    guardar_texto(estructura)
    generar_imagen(estructura)
    print("\n✅ Proceso completado. Revisa los archivos 'estructura.txt' y 'estructura.png'.")


if __name__ == "__main__":
    main()
