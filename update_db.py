#! /usr/bin/env python3
# coding: utf-8

'''This module inserts data from the openfoodfacts api into a database
Don't forget to specify the database URL in a .env file (see README)
Run this module only once, before the first main.py run'''


import requests

import queries

accepted_categories = ["Boissons", "Plats préparés",
                       "Produits laitiers", "Snacks", "Viandes"]

def main():
    '''Requests the open food facts api and unpacks the obtained data
    Each valid product (that is, with existing name, grade and categories)
    is added into the Products Table and linked to Stores and Categories
    using association tables
    Also inserts not-yet-existing store names into the Stores table
    '''

    r = requests.get(
        'https://fr.openfoodfacts.org/cgi/search.pl?search_terms&search_simple=1&json=1')
    products = r.json()["products"]

    for product in products:
        categories = [category.strip() for category
                      in product["categories"].split(",")
                      if category in accepted_categories]
        stores = [store.strip() for store in product['stores'].split(",")]
        if categories and product["product_name"] and product["nutrition_grades"]:
            queries.add_product(
                product["product_name"],
                product["nutrition_grades"],
                product["url"],
                product["generic_name"]
            )

            product_id = queries.get_last_id()[0]["LAST_INSERT_ID()"]

            for store in stores:
                queries.add_store(store)

                store_id = queries.get_id('Stores', store)[0]["id"]
                queries.add_association('Product_Stores', product_id, store_id)

            for category in categories:
                category_id = queries.get_id('Categories', category)[0]["id"]
                queries.add_association(
                    'Product_Categories', product_id, category_id)


if __name__ == "__main__":
    main()
