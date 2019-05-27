#! /usr/bin/env python3
# coding: utf-8

import re
import os

from local_settings import db_config

import requests
import json
# -tc- Si tu utilises records, l'import de mysql.connector est inutile. Records l'utilise en interne
import mysql.connector
import records

accepted_categories = ["Boissons", "Plats préparés", "Produits laitiers", "Snacks", "Viandes"]



def update_db():
    # -tc- de manière plus lisible, j'écrirais:
    # params = {
    #     "action": "process",
    #     "tagtype_0": "categories",
    #     "tag_contains_0": "contains",
    #     "tag_0": category,
    #     "json": 1,
    #     "page_size": 1000
    # }
    # r = requests.get('https://fr.openfoodfacts.org/cgi/search.pl', params=params)
    #
    # Pourquoi se contenter de une seule catégorie et de un seul nutriscore? Nous ne sommes pas obligé d'avoir que des A
    r = requests.get('https://fr.openfoodfacts.org/cgi/search.pl?search_terms=pizza&nutrition_grades=a&search_simple=1&json=1')
    products = r.json()["products"]
    db = records.Database(os.environ.get(DB_CREDENTIALS))
    
    
    # -tc- Personnellement, je séparerais interaction avec l'API avec gestion des produits en base dans des classes séparées

    # -tc- Pour écrire des requêtes sur plusieurs lignes, on peut utiliser des triples guillemets ou triples apostrophes
    add_product = ('INSERT INTO Products'
                   '(name, grade, link, description)'
                   # -tc- records utilisera 'VALUES (:product_name,  :nutrition_grades, :url, :generic_name)'
                   'VALUES (%(product_name)s,  %(nutrition_grades)s, %(url)s, %(generic_name)s)')

    # -tc- INSERT IGNORE fonctionne avec records
    add_store = ('INSERT INTO Stores'
                  '(name)'
                  'VALUES (%(name)s)'
                  'ON DUPLICATE KEY UPDATE name = %(name)s')

    add_pro_sto = ('INSERT INTO Product_Stores'
                    'VALUES (%(idp)s, %(ids)s)')

    add_pro_cat = ('INSERT INTO Product_Categories'
                    'VALUES (%s, %s)')

    get_store_id = ('SELECT id FROM Stores'
                    'WHERE name = \'%(name)s\'')

    get_category_id = ('SELECT id FROM Categories'
                       'WHERE name = %s')

    for product in products:
        categories = [category for category in product["categories"].split(", ") if category in accepted_categories]
        stores = [store for store in product["stores"].split(", ")]
        if categories and product["product_name"] and product["nutrition_grades"]:
            product_stats = {
            "product_name": product["product_name"],
            "nutrition_grades": product["nutrition_grades"],
            "url": product["url"],
            "generic_name": product["generic_name"]
            }
            # -tc- Ne jamais utiliser de format pour faire de l'insertion, risques d'injections sql, 
            # -tc- Records fournit un mécanisme pour l'éviter
            # db.query(
            #     """INSERT INTO Products (name, grade, link, description) 
            #        VALUES (:product_name, :nutrition_grades, :url, :description
            #     """, 
            #     product_name=product["product_name"], 
            #     nutrition_grades=product["nutrition_grades"], 
            #     product["url"], 
            #     description=product["generic_name"])
            #  )
            db.query('INSERT INTO Products (name, grade, link, description) VALUES (\'{}\', \'{}\', \'{}\', \'{}\')'.format(product["product_name"], product["nutrition_grades"], product["url"], product["generic_name"]))
            
            
            product_id = (db.query('SELECT LAST_INSERT_ID()')[0]["LAST_INSERT_ID()"])

            
            for store in stores:
                # -tc- Idem que plus haut, éviter format
                db.query('INSERT INTO Stores (name) VALUES (\'{}\') ON DUPLICATE KEY UPDATE name = \'{}\''.format(store, store))
                
                store_id = (db.query('SELECT LAST_INSERT_ID()')[0]["LAST_INSERT_ID()"])
                # -tc- Idem que plus haut, éviter format
                db.query('INSERT INTO Product_Stores VALUES ({}, {})'.format(product_id, store_id))
            
            
            for category in categories:
                # -tc- Idem que plus haut, éviter format
                category_id = db.query('SELECT id FROM Categories WHERE name = \'{}\''.format(category))[0]["id"]
                db.query('INSERT INTO Product_Categories VALUES ({}, {})'.format(product_id, category_id))

                
    

def main():
    update_db()


    

if __name__ == "__main__":
    main()
