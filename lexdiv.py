import re
from collections import Counter , defaultdict



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

