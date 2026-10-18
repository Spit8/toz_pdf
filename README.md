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
| `--dpi` | Résolution de rendu **et** métadonnée DPI écrite dans le JPEG | `200` |
| `--padding` | Marge (px) autour du contenu détecté | `8` |
| `--quality` | Qualité JPEG (1–95) | `90` |
| `--threshold` | Seuil de luminosité 0–255 pour détecter le contenu | `245` |
| `--tolerance` | Ignore le contenu dans une bande de N px sur les bords (bord de scan) | `20` |
| `--height` | Hauteur cible en px (proportions conservées). Absent = pas de resize. Pour Word : garder une valeur haute (ex. `890`) — la taille page est gérée à l’insertion, ne pas baisser pour « rentrer » | désactivé (ex. `890`) |

Aide :

```bat
.venv\Scripts\python.exe convert.py --help
```

## Insertion dans un Word (.docx)

Après la conversion PDF → JPEG (ou à partir de n’importe quel dossier d’images), ajoutez les images à la fin d’un fichier Word existant.

### Comportement

- Placez **exactement un** fichier `.docx` **source** dans `input_docx/` (par défaut).
  - Les fichiers `*_images.docx` (copies générées) sont **ignorés** à la sélection.
  - **0** source → erreur
  - **≥2** sources → erreur (les noms trouvés sont listés)
  - Source + `*_images.docx` déjà présent → **OK** (régénération en boucle possible)
- Les images sont ajoutées **après le contenu existant** (saut de page avant la première).
- **Une image par page**, **centrée**, **adaptée à la zone imprimable** (marges du document, proportions conservées, pas d’agrandissement).
- La **source n’est jamais modifiée** : sortie = `{nom}_images.docx` (écrasée à chaque run).
- Ordre d’insertion : **tri alphabétique** des noms de fichiers (compatible `page_001.jpeg`, `page_002.jpeg`, …).
- Formats acceptés : `.jpeg`, `.jpg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.tif`, `.webp`.

**Netteté :** ne baissez pas `--height` pour faire rentrer les images dans Word (cela floute). Gardez par ex. `DPI=200` et `HEIGHT=890` dans `convertir.bat` ; `insert_docx.py` réduit l’affichage à la page.

### Usage rapide (Windows)

1. Lancez `setup.bat` une fois (si ce n’est pas déjà fait).
2. Placez **un seul** `.docx` source dans `input_docx/` (vous pouvez laisser l’ancienne `*_images.docx`).
3. Préparez vos images, par exemple via `convertir.bat` → `output\<titre_du_pdf>\`.
4. Éditez `Fabriquer_DOCX.bat` si besoin (variable `IMAGES`) :

```bat
set DOCX_DIR=input_docx
set IMAGES=output\rapport
```

5. Double-cliquez `Fabriquer_DOCX.bat` (autant de fois que nécessaire).

Exemple de flux complet :

```text
input/rapport.pdf
  → convertir.bat
  → output/rapport/page_001.jpeg …
input_docx/mon_modele.docx          (source, intacte)
  → Fabriquer_DOCX.bat (IMAGES=output\rapport)
  → input_docx/mon_modele_images.docx   (copie avec images)
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
| `docx_dir` | Dossier contenant **exactement un** `.docx` source (`*_images.docx` ignorés) |
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
