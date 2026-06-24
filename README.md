---

# 🇫🇷 Version française

# Bookworm - Analyseur de livres textuels

Ce projet permet de rechercher, télécharger et analyser des œuvres littéraires à partir du catalogue au format `.csv` du site [Project Gutenberg](https://www.gutenberg.org).

Le script applique un pipeline de Traitement Automatique du Langage Naturel (NLP) permettant l'analyse automatisée d'œuvres littéraires.

## Fonctionnalités

- Téléchargement automatisé du texte brut via l'ID du livre.
- Nettoyage du texte (suppression des en-têtes et pieds de page Gutenberg).
- Tokenisation en phrases et en mots.
- Analyse lexicale.
- Extraction des entités nommées.
- Résumé automatique.
- Analyse thématique.
- Recherche d'œuvres similaires.

---

## Installation et prérequis

Avant de lancer le script, assurez-vous d'installer les dépendances nécessaires et de télécharger les modèles NLP requis :

```bash
pip install nltk spacy requests
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_lg
python -m spacy download en_core_web_trf
python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('stopwords')"
pip install spacy pytextrank
pip install sentence-transformers
pip install gensim nltk
pip install scikit-learn
```

## Utilisation

Lancement du projet depuis votre terminal :

```bash
python bookworm.py [BALISE] [NUMERO_DU_LIVRE]
```

### Exemple

```bash
python bookworm.py --card 11
```

Résultat :

```text
Génère l'analyse complète pour : Alice's Adventures in Wonderland
```

## Balises disponibles

Chaque balise exécute un filtre ou une analyse spécifique sur le texte préalablement tokenisé :

- `--lexdiv` : Calcule la diversité lexicale en analysant le ratio entre le nombre de tokens uniques (le vocabulaire) et le nombre total de mots.

- `--entities` : Extrait et liste les entités nommées majeures de l'œuvre, classées en deux catégories distinctes : les personnages et les lieux.

- `--topic` : Analyse le texte pour en extraire et identifier les thèmes principaux et les sujets globaux.

- `--summary` : Génère un résumé automatique textuel détaillé, structuré chapitre par chapitre.

- `--similar` : Parcourt le catalogue local pour identifier et suggérer des livres du Project Gutenberg traitant de thématiques ou de sujets similaires.

- `--card` : Génère une fiche d'identité complète (carte) du livre en combinant toutes les analyses ci-dessus, enrichie de métadonnées complémentaires.

## Structure du projet

Le code est structuré de manière modulaire pour faciliter sa maintenance et son évolution :

- `bookworm.py`  
  Point d'entrée principal du programme, gestion des arguments de la CLI et orchestration du pipeline (téléchargement, nettoyage, tokenisation) et de la lecture des métadonnées contenues dans le catalogue CSV.

- `entities.py`  
  Module autonome dédié au pipeline d'extraction, de vote et de filtrage des personnages et des lieux (propulsé par spaCy et WordNet).

- `lexdiv.py`  
  Calcule la diversité lexicale en analysant le ratio entre le nombre de tokens uniques (vocabulaire) et le nombre total de mots.

- `topic.py`  
  Analyse le texte pour en extraire les thèmes principaux et sujets globaux.

- `summary.py`  
  Génère un résumé automatique textuel détaillé, chapitre par chapitre.

- `similar.py`  
  Parcourt le catalogue local pour identifier et suggérer des livres traitant de thématiques ou de sujets similaires.

---

# 🇬🇧 English version

## Bookworm - Text Book Analyzer

This project allows you to search, download, and analyze literary works from the `.csv` catalog of the Project Gutenberg website.

The script applies a Natural Language Processing (NLP) pipeline enabling automated analysis of literary works.

## Features

- Automatic download of raw text using the book ID.
- Text cleaning (removal of Gutenberg headers and footers).
- Tokenization into sentences and words.
- Lexical analysis.
- Named entity extraction.
- Automatic summarization.
- Topic analysis.
- Similar works search.

## Installation and requirements

```bash
pip install nltk spacy requests
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_lg
python -m spacy download en_core_web_trf
python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('stopwords')"
pip install spacy pytextrank
pip install sentence-transformers
pip install gensim nltk
pip install scikit-learn
```

## Usage

```bash
python bookworm.py [FLAG] [BOOK_ID]
```

## Example

```bash
python bookworm.py --card 11
```

Result:

```text
Generates a full analysis for: Alice's Adventures in Wonderland
```

## Available flags

- `--lexdiv`: Computes lexical diversity...
- `--entities`: Extracts named entities...
- `--topic`: Extracts themes...
- `--summary`: Generates chapter-by-chapter summary
- `--similar`: Finds similar books
- `--card`: Generates full book card

## Project structure

- `bookworm.py` : Main entry point...
- `entities.py` : Named entity extraction...
- `lexdiv.py` : Lexical diversity...
- `topic.py` : Topic analysis...
- `summary.py` : Summary generation...
- `similar.py` : Similarity search
