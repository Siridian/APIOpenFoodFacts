#! /usr/bin/env python3
# coding: utf-8

import re
import os

from local_settings import db_config

import requests
import json
import mysql.connector
import records

accepted_categories = ["Boissons", "Plats préparés", "Produits laitiers", "Snacks", "Viandes"]



def update_db():
    r = requests.get('https://fr.openfoodfacts.org/cgi/search.pl?search_terms=pizza&nutrition_grades=a&search_simple=1&json=1')
    products = r.json()["products"]
    db = records.Database(os.environ.get(DB_CREDENTIALS))
    

    add_product = ('INSERT INTO Products'
                   '(name, grade, link, description)'
                   'VALUES (%(product_name)s,  %(nutrition_grades)s, %(url)s, %(generic_name)s)')

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
            db.query('INSERT INTO Products (name, grade, link, description) VALUES (\'{}\', \'{}\', \'{}\', \'{}\')'.format(product["product_name"], product["nutrition_grades"], product["url"], product["generic_name"]))
            
            
            product_id = (db.query('SELECT LAST_INSERT_ID()')[0]["LAST_INSERT_ID()"])

            
            for store in stores:
                db.query('INSERT INTO Stores (name) VALUES (\'{}\') ON DUPLICATE KEY UPDATE name = \'{}\''.format(store, store))
                
                store_id = (db.query('SELECT LAST_INSERT_ID()')[0]["LAST_INSERT_ID()"])
                db.query('INSERT INTO Product_Stores VALUES ({}, {})'.format(product_id, store_id))
            
            
            for category in categories:
                category_id = db.query('SELECT id FROM Categories WHERE name = \'{}\''.format(category))[0]["id"]
                db.query('INSERT INTO Product_Categories VALUES ({}, {})'.format(product_id, category_id))

                
    

def main():
    update_db()




if __name__ == "__main__":
    main()