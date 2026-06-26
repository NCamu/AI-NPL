import os
import csv
import sys

def similar(id: int):  
    with open('pg_catalog.csv', mode='r', encoding='utf-8') as fichier:
        read_csv = list(csv.DictReader(fichier))
        
    book_list = [] 
    info_book = None

    # 1. On cherche le livre cible UNE seule fois
    for ligne in read_csv:
        if ligne['Text#'] == str(id):
            info_book = {
                'id': ligne['Text#'],
                'bookshelves': ligne['Bookshelves'].strip()
            }
            break

    if not info_book:
        print(f"error: no book found with ID#{id}.")
        sys.exit(1)

    # Sécurité : Si le livre n'a aucune étagère
    if not info_book['bookshelves']:
        print(f"Le livre ID#{id} n'a pas d'étagères associées.")
        return []

    # 2. Premier essai : Correspondance exacte des étagères
    for i in read_csv:
        if info_book['bookshelves'] == i['Bookshelves'] and i["Text#"] != info_book["id"]:
            # Uniformisé : on utilise le même format de dictionnaire partout
            book_list.append({'title': i['Title']})

    # 3. Deuxième essai (Secours) : Si aucun match exact n'a été trouvé
    if not book_list:
        # On découpe les étagères du livre cible
        target_shelves = [s.strip().lower() for s in info_book['bookshelves'].split(';') if s.strip()]

        for i in read_csv:
            if i["Text#"] == info_book["id"]:
                continue

            # On découpe les étagères du livre comparé
            current_shelves = [s.strip().lower() for s in i['Bookshelves'].split(';') if s.strip()]

            # Si au moins une étagère correspond
            if any(shelf in target_shelves for shelf in current_shelves):
                book_list.append({'title': i['Title']})
               
    return book_list[:5]