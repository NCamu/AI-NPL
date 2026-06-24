import argparse

import sys

import csv

import requests

import re

import os

from collections import Counter , defaultdict

import nltk

import spacy

from nltk.stem import PorterStemmer, WordNetLemmatizer

from nltk.corpus import wordnet , stopwords

from nltk import ne_chunk, pos_tag

from nltk import word_tokenize as nltk_word_tokenize

from nltk.corpus import stopwords

from nltk.tokenize import sent_tokenize

#from nlp.io import load_book_text, read_cache, write_cache

#import entities
from STOPWORDS import STOPWORDS

from entities import entities
from info import info
from lexdiv import lexdiv
from similar import similar
from topic import topic
from summary import summary



STOPWORDS_NTLK = set(stopwords.words('english'))

#################

#################
def stop_word(fichier_entree: str):

    token = []

    for ligne in fichier_entree:

        mots_bruts = re.split(r"[\s\-\—\.\,\!\?\:\;\'\’\"\_]+", ligne)

        for mot in mots_bruts:

            cleaned = mot.lower()

            if cleaned and cleaned not in STOPWORDS and cleaned not in STOPWORDS_NTLK:

                token.append(cleaned)

    return token
#################

#################

def extract_top_words(lines: list[str], n: int = 10) -> list[str]:

    tokens = stop_word(lines)  

    filtered_tokens = [word for word in tokens if word != 'chapter']

    top_n = Counter(filtered_tokens).most_common(n)

    return [word for word, count in top_n]


#################

#################

def dl_book(id):
    filename = f"book_{id}.txt"
    
    # 💡 Si le livre est déjà sur le disque, on évite de requêter le serveur
    if os.path.exists(filename):
        print(f"📖 {filename} trouvé en local. Utilisation du cache.")
        return

    url = f"https://www.gutenberg.org/ebooks/{id}.txt.utf-8"
    # Ajout d'un User-Agent pour éviter de se faire bloquer/rejeter par Gutenberg
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        print(f"🌐 Téléchargement du livre {id} depuis Gutenberg...")
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            resp.encoding = 'utf-8'
            with open(filename, "w", encoding="utf-8") as file:
                file.write(resp.text)
        else:
            print(f"❌ Erreur HTTP {resp.status_code} : Impossible de récupérer le livre.")
            sys.exit(1)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur réseau / Timeout : {e}")
        print("Le serveur Gutenberg est injoignable et aucun fichier local n'a été trouvé.")
        sys.exit(1)


#################

#################
def top_down(id:int):

    with open(f"book_{id}.txt", "r", encoding="utf-8") as f:

            lignes = f.readlines()



    if len(lignes) <= (60 + 703):

        print(f"Attention : Le fichier ne contient que {len(lignes)} lignes. Impossible de supprimer 60 + 703 lignes.")

        return



    txt_nettoyees = lignes[60:-703]  

    texte_complet = "".join(txt_nettoyees)

   

    texte_final = texte_complet.replace("\n\n\n", "###MARKER###")

    texte_final = texte_final.replace("\n\n", ".")

    texte_final = texte_final.replace("\n", " ")

    texte_final = texte_final.replace("###MARKER###", ".\n")  



    with open(str(id)+"_td.txt", "w", encoding="utf-8") as f:

        f.writelines(texte_final)

#################

#################

