"""Convertit chaque page d'un PDF en JPEG, puis rogne les marges claires."""

from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

import pymupdf
from PIL import Image


DEFAULT_DPI = 200
DEFAULT_PADDING = 8
DEFAULT_QUALITY = 90
DEFAULT_THRESHOLD = 245
DEFAULT_TOLERANCE = 20
DEFAULT_HEIGHT = 890


def list_pdfs_in_dir(folder: Path) -> list[Path]:
    return sorted(folder.glob("*.pdf"))


def resolve_pdfs(source: Path | None, root: Path) -> list[Path]:
    """Résout une liste de PDF depuis un dossier, un fichier, ou input/ par défaut."""
    if source is None:
        source = root / "input"

    source = source.resolve()

    if source.is_dir():
        pdfs = list_pdfs_in_dir(source)
        if not pdfs:
            raise FileNotFoundError(f"Aucun PDF dans le dossier: {source}")
        return pdfs

    if source.is_file() and source.suffix.lower() == ".pdf":
        return [source]

    raise FileNotFoundError(f"Chemin invalide (dossier ou fichier .pdf attendu): {source}")


def _clear_border(mask: Image.Image, tolerance: int) -> Image.Image:
    """Ignore le contenu dans une bande périphérique (bord de scan)."""
    if tolerance <= 0:
        return mask
    w, h = mask.size
    if tolerance * 2 >= w or tolerance * 2 >= h:
        return mask
    cleared = mask.copy()
    black = 0
    # top / bottom
    cleared.paste(black, (0, 0, w, tolerance))
    cleared.paste(black, (0, h - tolerance, w, h))
    # left / right
    cleared.paste(black, (0, 0, tolerance, h))
    cleared.paste(black, (w - tolerance, 0, w, h))
    return cleared


def content_bbox(
    image: Image.Image,
    threshold: int = DEFAULT_THRESHOLD,
    padding: int = DEFAULT_PADDING,
    tolerance: int = DEFAULT_TOLERANCE,
) -> tuple[int, int, int, int] | None:
    """Bounding box des pixels plus sombres que *threshold*, avec marge.

    *tolerance* ignore les pixels sombres près des bords (liseré de page scannée).
    """
    gray = image.convert("L")
    mask = gray.point(lambda p: 255 if p < threshold else 0)
    mask = _clear_border(mask, tolerance)
    bbox = mask.getbbox()
    if bbox is None:
        return None

    left, top, right, bottom = bbox
    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(image.width, right + padding)
    bottom = min(image.height, bottom + padding)
    return left, top, right, bottom


def pixmap_to_image(pix: pymupdf.Pixmap) -> Image.Image:
    if pix.alpha:
        pix = pymupdf.Pixmap(pix, 0)  # drop alpha for JPEG
    mode = "RGB" if pix.n >= 3 else "L"
    return Image.frombytes(mode, (pix.width, pix.height), pix.samples)


def resize_to_height(image: Image.Image, height: int) -> Image.Image:
    """Redimensionne pour que la hauteur soit *height*, proportions conservees."""
    if height <= 0 or image.height == height:
        return image
    new_width = max(1, round(image.width * (height / image.height)))
    return image.resize((new_width, height), Image.Resampling.LANCZOS)


def convert_pdf(
    pdf_path: Path,
    out_dir: Path,
    dpi: int = DEFAULT_DPI,
    padding: int = DEFAULT_PADDING,
    quality: int = DEFAULT_QUALITY,
    threshold: int = DEFAULT_THRESHOLD,
    tolerance: int = DEFAULT_TOLERANCE,
    height: int | None = None,
) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    with pymupdf.open(pdf_path) as doc:
        total = doc.page_count
        for index, page in enumerate(doc, start=1):
            pix = page.get_pixmap(dpi=dpi)
            image = pixmap_to_image(pix)
            bbox = content_bbox(
                image,
                threshold=threshold,
                padding=padding,
                tolerance=tolerance,
            )
            if bbox is not None:
                image = image.crop(bbox)

            if height is not None and height > 0:
                image = resize_to_height(image, height)

            dest = out_dir / f"page_{index:03d}.jpeg"
            image.convert("RGB").save(
                dest,
                format="JPEG",
                quality=quality,
                optimize=True,
                dpi=(dpi, dpi),
            )
            written.append(dest)
            print(f"[{index}/{total}] {dest.name} ({image.width}x{image.height})")

    return written


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Convertit chaque page de PDF en JPEG et rogne les marges claires. "
            "Accepte un fichier ou un dossier (tous les *.pdf)."
        ),
    )
    parser.add_argument(
        "source",
        nargs="?",
        type=Path,
        help="Fichier PDF ou dossier d'entrée (défaut: input/)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Dossier parent de sortie (défaut: output/) ; un sous-dossier par PDF",
    )
    parser.add_argument("--dpi", type=int, default=DEFAULT_DPI, help=f"DPI de rendu (défaut: {DEFAULT_DPI})")
    parser.add_argument(
        "--padding",
        type=int,
        default=DEFAULT_PADDING,
        help=f"Marge autour du contenu en pixels (défaut: {DEFAULT_PADDING})",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=DEFAULT_QUALITY,
        help=f"Qualité JPEG 1-95 (défaut: {DEFAULT_QUALITY})",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=DEFAULT_THRESHOLD,
        help=f"Seuil de luminosité pour détecter le contenu 0-255 (défaut: {DEFAULT_THRESHOLD})",
    )
    parser.add_argument(
        "--tolerance",
        type=int,
        default=DEFAULT_TOLERANCE,
        help=(
            "Ignore le contenu dans une bande de N pixels sur les bords "
            f"(bord de page scannée ; défaut: {DEFAULT_TOLERANCE})"
        ),
    )
    parser.add_argument(
        "--height",
        type=int,
        default=None,
        metavar="PX",
        help=(
            "Hauteur cible en pixels (proportions conservees). "
            f"Sans cette option: pas de resize. Exemple: {DEFAULT_HEIGHT}"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parent
    args = build_parser().parse_args(argv)

    try:
        pdfs = resolve_pdfs(args.source, root)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    output_root = args.output.resolve() if args.output else (root / "output")

    total_pages = 0
    for pdf_path in pdfs:
        out_dir = output_root / pdf_path.stem
        print(f"PDF : {pdf_path}")
        print(f"Sortie : {out_dir}")
        try:
            written = convert_pdf(
                pdf_path,
                out_dir,
                dpi=args.dpi,
                padding=args.padding,
                quality=args.quality,
                threshold=args.threshold,
                tolerance=args.tolerance,
                height=args.height,
            )
        except Exception:
            print(f"Erreur pendant la conversion de: {pdf_path}", file=sys.stderr)
            traceback.print_exc()
            return 1
        total_pages += len(written)
        print(f"OK: {len(written)} page(s) pour '{pdf_path.stem}'\n")

    print(f"Termine - {len(pdfs)} PDF, {total_pages} page(s) au total.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
