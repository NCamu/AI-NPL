import re
from collections import Counter, defaultdict
from nltk.corpus import stopwords, wordnet
import spacy
from STOPWORDS import STOPWORDS, SPE_EXCLU
from CLUES import PREPOSITIONS_LIEUX, TYPE_LIEUX, ORG_KEYWORDS, TITRES, SPEAK_WORD, PONCT

def character_for_sure(mot):
    try:
        for syn in wordnet.synsets(mot.lower()):
            for hyper in syn.hypernyms():
                if any(word in hyper.name() for word in SPEAK_WORD):
                    return True
        return False
    except Exception:
        return False

STOPWORDS_NTLK = set(stopwords.words('english'))

def ressemble_a_un_lieu(mot):
    try:
        if mot.lower() in TYPE_LIEUX:
            return True
        synsets = wordnet.synsets(mot.lower(), pos=wordnet.NOUN)
        
        # 🚀 PROTECTION : Si le mot désigne un animal ou un humain dans WordNet, 
        # on refuse de le considérer comme un lieu à cause d'un sens rare (ex: Crab/Constellation)
        lexnames = {syn.lexname() for syn in synsets}
        if any(lex in {"noun.person", "noun.animal"} for lex in lexnames):
            return False

        for syn in synsets:
            lex = syn.lexname()
            if "location" in lex or "place" in lex or "region" in lex:
                return True
        return False
    except Exception:
        return False

def is_section(line):
    line = line.strip().upper()
    patterns = [
        r"^CHAPTER\s+[IVXLCDM\d]+$",
        r"^PART\s+[IVXLCDM\d]+$",
        r"^BOOK\s+[IVXLCDM\d]+$",
        r"^(M{0,4})(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"
    ]
    return any(re.match(pattern, line) for pattern in patterns)

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


