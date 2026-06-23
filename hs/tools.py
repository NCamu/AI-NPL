#!/usr/bin/env python3
"""CLI toolkit: Project Gutenberg utilities and NLP."""

import argparse
import csv
import json
import re
import string
import sys
from pathlib import Path

import nltk
import requests
from nltk import pos_tag, word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.corpus import wordnet

GUTENBERG_CSV = Path(__file__).resolve().parent / "gutenberg.csv"
GUTENBERG_HEADER = re.compile(
    r"\*\*\* START OF (THIS|THE) PROJECT GUTENBERG EBOOK.*?\n",
    re.IGNORECASE | re.DOTALL,
)
GUTENBERG_FOOTER = re.compile(
    r"\*\*\* END OF (THIS|THE) PROJECT GUTENBERG EBOOK.*",
    re.IGNORECASE | re.DOTALL,
)


def ensure_nltk_data() -> None:
    for pkg in (
        "punkt",
        "punkt_tab",
        "stopwords",
        "averaged_perceptron_tagger",
        "averaged_perceptron_tagger_eng",
        "wordnet",
        "maxent_ne_chunker",
        "maxent_ne_chunker_tab",
        "words",
    ):
        nltk.download(pkg, quiet=True)


# --- Gutenberg module ---


def load_gutenberg_catalog(csv_path: Path = GUTENBERG_CSV) -> list[dict]:
    if not csv_path.exists():
        print(f"error: catalog not found: {csv_path}", file=sys.stderr)
        sys.exit(1)
    with csv_path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def info(book_id: str, csv_path: Path = GUTENBERG_CSV) -> dict:
    catalog = load_gutenberg_catalog(csv_path)
    book_id = str(book_id).strip()
    for row in catalog:
        if str(row.get("id", "")).strip() == book_id:
            return {
                "id": str(row["id"]),
                "title": row["title"],
                "authors": row["authors"],
                "bookshelves": row["bookshelves"],
            }
    print(f"error: book id {book_id} not found in catalog", file=sys.stderr)
    sys.exit(1)


def gutenberg_text_url(book_id: str) -> str:
    bid = str(book_id).strip()
    return f"https://www.gutenberg.org/files/{bid}/{bid}-0.txt"


def download(book_id: str, output_dir: Path | None = None) -> Path:
    bid = str(book_id).strip()
    url = gutenberg_text_url(bid)
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
    except requests.RequestException as e:
        alt = f"https://www.gutenberg.org/cache/epub/{bid}/pg{bid}.txt"
        try:
            response = requests.get(alt, timeout=60)
            response.raise_for_status()
        except requests.RequestException:
            print(f"error: failed to download book {bid}: {e}", file=sys.stderr)
            sys.exit(1)
    text = response.content.decode("utf-8", errors="replace")
    dest_dir = output_dir or Path.cwd()
    dest_dir.mkdir(parents=True, exist_ok=True)
    out_path = dest_dir / f"{bid}.txt"
    out_path.write_text(text, encoding="utf-8")
    return out_path


def clean(text: str, lower: bool = False) -> str:
    cleaned = GUTENBERG_HEADER.sub("", text)
    cleaned = GUTENBERG_FOOTER.sub("", cleaned)
    cleaned = cleaned.replace("\t", " ")
    cleaned = re.sub(r" +", " ", cleaned)
    cleaned = cleaned.strip()
    if lower:
        cleaned = cleaned.lower()
    return cleaned


# --- NLP helpers ---


def remove_stopwords(tokens: list[str]) -> list[str]:
    stops = set(stopwords.words("english"))
    return [t for t in tokens if t.lower() not in stops]


def remove_punctuation(tokens: list[str]) -> list[str]:
    table = str.maketrans("", "", string.punctuation)
    return [t.translate(table) for t in tokens if t.translate(table)]


def wordnet_pos(treebank_tag: str) -> str:
    if treebank_tag.startswith("J"):
        return wordnet.ADJ
    if treebank_tag.startswith("V"):
        return wordnet.VERB
    if treebank_tag.startswith("N"):
        return wordnet.NOUN
    if treebank_tag.startswith("R"):
        return wordnet.ADV
    return wordnet.NOUN


def lemmatize_with_pos(tokens: list[str]) -> list[str]:
    lemmatizer = WordNetLemmatizer()
    tagged = pos_tag(tokens)
    return [
        lemmatizer.lemmatize(word, pos=wordnet_pos(tag))
        for word, tag in tagged
    ]


# --- NLP module ---


def tokenize(
    text: str,
    *,
    sentences: bool = False,
    drop_stop: bool = False,
    drop_punct: bool = False,
) -> list[str] | list[list[str]]:
    if sentences:
        sents = sent_tokenize(text)
        if drop_stop or drop_punct:
            return [
                _postprocess_tokens(word_tokenize(s), drop_stop, drop_punct)
                for s in sents
            ]
        return sents
    tokens = word_tokenize(text)
    return _postprocess_tokens(tokens, drop_stop, drop_punct)


def _postprocess_tokens(
    tokens: list[str], drop_stop: bool, drop_punct: bool
) -> list[str]:
    if drop_punct:
        tokens = remove_punctuation(tokens)
    if drop_stop:
        tokens = remove_stopwords(tokens)
    return tokens


def postag(text: str) -> list[tuple[str, str]]:
    tokens = word_tokenize(text)
    return pos_tag(tokens)


def normalize(tokens: list[str], *, stem: bool = False) -> list[str]:
    if stem:
        stemmer = PorterStemmer()
        return [stemmer.stem(t) for t in tokens]
    return lemmatize_with_pos(tokens)


# --- CLI ---


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Gutenberg and NLP CLI toolkit")
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("--info", metavar="ID", help="Book metadata from local CSV")
    group.add_argument("--download", metavar="ID", help="Download Gutenberg book text")
    group.add_argument("--clean", metavar="TEXT", help="Clean Gutenberg raw text")
    group.add_argument("--tokenize", metavar="TEXT", help="Tokenize text")
    group.add_argument("--postag", metavar="TEXT", help="POS tagging")
    group.add_argument("--normalize", metavar="TOKENS", nargs="+", help="Normalize tokens")

    parser.add_argument("--lower", action="store_true", help="Lowercase cleaned text")
    parser.add_argument("--sent", action="store_true", help="Sentence tokenization")
    parser.add_argument("--stop", action="store_true", help="Remove stopwords")
    parser.add_argument("--punct", action="store_true", help="Remove punctuation")
    parser.add_argument("--stem", action="store_true", help="Stem instead of lemmatize")

    return parser


def main() -> None:
    ensure_nltk_data()
    parser = build_parser()
    args = parser.parse_args()

    if args.info is not None:
        print(json.dumps(info(args.info), ensure_ascii=False))
        return

    if args.download is not None:
        path = download(args.download)
        print(path)
        return

    if args.clean is not None:
        print(clean(args.clean, lower=args.lower))
        return

    if args.tokenize is not None:
        result = tokenize(
            args.tokenize,
            sentences=args.sent,
            drop_stop=args.stop,
            drop_punct=args.punct,
        )
        print(result)
        return

    if args.postag is not None:
        print(postag(args.postag))
        return

    if args.normalize is not None:
        print(normalize(args.normalize, stem=args.stem))


if __name__ == "__main__":
    main()
