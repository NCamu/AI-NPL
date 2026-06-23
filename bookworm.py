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



STOPWORDS_NTLK = set(stopwords.words('english'))

STOPWORDS = {

    "had", "to", "that", "very", "few", "were", "a", "an", "the", "in", "on", "of", "and", "or", "is", "was",

    "o","i","ii","iii","iv","v","vi","vii","viii","ix","x","xi","xii","xiii","xiv","xv","xvi","xvii","xviii","xix","xx",

    "oh", "ah", "alas", "hurrah", "eh", "well", "yes", "no", "hello", "please",

    "this", "these", "those", "each", "every", "all", "any", "both", "some", "such", "no", "nor", "not", "other", "another",

    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves",

    "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them",

    "their", "theirs", "themselves", "what", "which", "who", "whom", "whose",

    "about", "above", "after", "against", "along", "among", "around", "at", "before", "behind", "below",

    "beneath", "beside", "between", "beyond", "by", "down", "during", "except", "for", "from", "inside",

    "into", "near", "off", "out", "outside", "over", "past", "through", "throughout", "till", "toward",

    "towards", "under", "underneath", "until", "up", "upon", "with", "within", "without", "but", "because",

    "as", "while", "again", "further", "then", "once", "so", "than",

    "am", "are", "be", "been", "being", "have", "has", "having", "do", "does", "did", "doing", "can",

    "could", "will", "would", "shall", "should", "may", "might", "must",

    "only", "too", "just", "now", "here", "there", "when", "where", "why", "how", "own", "same",

    "don't", "can't", "won't", "isn't", "aren't", "wasn't", "weren't", "haven't", "hasn't", "hadn't",

    "doesn't", "didn't", "shouldn't", "couldn't", "wouldn't", "mustn't", "shan't", "it's", "i'm",

    "you're", "he's", "she's", "we're", "they're", "i've", "you've", "we've", "they've", "i'd",

    "you'd", "he'd", "she'd", "we'd", "they'd", "i'll", "you'll", "he'll", "she'll", "we'll", "they'll",

    's', 't', 'll', 'd', 'm', 've', 're',

    "dont", "cant", "wont", "isnt", "arent", "wasnt", "werent", "havent", "hasnt", "hadnt",

    "doesnt", "didnt", "shouldnt", "couldnt", "wouldnt", "mustnt", "shant", "its", "im",

    "youre", "hes", "shes", "were", "theyre", "ive", "youve", "weve", "theyve", "id",

    "youd", "hed", "shed", "wed", "theyd", "ill", "youll", "hell", "shell", "well", "theyll",

    "monsieur", "madame", "mme", "mille", "mlle", "lord", "lady", "count", "comte", "marquis", "duchesse", "abbé", "monseigneur", "sir"

}


def stop_word(fichier_entree: str):

    token = []

    for ligne in fichier_entree:

        mots_bruts = re.split(r"[\s\-\—\.\,\!\?\:\;\'\’\"\_]+", ligne)

        for mot in mots_bruts:

            cleaned = mot.lower()

            if cleaned and cleaned not in STOPWORDS and cleaned not in STOPWORDS_NTLK:

                token.append(cleaned)

    return token


def extract_top_words(lines: list[str], n: int = 10) -> list[str]:

    tokens = stop_word(lines)  

    filtered_tokens = [word for word in tokens if word != 'chapter']

    top_n = Counter(filtered_tokens).most_common(n)

    return [word for word, count in top_n]


#########################--NETTOYAGE--############################################################

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


#####
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

######

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


############################--personnages et location--#########################################################

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



def supprimer_doublons_ordonne(liste_avec_doublons):

    return list(dict.fromkeys(liste_avec_doublons))



def supprimer_doublons_again(liste_avec_doublons):

    return list(set(liste_avec_doublons))
        
#######################################################################################################

def info(id:int):  


    found_book = False

    with open('pg_catalog.csv', mode = 'r', encoding = 'utf-8') as fichier:

        read_csv = csv.DictReader(fichier)

        for ligne in read_csv:

            if ligne['Text#'] == str(id):

                info_book = {

                    'id': ligne['Text#'],

                    'title': ligne['Title'],

                    'authors': ligne['Authors'],

                    'bookshelves': ligne['Bookshelves']

                   }
                return info_book 

                found_book = True

                break

    if not found_book:

        print(f"error: no book found with ID#{id}.")

        sys.exit(1)



#################

