import os
import csv

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
