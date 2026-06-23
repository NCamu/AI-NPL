import os
import csv

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
