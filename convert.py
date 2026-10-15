"""Convertit chaque page d'un PDF en JPEG, puis rogne les marges claires."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pymupdf
from PIL import Image


DEFAULT_DPI = 200
DEFAULT_PADDING = 8
DEFAULT_QUALITY = 90
DEFAULT_THRESHOLD = 245
DEFAULT_TOLERANCE = 40


def find_default_pdf(root: Path) -> Path | None:
    for folder in (root / "samples", root):
        if not folder.is_dir():
            continue
        pdfs = sorted(folder.glob("*.pdf"))
        if pdfs:
            return pdfs[0]
    return None


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


def convert_pdf(
    pdf_path: Path,
    out_dir: Path,
    dpi: int = DEFAULT_DPI,
    padding: int = DEFAULT_PADDING,
    quality: int = DEFAULT_QUALITY,
    threshold: int = DEFAULT_THRESHOLD,
    tolerance: int = DEFAULT_TOLERANCE,
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

            dest = out_dir / f"page_{index:03d}.jpeg"
            image.convert("RGB").save(dest, format="JPEG", quality=quality, optimize=True)
            written.append(dest)
            print(f"[{index}/{total}] {dest.name} ({image.width}x{image.height})")

    return written


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convertit chaque page d'un PDF en JPEG et rogne les marges claires.",
    )
    parser.add_argument(
        "pdf",
        nargs="?",
        type=Path,
        help="Fichier PDF source (défaut: premier *.pdf dans samples/ ou à la racine)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Dossier de sortie (défaut: output/<nom_du_pdf>/)",
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
    return parser


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parent
    args = build_parser().parse_args(argv)

    pdf_path = args.pdf
    if pdf_path is None:
        pdf_path = find_default_pdf(root)
        if pdf_path is None:
            print("Aucun PDF trouvé. Passez un chemin ou placez un fichier dans samples/.", file=sys.stderr)
            return 1
    else:
        pdf_path = pdf_path.resolve()

    if not pdf_path.is_file():
        print(f"Fichier introuvable: {pdf_path}", file=sys.stderr)
        return 1

    out_dir = args.output
    if out_dir is None:
        out_dir = root / "output" / pdf_path.stem
    else:
        out_dir = out_dir.resolve()

    print(f"PDF : {pdf_path}")
    print(f"Sortie : {out_dir}")
    written = convert_pdf(
        pdf_path,
        out_dir,
        dpi=args.dpi,
        padding=args.padding,
        quality=args.quality,
        threshold=args.threshold,
        tolerance=args.tolerance,
    )
    print(f"Terminé — {len(written)} page(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