def entities(id: int):
    try:
        nlp = spacy.load("en_core_web_trf")
    except OSError:
        nlp = spacy.load("en_core_web_lg")

    with open(f"{id}_sent_tok.txt", "r", encoding="utf-8") as f:
        text = f.read()

    phrases = [p.strip() for p in text.split('\n') if p.strip()]

    entity_votes = defaultdict(Counter)
    LABELS_LIEUX = {"GPE", "LOC", "FAC"}
    
    pattern_bruit = re.compile(
        r'^(chapter|part|book|v|x|i|l|m|c|d|xv|lxvi|xliv|xxix|xxxiv|xxxix|xlix|li|v|vi|vii|viii|ix|xi|xii|xiii|xiv|xvi|xvii|xviii|xix|xx)\b',
        re.IGNORECASE
    )

    GLOBAL_EXCLUSIONS = SPE_EXCLU

    TITRES_PERSONNAGES = TITRES

    # --- ÉTAPE 1 : Collecte ---
    for doc in nlp.pipe(phrases):
        for enti in doc.ents:
            if enti.label_ in {"DATE", "TIME", "CARDINAL", "ORDINAL", "QUANTITY", "PERCENT", "MONEY", "NORP"}:
                continue

            nom_entite = enti.text.strip(" \t\n\r.,;:!?\"''""—_()[]-")
            if not nom_entite:
                continue

            mots_dep = nom_entite.split()
            if mots_dep and mots_dep[0].lower() in {"the", "a", "an", "o"}:
                if len(mots_dep) > 1:
                    nom_entite = " ".join(mots_dep[1:]).strip(" \t\n\r.,;:!?\"''""—_()[]-")
                else:
                    continue

            nom_entite = re.sub(r"['’](ll|s|d|re|ve|m)$", "", nom_entite, flags=re.IGNORECASE).strip()

            if not nom_entite or nom_entite[0].islower() or len(nom_entite) <= 2:
                continue

            if nom_entite.lower() == "queen" and "queen of hearts" in doc.text.lower():
                nom_entite = "Queen of Hearts"
            elif nom_entite.lower() == "king" and "king of hearts" in doc.text.lower():
                nom_entite = "King of Hearts"
            elif nom_entite.lower() == "knave" and "knave of hearts" in doc.text.lower():
                nom_entite = "Knave of Hearts"

            if nom_entite.lower() in GLOBAL_EXCLUSIONS or nom_entite.lower() in STOPWORDS or nom_entite.lower() in STOPWORDS_NTLK:
                continue

            if "--" + nom_entite in doc.text or nom_entite + "--" in doc.text:
                continue

            if len(nom_entite.split()) == 1:
                mot_low = nom_entite.lower()
                mot_singulier = mot_low.rstrip('s') if (mot_low.endswith('s') and len(mot_low) > 3) else mot_low
                
                syns_noun = wordnet.synsets(mot_low, pos=wordnet.NOUN) or wordnet.synsets(mot_singulier, pos=wordnet.NOUN)
                lexs_noun = {s.lexname() for s in syns_noun}
                if "noun.food" in lexs_noun and not any(l in {"noun.person", "noun.animal"} for l in lexs_noun):
                    continue
                if mot_low.endswith("ing") and mot_low not in TITRES:
                    continue

            if nom_entite.isupper() and nom_entite.lower() not in {"france", "paris", "london", "rome", "spain", "england"}:
                continue

            if pattern_bruit.match(nom_entite) or is_section(nom_entite):
                continue

            if any(char in nom_entite for char in PONCT):
                continue

            while True:
                mots_courants = nom_entite.split()
                if mots_courants and (mots_courants[0].lower() in STOPWORDS or mots_courants[0].lower() in {"mdot", "mmdot"}):
                    if len(mots_courants) > 1:
                        nom_entite = " ".join(mots_courants[1:]).strip(" \t\n\r.,;:!?\"''""—_()[]-")
                    else:
                        break
                else:
                    break

            if len(nom_entite) <= 2 or nom_entite.lower() in GLOBAL_EXCLUSIONS:
                continue

            mots_fin = nom_entite.split()
            if len(mots_fin) > 1 and mots_fin[-1].islower():
                dernier_mot_clean = mots_fin[-1].split('-')[-1]
                if wordnet.synsets(dernier_mot_clean, pos=wordnet.VERB) or dernier_mot_clean.endswith("entered"):
                    mots_fin.pop()
                    nom_entite = " ".join(mots_fin).strip(" \t\n\r.,;:!?\"''""—_()[]-")

            mots_entite = nom_entite.lower().split()
            if mots_entite and mots_entite[0] in TYPE_LIEUX:
                entity_votes[nom_entite]["LOC"] += 1
                continue

            if enti.label_ == "PERSON":
                entity_votes[nom_entite]["PERSON"] += 1
            elif enti.label_ in LABELS_LIEUX:
                entity_votes[nom_entite]["LOC"] += 1
            elif enti.label_ == "ORG":
                entity_votes[nom_entite]["ORG"] += 1

    # --- ÉTAPE 2 : Répartition et Scoring ---
    tt_perso = []
    tt_lieux = []
    tt_orgs = []

    nombre_total_phrases = len(phrases)

    for entite, votes in entity_votes.items():
        total_citations = sum(votes.values())

        if total_citations < 2:
            continue

        if entite.lower() in GLOBAL_EXCLUSIONS:
            continue

        perso_score = votes["PERSON"] * 3
        lieu_score = votes["LOC"] * 3
        org_score = votes["ORG"] * 3

        mots_ent = entite.split()
        if not mots_ent:
            continue

        mots_ent_lower = [m.lower() for m in mots_ent]
        dernier_mot = mots_ent[-1].lower()
        frequence = total_citations / nombre_total_phrases

        if frequence > 0.005:
            perso_score += 1
        if frequence > 0.01:
            perso_score += 1

        if any(titre in mots_ent_lower for titre in TITRES_PERSONNAGES):
            if not any(o in mots_ent_lower for o in ORG_KEYWORDS) and not any(l in mots_ent_lower for l in TYPE_LIEUX):
                perso_score += (org_score + lieu_score + 50)

        if character_for_sure(dernier_mot):
            perso_score += 10  

        synsets = wordnet.synsets(dernier_mot, pos=wordnet.NOUN)
        lexnames = {s.lexname() for s in synsets}

        if any(lex in {"noun.person", "noun.animal"} for lex in lexnames):
            perso_score += 2

        if ressemble_a_un_lieu(dernier_mot):
            lieu_score += 15

        if any(mot in entite.lower() for mot in ORG_KEYWORDS):
            org_score += 3

        if len(mots_ent) >= 2:
            perso_score += 1

        scores = {
            "PERSON": perso_score,
            "LOC": lieu_score,
            "ORG": org_score
        }

        label_final = max(scores, key=scores.get)

        # 🚀 RECLASSIFICATION 1 : Si le modèle a voté ORG mais qu'aucun suffixe corporate n'est là (ex: Caterpillar)
        if label_final == "ORG" and not any(mot in entite.lower() for mot in ORG_KEYWORDS):
            if any(lex in {"noun.person", "noun.animal"} for lex in lexnames) or character_for_sure(dernier_mot):
                label_final = "PERSON"
            elif ressemble_a_un_lieu(dernier_mot) or any(l in TYPE_LIEUX for l in mots_ent_lower):
                label_final = "LOC"
            else:
                label_final = "PERSON"

        # 🚀 RECLASSIFICATION 2 : Si le mot final est sémantiquement un lieu pur et sans titre, bascule en LOC
        if label_final == "PERSON" and (ressemble_a_un_lieu(dernier_mot) or any(l in TYPE_LIEUX for l in mots_ent_lower)):
            if not any(titre in mots_ent_lower for titre in TITRES_PERSONNAGES):
                label_final = "LOC"

        if label_final == "PERSON":
            tt_perso.append(entite)
        elif label_final == "LOC":
            tt_lieux.append(entite)
        else:
            tt_orgs.append(entite)

    # --- ÉTAPE 3 : Nettoyage & Fusion ---
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

    perso_clean = fusionner_variantes(list(dict.fromkeys(perso_harmonises)))
    lieux_clean = fusionner_variantes(list(dict.fromkeys(tt_lieux)))
    lieux_clean = [l.title() if l.isupper() else l for l in lieux_clean]

    print("✅ Extraction terminée !")
    print(f"   - {len(perso_clean)} personnages uniques trouvés.")
    print(f"   - {len(lieux_clean)} lieux uniques trouvés.")

    return {
        "persos": perso_clean,
        "lieux": lieux_clean
    }