def lexdiv(id:int) -> dict[str,int|float]:
    with open(f"{id}_td.txt", "r", encoding="utf-8") as f:
        lignes = f.read()
    
    lignes=re.sub(r"[^\w\s]|_", " ", lignes)
    token=lignes.split()

        #print (word)
    tok=len(token)
    typ=len(set(token))
    compteur = Counter(token)
    hap=sum(1 for freq in compteur.values() if freq == 1)
    ttr=typ/tok if tok > 0 else 0
    mwl=sum(len(word) for word in token) / tok if tok > 0 else 0
    mwf=tok/typ if typ > 0 else 0

    return  {"tok":tok,
            "typ":typ,
            "hap":hap,
            "ttr":ttr,
            "mwl":mwl,
            "mwf":mwf
            }


#################


def topic(id: int) -> dict[int, list[str]]:

    with open(str(id) + "_td.txt", "r", encoding="utf-8") as f:

        lignes = f.readlines()


    sec ={"section":id}

    return sec

#################

def entities(id: int):
    #nlp = spacy.load("en_core_web_sm")
    #nlp = spacy.load("en_core_web_lg")
    nlp = spacy.load("en_core_web_trf")

    with open(f"{id}_sent_tok.txt", "r", encoding="utf-8") as f:
        text = f.read()

    phrases = [p.strip() for p in text.split('\n') if p.strip()]

    from collections import defaultdict, Counter
    entity_votes = defaultdict(Counter)

    LABELS_LIEUX = {"GPE", "LOC", "FAC"}
    pattern_bruit = re.compile(
        r'^(chapter|part|book|v|x|i|l|m|c|d|xv|lxvi|xliv|xxix|xxxiv|xxxix|xlix|li|v|vi|vii|viii|ix|xi|xii|xiii|xiv|xvi|xvii|xviii|xix|xx)\b',
        re.IGNORECASE
    )

    # 1. On allège la blacklist pour autoriser les titres autonomes qui font de vrais personnages (ex: Queen, King)
    BLACKLIST_PERSO = {
        "duke", "prince", "princess", "constable", "principal", "guards",
        "guardsman", "guardsmen", "musketeer", "inseparables", "post",
        "englishman", "englishmen", "frenchman", "frenchmen", "gascon", "gascons",
        "norman", "huguenot", "huguenots", "puritan", "jesuit", "hebrews",
        "jew", "negro", "morbleu", "holà", "god", "satan", "antichrist", "saints",
        "long tale", "said", "beau", "page", "preface"
    }

    BLACKLIST_LIEUX = {
        "béarnais", "rochellais", "de la", "commissary", "church", "providence", 
        "pale", "isle", "de tréville's", "dessessart's"
    }

    # 2. Nettoyage : On retire les vrais lieux d'ici (Festubert, La Prée, etc. n'ont rien à faire côté Perso !)
    BLACKLIST_LIEUX_PERSO = {
        "antoine", "dessessart", "séguier", "de cahusac", "cahusac",
        "de laffemas", "laffemas", "de voiture", "voiture",
        "de chevreuse", "chevreuse", "comtesse de la fère"
    }

    WHITELIST_PERSO = {
    "athos", "porthos", "aramis",
    "rochefort", "buckingham", "mousqueton",
    "bonacieux", "coquenard", "king louis xiii",
    "laporte", "marion de lorme", "de tréville",
    "de winter"
}







    # --- ÉTAPE 1 : Collecte des votes par entité ---
    for doc in nlp.pipe(phrases):
        for enti in doc.ents:
            nom_entite = enti.text.strip(" \t\n\r.,;:!?\"''""—_()[]-")

            if not nom_entite or nom_entite[0].islower():
                continue

            if len(nom_entite) <= 2:
                continue

            if nom_entite.isupper() and nom_entite.lower() not in {"france", "paris", "london", "rome", "spain", "england"}:
                continue

            if pattern_bruit.match(nom_entite) or is_section(nom_entite):
                continue

            if any(char in nom_entite for char in {':', ';', '!', '?', '*', '"', ','}):
                continue

            if nom_entite.lower().startswith(("the ", "a ", "an ", "o ")):
                mots_det = nom_entite.split()
                if len(mots_det) > 1:
                    nom_entite = " ".join(mots_det[1:]).strip(" \t\n\r.,;:!?\"''""—_()[]-")

            while True:
                mots_courants = nom_entite.split()
                if mots_courants and (mots_courants[0].lower() in STOPWORDS or mots_courants[0].lower() in {"mdot", "mmdot"}):
                    if len(mots_courants) > 1:
                        nom_entite = " ".join(mots_courants[1:]).strip(" \t\n\r.,;:!?\"''""—_()[]-")
                    else:
                        break
                else:
                    break

            if len(nom_entite) <= 2:
                continue

            mots_fin = nom_entite.split()
            if len(mots_fin) > 1 and mots_fin[-1].islower():
                dernier_mot_clean = mots_fin[-1].split('-')[-1]
                if wordnet.synsets(dernier_mot_clean, pos=wordnet.VERB) or dernier_mot_clean.endswith("entered"):
                    mots_fin.pop()
                    nom_entite = " ".join(mots_fin).strip(" \t\n\r.,;:!?\"''""—_()[]-")

            if len(nom_entite) <= 2:
                continue

            if nom_entite.lower() in STOPWORDS or nom_entite.lower() in STOPWORDS_NTLK or nom_entite.lower() in {"mdot", "mmdot"}:
                continue

            if nom_entite.lower() in {"end", "esq", "page", "preface", "chapter", "ibid", "patience", "holà", "remain", "besides", "buff", "jewel", "inn"}:
                continue

            if nom_entite.lower().startswith(("rue ", "avenue ", "boulevard ", "faubourg ")):
                entity_votes[nom_entite]["LOC"] += 1
                continue
            # Dans ton check final en bas de l'ÉTAPE 1, ajoute :
            if nom_entite.lower() in {"mass", "pardieu", "parbleu", "morbleu", "holà"}:
                continue
            if enti.label_ == "PERSON":
                entity_votes[nom_entite]["PERSON"] += 1
            elif enti.label_ in LABELS_LIEUX:
                entity_votes[nom_entite]["LOC"] += 1
            elif enti.label_ == "ORG":
                entity_votes[nom_entite]["ORG"] += 1

    # --- ÉTAPE 2 : Résolution sémantique et répartition perso / lieux ---
    tt_perso = []
    tt_lieux = []

    # On dote notre référentiel des villes et localités françaises clés des Mousquetaires et d'Alice
    VRAIS_LIEUX = {
        "france", "paris", "london", "la rochelle", "spain", "austria",
        "england", "brussels", "amsterdam", "rome", "calais", "boulogne",
        "lille", "bastille", "louvre", "wonderland", "meung", "tarbes", 
        "béarn", "amiens", "rouen", "chantilly", "bondy", "pontoise", 
        "montdidier", "portsmouth", "tyburn", "lilliers", "armentières", 
        "festubert", "fromelles", "charente", "notre dame", "la prée", 
        "angoutin", "mandé", "dompierre", "perigny", "germain", "denis",
        "saint-mandé", "croquet-ground", "caucus-race", "northumbria", "harpe", 
        "vaugirard","béthune", "la grève", "berry", "bed of justice"
    }

    for entite, votes in entity_votes.items():
        total_citations = sum(votes.values())

        if total_citations < 2 and entite.lower() not in {
            "alice", "wonderland", "white rabbit", "march hare", "cheshire cat", 
            "queen of hearts", "king of hearts", "knave of hearts", "duchess"
        }:
            continue

        label_dominant = max(votes, key=votes.get)
        mots_ent = entite.split()
        if not mots_ent:
            continue

        dernier_mot = mots_ent[-1].lower()
        syns_noun = wordnet.synsets(dernier_mot, pos=wordnet.NOUN)
        lexnames = {s.lexname() for s in syns_noun} if syns_noun else set()

        # Dans ta boucle ÉTAPE 2, juste après le calcul de label_dominant :
        if entite.lower() in WHITELIST_PERSO:
            tt_perso.append(entite)
            continue


        # Forcer en PERSON si le mot final indique explicitement un être vivant ou un titre de personnage majeur
        if label_dominant in {"LOC", "ORG"}:
            if any(lex in {'noun.person', 'noun.animal'} for lex in lexnames) or dernier_mot in {
                'rabbit', 'hare', 'cat', 'mouse', 'crab', 'pigeon', 'caterpillar',
                'turtle', 'dormouse', 'musketeer', 'guardsman', 'guardsmen', 'king', 'queen', 'knave'
            }:
                label_dominant = "PERSON"

        if label_dominant == "PERSON":
            if len(mots_ent) == 1:
                v_syns = wordnet.synsets(dernier_mot, pos=wordnet.VERB)
                if v_syns and not syns_noun:
                    continue
                if dernier_mot in {"said", "beau", "besides", "remain", "yez", "buff"}:
                    continue

            # Validation Sémantique WordNet
            if syns_noun and not any(lex in {'noun.person', 'noun.animal', 'noun.group'} for lex in lexnames):
                # 🔥 SÉCURITÉ COMPOSÉS : Si l'entité contient un titre de personnage, on ne la rejette pas !
                # Sauve d'un coup "Queen of Hearts", "King of Hearts", etc.
                titres_autorises = {'king', 'queen', 'knave', 'duchess', 'hatter', 'caterpillar', 'rabbit', 'hare', 'cardinal', 'captain', 'count'}
                if not any(t in [m.lower() for m in mots_ent] for t in titres_autorises):
                    if dernier_mot not in {'majesty', 'grace', 'eminence', 'highness', 'lord', 'lady', 'footman', 'gryphon'}:
                        continue

        # Attribution stricte basée sur le label dominant final nettoyé (Bloque la contagion)
        est_un_personnage = (label_dominant == "PERSON")

        # Filet de sécurité géographique absolu (Une adresse ou un vrai lieu reste un lieu)
        if entite.lower() in VRAIS_LIEUX or entite.lower().startswith(("rue ", "avenue ", "boulevard ", "faubourg ")):
            est_un_personnage = False

        if est_un_personnage:
            if entite.lower() in BLACKLIST_PERSO:
                continue
            tt_perso.append(entite)
        else:
            if entite.lower() in BLACKLIST_LIEUX:
                continue
            if entite.lower() in BLACKLIST_LIEUX_PERSO:
                tt_perso.append(entite)
                continue
            tt_lieux.append(entite)

    # --- ÉTAPE 3 : Harmonisation et nettoyage final ---
    perso_harmonises = []
    for p in tt_perso:
        if p.lower() == "rabbit":
            perso_harmonises.append("White Rabbit")
        elif p.lower() == "cat":
            perso_harmonises.append("Cheshire Cat")
        elif p.lower() == "hare":
            perso_harmonises.append("March Hare")
        else:
            perso_harmonises.append(p)

    def fusionner_variantes(liste):
        vus = {}
        for nom in liste:
            cle = nom.lower()
            if cle not in vus:
                vus[cle] = nom
            else:
                if nom[0].isupper() and not vus[cle][0].isupper():
                    vus[cle] = nom
        liste_dedup = list(vus.values())

        a_supprimer = set()
        for i, nom_court in enumerate(liste_dedup):
            mots_court = set(nom_court.lower().split())
            for j, nom_long in enumerate(liste_dedup):
                if i == j:
                    continue
                mots_long = set(nom_long.lower().split())
                if mots_court < mots_long:
                    a_supprimer.add(nom_court.lower())
                    break

        return [n for n in liste_dedup if n.lower() not in a_supprimer]

    perso_clean = fusionner_variantes(supprimer_doublons_ordonne(perso_harmonises))
    lieux_clean = fusionner_variantes(supprimer_doublons_ordonne(tt_lieux))

    lieux_clean = [l.title() if l.isupper() else l for l in lieux_clean]

    print(f"✅ Extraction terminée !")
    print(f"   - {len(perso_clean)} personnages uniques trouvés.")
    print(f"   - {len(lieux_clean)} lieux uniques trouvés.")

    return {
        "persos": perso_clean,
        "lieux": lieux_clean
    }
    
#################




##################

def summary(id :int) -> str:

    sum = {"summary":id}

    return sum

#################

def similar(id :int):  

    found_book = False

    with open('pg_catalog.csv', mode = 'r', encoding = 'utf-8') as fichier:

        read_csv = list(csv.DictReader(fichier))

        book_list=[]            

        for ligne in read_csv:



            if ligne['Text#'] == str(id):

                info_book = {

                    'id': ligne['Text#'],

                    'bookshelves': ligne['Bookshelves'],

                   }

                found_book = True

                break



        if not found_book:

            print(f"error: no book found with ID#{id}.")

            sys.exit(1)



        for i in read_csv:

            if info_book['bookshelves'] == i['Bookshelves'] and i["Text#"] != info_book["id"]:

                book_list.append(

                    {#'id':i['Text#'],

                    i['Title'],

                    })

               

    return book_list[:5]

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

    elif arg.similar:

      print(similar(a))

    else:
        print("run --card by default if you don't specify a flag:")
        #card(a)
        sys.exit(1)





if __name__ == "__main__":

    main()
    