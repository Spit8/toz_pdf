# PDF → JPEG → Word

Deux outils complémentaires :

1. **Conversion** : chaque page d’un PDF devient un `.jpeg`, avec rognage automatique des marges claires (y compris le bord sombre typique d’une page scannée).
2. **Insertion Word** : les images d’un dossier sont ajoutées à la fin d’un fichier `.docx` existant.

## Prérequis

- [Python](https://www.python.org/downloads/) 3.10 ou plus récent
- Sous Windows, cochez **Add python.exe to PATH** à l’installation

## Installation

### Avec un `.venv` local (recommandé)

À la racine du projet :

```bat
setup.bat
```

Cela crée `.venv/` et installe les paquets de `requirements.txt`.

### Sans `.venv` (Python global / environnement déjà actif)

```bat
pip install -r requirements.txt
```

Sous Linux / macOS :

```bash
python3 -m pip install -r requirements.txt
```

## Utilisation

### Usage rapide (Windows)

1. Lancez `setup.bat` une fois.
2. Placez vos PDF dans le dossier `input/` (n’importe quels noms de fichiers `.pdf`).
3. Double-cliquez `convertir.bat`.

Aucun nom de fichier n’est imposé : tous les `*.pdf` présents dans `input/` sont traités. Les JPEG sont écrits dans `output/<titre_du_pdf>/` :

```text
input/rapport.pdf     →  output/rapport/page_001.jpeg …
input/document.pdf    →  output/document/page_001.jpeg …
```

### Via Python / `run.bat`

L’argument positionnel est un **fichier PDF** ou un **dossier**. Sans argument, tous les `*.pdf` de `input/` sont traités.

```bat
rem Tous les PDF de input/ vers output/
run.bat
run.bat input -o output

rem Un seul PDF (chemin libre)
run.bat document.pdf -o output

rem Options
run.bat input -o output --dpi 200 --padding 8 --quality 90 --tolerance 20 --height 890
run.bat document.pdf -o output --tolerance 60
```

Avec le `.venv` :

```bat
.venv\Scripts\python.exe convert.py input -o output --tolerance 20
```

Sans `.venv` :

```bat
python convert.py input -o output --tolerance 20
```

Sous Linux / macOS :

```bash
python3 convert.py input -o output --tolerance 20
```

## Options

| Option | Description | Défaut |
|--------|-------------|--------|
| `source` | Fichier PDF ou dossier d’entrée | `input/` |
| `-o`, `--output` | Dossier parent de sortie (un sous-dossier par PDF) | `output/` |
| `--dpi` | Résolution de rendu | `200` |
| `--padding` | Marge (px) autour du contenu détecté | `8` |
| `--quality` | Qualité JPEG (1–95) | `90` |
| `--threshold` | Seuil de luminosité 0–255 pour détecter le contenu | `245` |
| `--tolerance` | Ignore le contenu dans une bande de N px sur les bords (bord de scan) | `20` |
| `--height` | Hauteur cible en px (proportions conservées). Absent = pas de resize | désactivé (ex. `890`) |

Aide :

```bat
.venv\Scripts\python.exe convert.py --help
```

## Insertion dans un Word (.docx)

Après la conversion PDF → JPEG (ou à partir de n’importe quel dossier d’images), ajoutez les images à la fin d’un fichier Word existant.

### Comportement

- Placez **exactement un** fichier `.docx` dans le dossier d’entrée (`input_docx/` par défaut).
  - **0** fichier → erreur
  - **≥2** fichiers → erreur (les noms trouvés sont listés)
- Les images sont ajoutées **après le contenu existant** (saut de page avant la première).
- **Une image par page**, **centrée**, **sans redimensionnement** (taille native selon le DPI de l’image).
- Le fichier `.docx` source est **écrasé** (faites une copie avant si besoin).
- Ordre d’insertion : **tri alphabétique** des noms de fichiers (compatible `page_001.jpeg`, `page_002.jpeg`, …).
- Formats acceptés : `.jpeg`, `.jpg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.tif`, `.webp`.

### Usage rapide (Windows)

1. Lancez `setup.bat` une fois (si ce n’est pas déjà fait).
2. Placez **un seul** `.docx` dans `input_docx/`.
3. Préparez vos images, par exemple via `convertir.bat` → `output\<titre_du_pdf>\`.
4. Éditez `Fabriquer_DOCX.bat` si besoin (variable `IMAGES`) :

```bat
set DOCX_DIR=input_docx
set IMAGES=output\rapport
```

5. Double-cliquez `Fabriquer_DOCX.bat`.

Exemple de flux complet :

```text
input/rapport.pdf
  → convertir.bat
  → output/rapport/page_001.jpeg …
input_docx/mon_modele.docx   (un seul .docx)
  → Fabriquer_DOCX.bat (IMAGES=output\rapport)
  → input_docx/mon_modele.docx (contenu d’origine + images en pages suivantes)
```

### Via Python

Deux arguments positionnels : le **dossier du `.docx`** puis le **dossier d’images**.

Avec le `.venv` :

```bat
.venv\Scripts\python.exe insert_docx.py input_docx output\rapport
```

Sans `.venv` :

```bat
python insert_docx.py input_docx output\rapport
```

Sous Linux / macOS :

```bash
python3 insert_docx.py input_docx output/rapport
```

### Arguments

| Argument | Description |
|----------|-------------|
| `docx_dir` | Dossier contenant **exactement un** fichier `.docx` (**écrasé** à la fin) |
| `images` | Dossier contenant les images à insérer |

Aide :

```bat
.venv\Scripts\python.exe insert_docx.py --help
```

## Dépendances

- [PyMuPDF](https://pymupdf.readthedocs.io/) — rendu des pages PDF
- [Pillow](https://pillow.readthedocs.io/) — rognage et enregistrement JPEG
- [python-docx](https://python-docx.readthedocs.io/) — insertion d’images dans un `.docx`

Listées dans `requirements.txt`.

## Contenu non versionné

Les PDF dans `input/`, les `.docx` dans `input_docx/` (et `samples/` en local), le contenu de `output/` et `.venv/` sont ignorés par Git : placez vos fichiers localement, sans les committer.
