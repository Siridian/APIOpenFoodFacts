#! /usr/bin/env python3
# coding: utf-8

import queries

import requests
import records
import os




class Menu():

    def __init__(self):       
        self.title = "title"
        self.options = []
        self.display()

    def display(self):
        print(self.title)
        for count, option in enumerate(self.options, 1):
            print(str(count) + " - " + option)
        self.read_input()

    def read_input(self):
        choice = input()
        if int(choice) in range(1, len(self.options) + 1):
            self.proceed(choice)
        else:
            print("Invalid input.")
            self.display()

    def proceed(self, choice):
        pass

    def describe_product(self, info):
        print("Nom du produit : " + info['name'])
        print("Score nutritionnel : " + info['grade'].upper())
        if info['link'] : print("Lien vers le site : " + info['link'])
        if info['description'] : print("Description : " + info['description'])
        if info['store_name'] : print("Enseigne(s) proposant ce produit : " + info[('store_name')])
        print('\n')


class MainMenu(Menu):

    def __init__(self):
        self.title = "Menu Principal"
        self.options = ["Trouver un substitut à un aliment",
                        "Retrouver mes aliments substitués"]
        self.display()

    def proceed(self, choice):
        if choice == "1":
            currentMenu = CategoryMenu()
        elif choice == "2":
            currentMenu = BookmarkMenu()


class CategoryMenu(Menu):
    
    def __init__(self):
        self.title = "Choisissez une catégorie"
        self.options = category_data
        self.display()

    def proceed(self, choice):
        currentMenu = FoodMenu(self.options[int(choice) - 1])


class FoodMenu(Menu):

    def __init__(self, category):
        data = queries.get_products_in_category(category)
        self.options = [r.name for r in data]
        self.ids = [r.id for r in data]
        self.title = category
        self.display()

    def proceed(self, choice):
        currentMenu = FoodDetail(self.ids[int(choice) - 1])


class FoodDetail(Menu):
    def __init__(self, food_id):
        self.options = ["Enregistrer l'aliment et son substitut",
                        "Quitter l'application"]
        self.ids = []
        self.display(food_id)

    def display(self, food_id):
        print('\n ### Produit sélectionné ### \n')
        base_info = queries.get_product_details(food_id)[0]
        self.describe_product(base_info)
        try:
            print('### Substitut proposé ### \n')
            substitute_info = queries.get_matching_product(base_info['grade'], base_info['id'])[0]
            self.describe_product(substitute_info)     
            for count, option in enumerate(self.options, 1):
                print(str(count) + " - " + option)
            self.ids = [base_info['id'], substitute_info['id']]
            self.read_input()
        except IndexError:
            print('Aucun substitut plus sain n\'a été trouvé dans la base de données')

    def proceed(self, choice):
        if choice == "1":
            queries.add_bookmark(*self.ids)
        elif choice == "2":
            pass


class BookmarkMenu(Menu):
    def __init__(self):
        bookmarks = queries.get_bookmarks()
        self.options = ["{} => {}".format(bookmark.base_name, bookmark.substitute_name) for bookmark in bookmarks] 
        self.ids = [(bookmark.base_id, bookmark.substitute_id) for bookmark in bookmarks]
        self.title = 'Substituts enregistrés'
        self.display()

    def display(self):
        if not self.options:
            print("Aucun substitut n'est inscrit dans la base de données")
        else:
            super().display()

    def proceed(self, choice):
        currentMenu = BookmarkDetail(self.ids[int(choice) - 1], self.options[int(choice) - 1])

class BookmarkDetail(Menu):
    def __init__(self, bookmark_ids, bookmark_names):
        self.options = ["Retour aux substituts",
                        "Effacer ce substitut",
                        "Quitter l'application"]
        self.title = '{} => {}'.format(bookmark_names[0], bookmark_names[1])
        self.bookmark_ids = bookmark_ids
        self.display()

    def display(self):
        print(self.title)

        base_info = queries.get_product_details(self.bookmark_ids[0])[0]
        self.describe_product(base_info)

        substitute_info = queries.get_product_details(self.bookmark_ids[1])[0]
        self.describe_product(substitute_info)

        for count, option in enumerate(self.options, 1):
            print(str(count) + " - " + option)

        self.read_input()               

    def proceed(self, choice):
        if choice == "1":
            currentMenu = BookmarkMenu()
        elif choice == "2":
            queries.remove_bookmark(*self.bookmark_ids)
            currentMenu = BookmarkMenu()
        elif choice == "3":
            pass

if __name__ == "__main__":
    category_data = [r.name for r in queries.get_categories()]
    currentMenu = MainMenu()