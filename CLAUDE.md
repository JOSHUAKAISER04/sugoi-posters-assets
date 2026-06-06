# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This is an **asset + catalog-generation repo** for "Sugoi Posters", an otaku/anime
merchandise store. It holds the product images (`.webp`) organized into a strict
folder tree, plus a set of standalone Python scripts that maintain that tree and
generate `products.dart` — the catalog consumed by a separate Flutter app.

There is no application here, no test suite, and no package manifest. The "build"
is running `productos.py` to regenerate `products.dart`. Everything is in Spanish
(folder names, product fields, script output).

## Core workflow

The whole pipeline is driven by file/folder *layout*, not by data files. To add or
change products you manipulate images on disk, then regenerate:

```bash
python convertir.py            # 1. PNG/JPG/JPEG → WebP (q85); deletes originals
python organizar_carpetas.py   # 2. (interactive) wrap loose images into Foo/Foo.webp folders
python Renombrar.py            # 3. (interactive) normalize __/##, renumber siblings _1.._n
python productos.py            # 4. regenerate products.dart from the tree
```

Only `convertir.py` (argparse) and `productos.py` are non-interactive. The others
prompt via `input()` (and `buscar_carpetas_una_imagen.py` opens a Tk dialog), so
they cannot be run unattended — describe what they'd do rather than invoking them
blindly.

## Category folder layout (drives everything)

Top-level dirs map to product categories via the `categorias` dict in `productos.py:61`.
**Only these five prefixes are scanned; any other top-level dir is ignored:**

| Dir   | Category   | Price |
|-------|------------|-------|
| `C-a` | Camisas    | 280   |
| `S-u` | Sueters    | 500   |
| `P-o` | Posters    | 70    |
| `S-e` | Separadores| 25    |
| `Pol` | Polaroids  | 20    |

Canonical "organized" shape (enforced by `organizar_carpetas.py`):
`Categoria/Subcategoria(serie)/Personaje[_N]/Personaje[_N].webp`. A folder is
"already organized" when it contains exactly one image whose stem equals the
folder name and no subfolders.

`productos.py` handles several shapes per category and these are load-bearing:
- **Personalized products**: subfolders starting with `1_` or containing `personaliz`
  are emitted first and as a single `"Camisa Personalizada #1"`-style product whose
  `imagenes` list bundles *all* images in that folder.
- **C-a/S-u/P-o/Pol**: inner variant folders → `"Nombre Personaje #N"`; loose files
  directly under a subcategory → product per file. For `Pol/anime`, the cleaned
  filename becomes the `subcategoria`.
- **S-e and others**: handled by the generic branch at the bottom of the loop.

## products.dart is generated — never hand-edit it

`products.dart` (~5000 lines) is overwritten wholesale by `productos.py`. The one
piece of state worth preserving across regenerations is **`dateAdded`**:
`productos.py` reads the *previous* `products.dart` (looked for at
`../lib/data/products.dart`, i.e. the sibling Flutter project — see
`PRODUCTOS_DART_EXISTENTE` at `productos.py:13`) to keep existing dates; genuinely
new products get `dateAdded` from the newest image mtime. If you edit the generator,
do not break date preservation or the URL format.

Image URLs are jsDelivr CDN links built from `usuario`/`repositorio`/`rama` at
`productos.py:6-8` (`JOSHUAKAISER04/sugoi-posters-assets@main`). Note this differs
from the local git user (`Milo-IZ`); the CDN owner string, not git, determines the
served URLs, so changing it silently breaks every image link.

## Naming conventions baked into the generator

These regex helpers in `productos.py` define how folder/file names become product
names — match their behavior when adding logic:
- `limpiar_nombre` — strips extension, turns trailing `_1`/`(1)` into ` #1`.
- `normalize_hashes` — collapses `# #`→`#`, drops stray `#` not followed by a digit.
- `formatear_subcategoria` — Title Cases names but preserves all-caps acronyms (`DC`).
- `extraer_variante` — splits trailing number off a folder name for the `#N` suffix.

`Renombrar.py` and `Quitar_espacios.py` are the on-disk counterparts: `Quitar_espacios.py`
replaces spaces/`#` with `_` in image and folder names; `Renombrar.py` normalizes
duplicate separators and renumbers sibling groups to consecutive `_1.._n` (with a
dry-run analysis step and a safe two-phase temp-rename to avoid collisions).

## Utility scripts (no side effects on the catalog)

- `estructura.py` — dumps the folder tree to `estructura.txt` and a PNG.
- `buscar_carpetas_una_imagen.py` — lists folders containing exactly one image → `carpetas_con_una_imagen.txt`.
- `Copiar.py` — clones a folder tree's structure (dirs only, no files).

## Dependencies

`convertir.py` and `estructura.py` need **Pillow** (`pip install Pillow`).
Everything else is stdlib. Target Python 3.10+ (uses `X | None` / `dict[str, str]`).
