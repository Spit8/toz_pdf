# toz_pdf

Convertit chaque page d’un PDF en fichier `.jpeg`, puis rogne automatiquement les marges claires (y compris le bord sombre typique d’une page scannée).

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

### Via `run.bat` (utilise le `.venv`)

```bat
rem Premier PDF trouvé dans samples/ ou à la racine
run.bat

rem PDF explicite
run.bat document.pdf

rem Options courantes
run.bat document.pdf -o output\mon_export --dpi 200 --padding 8 --quality 90 --tolerance 40

rem Scan avec bord de page visible (rogner plus agressivement)
run.bat scan.pdf --tolerance 60
```

### Via Python directement

Avec le `.venv` :

```bat
.venv\Scripts\python.exe convert.py document.pdf -o output\mon_export --tolerance 40
```

Sans `.venv` :

```bat
python convert.py document.pdf -o output\mon_export --tolerance 40
```

Sous Linux / macOS :

```bash
python3 convert.py document.pdf -o output/mon_export --tolerance 40
```

Sans argument PDF, le script prend le premier `*.pdf` trouvé dans `samples/` puis à la racine du projet.

Les JPEG sont écrits dans `output/<nom_du_pdf>/` sous la forme `page_001.jpeg`, `page_002.jpeg`, …

## Options

| Option | Description | Défaut |
|--------|-------------|--------|
| `-o`, `--output` | Dossier de sortie | `output/<nom_du_pdf>/` |
| `--dpi` | Résolution de rendu | `200` |
| `--padding` | Marge (px) autour du contenu détecté | `8` |
| `--quality` | Qualité JPEG (1–95) | `90` |
| `--threshold` | Seuil de luminosité 0–255 pour détecter le contenu | `245` |
| `--tolerance` | Ignore le contenu dans une bande de N px sur les bords (bord de scan) | `40` |

Aide :

```bat
.venv\Scripts\python.exe convert.py --help
```

## Dépendances

- [PyMuPDF](https://pymupdf.readthedocs.io/) — rendu des pages PDF
- [Pillow](https://pillow.readthedocs.io/) — rognage et enregistrement JPEG

Listées dans `requirements.txt`.

## Contenu non versionné

Les PDF (ex. dans `samples/`), le dossier `output/` et `.venv/` sont ignorés par Git : placez vos fichiers localement pour tester, sans les committer.
