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


def resolve_single_docx(folder: Path) -> Path:
    """Retourne le unique .docx du dossier, ou lève FileNotFoundError / ValueError."""
    if not folder.is_dir():
        raise FileNotFoundError(f"Dossier .docx invalide: {folder}")

    docxs = list_docx_in_dir(folder)
    if len(docxs) == 0:
        raise FileNotFoundError(f"Aucun fichier .docx dans le dossier: {folder}")
    if len(docxs) >= 2:
        names = ", ".join(p.name for p in docxs)
        raise ValueError(
            f"Plusieurs fichiers .docx dans {folder} ({len(docxs)}) : {names}. "
            "Placez un seul .docx dans ce dossier."
        )
    return docxs[0]


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


def insert_images(docx_path: Path, images: list[Path]) -> None:
    doc = Document(str(docx_path))
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

    doc.save(str(docx_path))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Insère toutes les images d'un dossier à la fin du unique .docx "
            "présent dans un dossier d'entrée (une image par page, centrées, "
            "adaptées à la zone imprimable). Écrase le fichier source."
        ),
    )
    parser.add_argument(
        "docx_dir",
        type=Path,
        help="Dossier contenant exactement un fichier .docx (écrasé)",
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
        docx_path = resolve_single_docx(docx_dir)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if not images_dir.is_dir():
        print(f"Dossier d'images invalide: {images_dir}", file=sys.stderr)
        return 1

    images = list_images(images_dir)
    if not images:
        print(f"Aucune image dans le dossier: {images_dir}", file=sys.stderr)
        return 1

    print(f"DOCX : {docx_path}")
    print(f"Images : {images_dir} ({len(images)} fichier(s))")

    try:
        insert_images(docx_path, images)
    except Exception:
        print(f"Erreur pendant l'insertion dans: {docx_path}", file=sys.stderr)
        traceback.print_exc()
        return 1

    print(f"OK: {len(images)} image(s) ajoutée(s), fichier écrasé.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
