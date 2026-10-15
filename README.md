# PDF to JPEG

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

## Dépendances

- [PyMuPDF](https://pymupdf.readthedocs.io/) — rendu des pages PDF
- [Pillow](https://pillow.readthedocs.io/) — rognage et enregistrement JPEG

Listées dans `requirements.txt`.

## Contenu non versionné

Les PDF dans `input/` (et `samples/` en local), le contenu de `output/` et `.venv/` sont ignorés par Git : placez vos fichiers localement, sans les committer.
