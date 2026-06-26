import os
import sys
import spacy
import pytextrank
import re

def summary(id: int) -> str:
    # 1. Charger le modèle de langue français
    try:
        nlp = spacy.load("en_core_web_trf")
    except OSError:
        return "Erreur spacy"
    
    nlp.max_length = 2000000
    # 2. Ajouter TextRank au pipeline de traitement de spaCy
    if "textrank" not in nlp.pipe_names:
        nlp.add_pipe("textrank")
    
    # Vérification que le fichier existe avant de tenter de l'ouvrir
    nom_fichier = f"{id}_sent_tok.txt"
    if not os.path.exists(nom_fichier):
        return f"Erreur : Le fichier '{nom_fichier}' est introuvable."
    # Lecture du texte tokenisé
    with open(nom_fichier, "r", encoding="utf-8") as f:
        text = f.read()

    text = re.sub(r', \.', ', ', text)  # Si c'était un artefact de split

    text = text.replace(',.', ', ')

    # 2. On corrige le vilain 'MDOT' pour redonner son nom au Capitaine des Mousquetaires
    text = text.replace('MDOT', 'M.')

    # 3. Sécurité pour le split : on s'assure que la ponctuation est décollée des mots
    # (Optionnel mais recommandé pour le .split() basique si tu n'utilises pas le tokenizer de spacy)
    text = re.sub(r'([.,!?;:])', r' \1 ', text)    
    print("######## FILE LOADED ########")
    # 3. Analyser le texte
    doc = nlp(text)
    
    phrases_importantes = list(doc._.textrank.summary(limit_phrases=25, limit_sentences=5))
    
    # 2. LES TRIER selon leur ordre d'apparition original dans le document
    # (On utilise l'index de départ de la phrase dans le document : sent.start)
    phrases_triees = sorted(phrases_importantes, key=lambda sent: sent.start)
    
    # 3. Recomposer le résumé proprement
    phrases_resume = [str(sent).strip() for sent in phrases_triees]
    
    return "\n\n".join(phrases_resume)

