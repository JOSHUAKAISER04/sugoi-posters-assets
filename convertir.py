#!/usr/bin/env python3
"""
comprimir.py — PNG/JPG/JPEG → WebP (85% calidad)
=================================================
Convierte imágenes (PNG, JPG, JPEG) a WebP con calidad 85%.
- Los archivos .webp existentes se ignoran por completo.
- El archivo original se elimina tras la conversión exitosa.
- El nuevo .webp queda en la misma carpeta con el mismo nombre.
- Recorre todos los subdirectorios recursivamente.

Uso:
    python comprimir.py                  # directorio actual
    python comprimir.py ruta/carpeta     # carpeta específica
    python comprimir.py --calidad 90     # cambiar calidad (default: 85)
    python comprimir.py --dry-run        # simular sin tocar nada
    python comprimir.py --backup         # guardar originales antes
"""

import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime

try:
    from PIL import Image, ImageFile
    ImageFile.LOAD_TRUNCATED_IMAGES = True
except ImportError:
    print("❌ Pillow no está instalado. Ejecuta: pip install Pillow")
    sys.exit(1)


def fmt(b: int) -> str:
    for u in ["B", "KB", "MB", "GB"]:
        if b < 1024:
            return f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} GB"

def icono(pct: float) -> str:
    if pct >= 70: return "🚀"
    if pct >= 50: return "✅"
    if pct >= 30: return "📉"
    if pct >  0:  return "🔹"
    return "⚠️ "


def convertir(ruta: Path, calidad: int, backup_dir: Path | None, dry_run: bool) -> dict:
    res = {
        "tam_orig": ruta.stat().st_size,
        "tam_nuevo": 0,
        "ruta_nueva": ruta.with_suffix(".webp"),
        "error": None,
    }

    # Control de seguridad: Si por algún motivo se coló un .webp, no hacer nada.
    if ruta.suffix.lower() == ".webp":
        res["error"] = "El archivo ya es WebP"
        return res

    try:
        with Image.open(ruta) as img:
            img.load()

            # Normalizar modo para WebP
            modo = img.mode
            if modo == "P":
                img = img.convert("RGBA" if "transparency" in img.info else "RGB")
            elif modo not in ("RGB", "RGBA", "L", "LA"):
                img = img.convert("RGB")

            if dry_run:
                # Estimar tamaño sin escribir
                from io import BytesIO
                buf = BytesIO()
                img.save(buf, format="WEBP", quality=calidad, method=6)
                res["tam_nuevo"] = len(buf.getvalue())
                return res

            # Backup del archivo original
            if backup_dir:
                dest = backup_dir / ruta.relative_to(ruta.anchor)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ruta, dest)

            # Guardar como WebP
            webp_path = ruta.with_suffix(".webp")
            img.save(webp_path, format="WEBP", quality=calidad, method=6)
            res["tam_nuevo"] = webp_path.stat().st_size

            # Eliminar archivo original (solo si la extensión cambia)
            if ruta != webp_path:
                ruta.unlink()

    except Exception as e:
        res["error"] = str(e)

    return res


def buscar_imagenes(directorio: Path, excluir: Path | None = None) -> list[Path]:
    imgs = []
    # Extensiones soportadas (Se excluye explícitamente .webp de la búsqueda)
    patrones = ("*.png", "*.PNG", "*.jpg", "*.jpeg", "*.JPG", "*.JPEG")
    
    for ext in patrones:
        imgs.extend(directorio.rglob(ext))
        
    imgs = sorted(set(imgs))
    if excluir:
        imgs = [i for i in imgs if excluir not in i.parents]
    return imgs


def main():
    parser = argparse.ArgumentParser(
        description="Convierte PNG/JPG/JPEG a WebP con calidad 85% recursivamente.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "directorio", nargs="?", default=".",
        help="Directorio raíz (default: directorio actual)"
    )
    parser.add_argument(
        "--calidad", type=int, default=85,
        help="Calidad WebP 1-100 (default: 85)"
    )
    parser.add_argument(
        "--backup", action="store_true",
        help="Guardar imágenes originales en _backup_imagenes/ antes de convertir"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Simular sin modificar ningún archivo"
    )
    args = parser.parse_args()

    raiz = Path(args.directorio).resolve()
    if not raiz.exists() or not raiz.is_dir():
        print(f"❌ Directorio no válido: {raiz}")
        sys.exit(1)

    backup_dir = None
    if args.backup:
        backup_dir = raiz / "_backup_imagenes"
        if not args.dry_run:
            backup_dir.mkdir(exist_ok=True)

    print(f"\n{'═'*60}")
    print(f"   🖼️  Conversor Multiformato → WebP")
    print(f"{'═'*60}")
    print(f"   📁 Directorio  : {raiz}")
    print(f"   🎯 Calidad     : {args.calidad}%")
    print(f"   💾 Backup      : {'Sí → _backup_imagenes/' if args.backup else 'No'}")
    print(f"   🧪 Dry-run     : {'SÍ — sin cambios reales' if args.dry_run else 'No'}")
    print(f"{'═'*60}\n")

    imagenes = buscar_imagenes(raiz, excluir=backup_dir)

    if not imagenes:
        print("⚠️  No se encontraron archivos nuevos para convertir (PNG, JPG o JPEG).")
        sys.exit(0)

    print(f"📸 {len(imagenes)} imágenes encontradas listas para procesar\n")

    total_orig = total_nuevo = procesadas = errores = 0
    inicio = datetime.now()

    for n, ruta in enumerate(imagenes, 1):
        rel = ruta.relative_to(raiz)
        print(f"   [{n:>4}/{len(imagenes)}] {rel}", end=" ... ", flush=True)

        res = convertir(ruta, args.calidad, backup_dir, args.dry_run)
        total_orig += res["tam_orig"]

        if res["error"]:
            print(f"❌ {res['error']}")
            errores += 1
            total_nuevo += res["tam_orig"]
            continue

        pct = (res["tam_orig"] - res["tam_nuevo"]) / res["tam_orig"] * 100
        nueva_ext = res["ruta_nueva"].name
        tag = " [estimado]" if args.dry_run else f" → {nueva_ext}"
        print(f"{icono(pct)} {fmt(res['tam_orig'])} → {fmt(res['tam_nuevo'])}  (-{pct:.1f}%){tag}")
        total_nuevo += res["tam_nuevo"]
        procesadas += 1

    elapsed = (datetime.now() - inicio).total_seconds()
    ahorro = total_orig - total_nuevo
    pct_total = (ahorro / total_orig * 100) if total_orig else 0

    print(f"\n{'═'*60}")
    print(f"   📊 RESUMEN {'[DRY-RUN]' if args.dry_run else 'FINAL'}")
    print(f"{'═'*60}")
    print(f"   ✅ Convertidas  : {procesadas}")
    print(f"   ❌ Errores      : {errores}")
    print(f"   ⏱️  Tiempo       : {elapsed:.1f}s")
    print(f"   📦 Antes        : {fmt(total_orig)}")
    print(f"   📦 Después(WebP): {fmt(total_nuevo)}")
    print(f"   💾 Ahorro total : {fmt(ahorro)}  ({pct_total:.1f}%)")
    if backup_dir and not args.dry_run:
        print(f"   🗂️  Originales   : {backup_dir}")
    print(f"{'═'*60}\n")

    if not args.dry_run and procesadas > 0:
        print("🎉 ¡Conversión completa! Recuerda actualizar las referencias de tus imágenes a .webp\n")


if __name__ == "__main__":
    main()