def sent_tok(id: int):
    input_file = f"{id}_td.txt"
    output_file = f"{id}_sent_tok.txt"

    if not os.path.exists(input_file):
        print(f"❌ Erreur : {input_file} introuvable.")
        return

    with open(input_file, mode='r', encoding='utf-8') as f:
        text = f.read()


    # =========================================================================
    # CORRECTION ETAPE 1 : Nettoyage strict des lignes de points
    # [^\S\r\n] cible uniquement les espaces horizontaux (pas les \n).
    # Ainsi, la regex reste bloquée sur sa ligne et nettoie parfaitement les successions de "."
    # =========================================================================
    text = re.sub(r'^[^\S\r\n]*\.+[^\S\r\n]*$', '', text, flags=re.MULTILINE)

    # Convertir les séparateurs de section Gutenberg '*' en sauts de ligne
    text = re.sub(r'\*', '\n', text)

    # 💡 EXCEPTION : Protection de "M." et "MM." via des placeholders
    text = re.sub(r'\bMM\.', '__MM_DOT__', text)
    text = re.sub(r'\bM\.', '__M_DOT__', text)

    # ETAPE 2 : Normalisation des espaces et sauts de ligne globaux
    cleaned = re.sub(r'\s+', ' ', text).strip()

    # ETAPE 3 : Découpage en phrases
    sentences = re.split(r'(?<=[.!?])\s+', cleaned)

    # ETAPE 4 : Nettoyage chirurgical des phrases pour NLTK
    cleaned_sentences = []
    for sentence in sentences:
        s = sentence
        
        # 1. Standardisation des guillemets et apostrophes pour le tokenizer ASCII de NLTK
        s = s.replace('’', "'").replace('“', '"').replace('”', '"')
        
        # 2. Suppression des underscores d'italique (ex: _very_ -> very)
        s = re.sub(r'_', '', s)
        
        # 3. Remplacement des points INTERNES uniquement (ex: the.bank -> the bank)
        s = re.sub(r'(?<=\w)\.(?=\w)', ' ', s)
        
        # 4. Remplacement des points de suspension ou doubles points résiduels par un espace
        s = re.sub(r'\.{2,}', ' ', s)
        
        # 5. Nettoyage des doubles espaces potentiels
        s = re.sub(r'\s{2,}', ' ', s).strip()
        
        # 6. RESTAURATION DES EXCEPTIONS
        s = re.sub(r'__MM_DOT__', 'MM.', s)
        s = re.sub(r'__M_DOT__', 'M.', s)
        
        # =========================================================================
        # 💡 SÉCURITÉ NER : Si la ligne est vide ou ne contient QUE des points/espaces,
        # on la rejette pour éviter de polluer le chunker NLTK
        # =========================================================================
        if not s or re.match(r'^[\s.]+$', s):
            continue
            
        cleaned_sentences.append(s)

    # ETAPE 5 : Écriture du résultat (une phrase propre par ligne)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(cleaned_sentences))
    
    
######

######

def is_section(line):

    line = line.strip().upper()


    patterns = [

        r"^CHAPTER\s+[IVXLCDM\d]+$",

        r"^PART\s+[IVXLCDM\d]+$",

        r"^BOOK\s+[IVXLCDM\d]+$",

        r"^(M{0,4})(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"

    ]

    return any(re.match(pattern, line) for pattern in patterns)


#################

#################
def get_wordnet_pos(treebank_tag):

    """Convertit les tags Penn Treebank en formats lisibles par le WordNetLemmatizer"""

    if treebank_tag.startswith('J'):

        return wordnet.ADJ

    elif treebank_tag.startswith('V'):

        return wordnet.VERB

    elif treebank_tag.startswith('N'):

        return wordnet.NOUN

    elif treebank_tag.startswith('R'):

        return wordnet.ADV

    else:

        return wordnet.NOUN  # Par défaut, on considère les mots comme des noms pour la lemmatisation

#################

#################

def supprimer_doublons_ordonne(liste_avec_doublons):

    return list(dict.fromkeys(liste_avec_doublons))


def supprimer_doublons_again(liste_avec_doublons):

    return list(set(liste_avec_doublons))
        

#################

#################

def card(id :int):

    rez={

    "info":info(id),

    "lexdiv":lexdiv(id),

    "topic":topic(id),

    "entities":entities(id),

    "summary":summary(id),

    "similar": similar(id)

    }
    return rez

############################--MEME GENRE DE LIVRES--#########################################################

def main():

    parser = argparse.ArgumentParser (

        prog = "bookworm.py",

        description = " info or dl a book from gutenberg"

    )

    parser.add_argument("--lexdiv", action = "store_true", help="liguistic diversity")

    parser.add_argument("--topic", action = "store_true", help="topic of the book")

    parser.add_argument("--entities", action="store_true", help="entities names, charaters and places")

    parser.add_argument("--summary", action="store_true", help="summary of the book")

    parser.add_argument("--similar", action="store_true", help="similar book")

    parser.add_argument("--card", action="store_true", help="all previous options")



    parser.add_argument("number",nargs = "*", help="book id")

    arg = parser.parse_args()



    if len(arg.number) != 1:

        print("error: just book ID needed")

        sys.exit(1)



    try:

        a = int(arg.number[0])

    except ValueError:

        print("error: invalide arg")

        sys.exit(1)



    dl_book(a)

    top_down(a)

    sent_tok(a)

    if arg.card:

        print(card(a))

    elif arg.lexdiv:

      print(  lexdiv(a))

    elif arg.topic:

      print(  topic(a))

    elif arg.entities:

      print(entities(a))

    elif arg.summary:

      print(summary(a))  

    elif arg.similar:

      print(similar(a))

    else:
        print("run --card by default if you don't specify a flag:")
        #card(a)
        sys.exit(1)





if __name__ == "__main__":

    main()
    