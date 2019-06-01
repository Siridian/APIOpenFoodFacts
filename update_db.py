#! /usr/bin/env python3
# coding: utf-8

import os
import json

import requests
import records

import queries

accepted_categories = ["Boissons", "Plats préparés", "Produits laitiers", "Snacks", "Viandes"]



def update_db():
    r = requests.get('https://fr.openfoodfacts.org/cgi/search.pl?search_terms&search_simple=1&json=1')
    products = r.json()["products"]
    db = records.Database(os.environ.get('DB_CREDENTIALS'))    

    for product in products:
        categories = [category.strip() for category in product["categories"].split(",") if category in accepted_categories]
        stores = [store.strip() for store in product['stores'].split(",")]
        if categories and product["product_name"] and product["nutrition_grades"]:
            queries.add_product(product["product_name"], product["nutrition_grades"], product["url"], product["generic_name"])
            
            
            product_id = queries.get_last_id()[0]["LAST_INSERT_ID()"]

            
            for store in stores:
                queries.add_store(store)
                
                store_id = queries.get_id('Stores', store)[0]["id"]
                queries.add_association('Product_Stores', product_id, store_id)
            
            
            for category in categories:
                category_id = queries.get_id('Categories', category)[0]["id"]
                queries.add_association('Product_Categories', product_id, category_id)

def main():
    update_db()


if __name__ == "__main__":
    main()