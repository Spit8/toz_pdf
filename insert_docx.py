"""Insère les images d'un dossier à la fin d'un fichier Word (.docx)."""

from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.image.image import Image as DocxImage
from docx.shared import Cm, Emu, Pt


IMAGE_EXTENSIONS = {".jpeg", ".jpg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp"}
OUTPUT_SUFFIX = "_images"

# Marge de sécurité pour le paragraphe (évite un léger débordement vertical).
_SAFETY = Cm(0.2)


def list_images(folder: Path) -> list[Path]:
    images = [
        p
        for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    ]
    return sorted(images, key=lambda p: p.name.lower())


def list_docx_in_dir(folder: Path) -> list[Path]:
    return sorted(folder.glob("*.docx"), key=lambda p: p.name.lower())


def is_output_docx(path: Path) -> bool:
    """True si le fichier est une copie générée (*_images.docx)."""
    return path.stem.lower().endswith(OUTPUT_SUFFIX)


def list_source_docx(folder: Path) -> list[Path]:
    """Fichiers .docx sources (ignore les copies *_images)."""
    return [p for p in list_docx_in_dir(folder) if not is_output_docx(p)]


def output_path(source: Path) -> Path:
    """Chemin de la copie avec images : {stem}_images.docx."""
    return source.with_name(f"{source.stem}{OUTPUT_SUFFIX}{source.suffix}")


def resolve_single_docx(folder: Path) -> Path:
    """Retourne l'unique .docx source du dossier (ignore *_images)."""
    if not folder.is_dir():
        raise FileNotFoundError(f"Dossier .docx invalide: {folder}")

    sources = list_source_docx(folder)
    if len(sources) == 0:
        raise FileNotFoundError(
            f"Aucun fichier .docx source dans le dossier: {folder} "
            f"(les fichiers *{OUTPUT_SUFFIX}.docx sont ignorés)."
        )
    if len(sources) >= 2:
        names = ", ".join(p.name for p in sources)
        raise ValueError(
            f"Plusieurs fichiers .docx source dans {folder} ({len(sources)}) : {names}. "
            f"Placez un seul modèle (les *{OUTPUT_SUFFIX}.docx sont autorisés en plus)."
        )
    return sources[0]


def printable_area(section) -> tuple[Emu, Emu]:
    """Zone utile de la page (largeur × hauteur), hors marges."""
    max_w = section.page_width - section.left_margin - section.right_margin
    max_h = section.page_height - section.top_margin - section.bottom_margin - _SAFETY
    if max_w <= 0 or max_h <= 0:
        raise ValueError("Zone imprimable invalide (marges trop grandes pour la page).")
    return Emu(int(max_w)), Emu(int(max_h))


def fitted_size(image_path: Path, max_w: Emu, max_h: Emu) -> tuple[Emu, Emu]:
    """Taille d'affichage : tient dans max_w×max_h, ratio conservé, pas d'upscale."""
    img = DocxImage.from_file(str(image_path))
    native_w = float(img.width)
    native_h = float(img.height)
    scale = min(float(max_w) / native_w, float(max_h) / native_h, 1.0)
    return Emu(int(native_w * scale)), Emu(int(native_h * scale))


def insert_images(source_path: Path, out_path: Path, images: list[Path]) -> None:
    doc = Document(str(source_path))
    max_w, max_h = printable_area(doc.sections[-1])

    # Démarrer après le contenu existant, sur une nouvelle page.
    doc.add_page_break()

    total = len(images)
    for index, image_path in enumerate(images, start=1):
        width, height = fitted_size(image_path, max_w, max_h)

        paragraph = doc.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.space_before = Pt(0)
        paragraph.paragraph_format.space_after = Pt(0)
        paragraph.paragraph_format.line_spacing = 1.0

        run = paragraph.add_run()
        run.add_picture(str(image_path), width=width, height=height)
        print(f"[{index}/{total}] {image_path.name} ({width.cm:.2f}x{height.cm:.2f} cm)")

        if index < total:
            doc.add_page_break()

    doc.save(str(out_path))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Insère toutes les images d'un dossier à la fin du unique .docx source "
            f"d'un dossier d'entrée (ignore *{OUTPUT_SUFFIX}.docx). Une image par page, "
            "centrées, adaptées à la zone imprimable. Écrit une copie "
            f"{{stem}}{OUTPUT_SUFFIX}.docx sans modifier la source."
        ),
    )
    parser.add_argument(
        "docx_dir",
        type=Path,
        help=(
            "Dossier contenant exactement un .docx source "
            f"(les *{OUTPUT_SUFFIX}.docx sont ignorés)"
        ),
    )
    parser.add_argument(
        "images",
        type=Path,
        help="Dossier contenant les images à insérer",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    docx_dir = args.docx_dir.resolve()
    images_dir = args.images.resolve()

    try:
        source_path = resolve_single_docx(docx_dir)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    out_path = output_path(source_path)

    if not images_dir.is_dir():
        print(f"Dossier d'images invalide: {images_dir}", file=sys.stderr)
        return 1

    images = list_images(images_dir)
    if not images:
        print(f"Aucune image dans le dossier: {images_dir}", file=sys.stderr)
        return 1

    print(f"Source : {source_path}")
    print(f"Sortie : {out_path}")
    print(f"Images : {images_dir} ({len(images)} fichier(s))")

    try:
        insert_images(source_path, out_path, images)
    except Exception:
        print(f"Erreur pendant l'insertion (sortie: {out_path})", file=sys.stderr)
        traceback.print_exc()
        return 1

    print(f"OK: {len(images)} image(s) ajoutée(s) → {out_path.name} (source intacte).")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
