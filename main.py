#! /usr/bin/env python3
# coding: utf-8

# -tc- actuellement, package absent de github
from local_settings import db_config

# -tc- Pas nécessaire d'importer mysql.connector, car il n'est pas utiliser explicitement dans ce module.
# -tc- Il est utilisé par records, mais on n'a pas besoin de s'en préoccuper.
import mysql.connector
import records
import os




category_data = ["Pizza", "Boissons", "Snacks", "Viandes", "Légumes"]
pizza_data = ["Bolo", "Pesto", "Mozza"]
boissons_data = ["Coca", "Pepsi"]
snacks_data = ["maltesers"]
viandes_data = ["steak", "poulet"]
legumes_data = ["carotte"]

class Menu():

    TITLE = "title"

    def __init__(self):
        self.options = []
        self.display()

    def display(self):
        print(self.TITLE)
        for count, option in enumerate(self.options, 1):
            print(str(count) + " - " + option)
        self.read_input()

    def read_input(self):
        choice = input()
        if int(choice) in range(1, len(self.options) + 1):
            self.proceed(choice)
        else:
            print("Invalid input.")
            # -tc- Ca peut être dangereux d'utiliser la récursivité ici. L'utilisateur peut
            # -tc- volontairement faire planter ton programme en donnant une réponse invalide de manière répétée
            self.display()

    def proceed(self, choice):
        pass


class MainMenu(Menu):

    TITLE = "Menu Principal"

    def __init__(self):
        self.options = ["Trouver un substitut à un aliment",
                        "Retrouver mes aliments substitués"]
        self.display()

    def proceed(self, choice):
        # -tc- Pourquoi deux if? Ces conditions étant mutuellement exclusives: if...elif
        if choice == "1":
            currentMenu = CategoryMenu()
        if choice == "2":
            currentMenu = BookmarkMenu()


class CategoryMenu(Menu):

    TITLE = "Choisissez une catégorie"
    
    def __init__(self):
        self.options = category_data
        self.display()

    def proceed(self, choice):
        currentMenu = FoodMenu(self.options[int(choice) - 1])


# -tc- Dans la mesure du possible, essayer de séparer le code client de l'accès à la base de données
class FoodMenu(Menu):

    def __init__(self, category):
        self.options = [r.name for r in db.query('SELECT Products.name FROM Products INNER JOIN Product_Categories on Products.id = Product_Categories.product_id INNER JOIN Categories on Product_Categories.category_id = Categories.id WHERE Categories.name = \'{}\''.format(category))]
        FoodMenu.TITLE = category
        self.display()

    def proceed(self, choice):
        currentMenu = FoodMenu(self.options[int(choice) - 1])


class FoodDetail(Menu):
    def __init__(self, food_name):
        self.options = ["Enregistrer l'aliment et son substitut",
                        "Quitter l'application"]
        FoodDetail.TITLE = food_name
        self.display()

    def display(self):
        print(self.TITLE)
        print(db.query('SELECT name, grade, link, description FROM Products WHERE name = \'{}\' '.format(self.TITLE))[0])
        for pair in db.query('SELECT name, grade, link, description FROM Products WHERE name = \'{}\' '.format(self.TITLE))[0]:
            print("{} : {}".format(pair[0], pair[1]))
        for count, option in enumerate(self.options, 1):
            print(str(count) + " - " + option)
        self.read_input()

    def proceed(self, choice):
        if choice == "1":
            print("Aliment et substitut enregistrés")
        if choice == "2":
            pass


class BookmarkMenu(Menu):
    def __init__(self):
        self.options = ["Bookmark placeholder"]
        self.display()

if __name__ == "__main__":
    db = records.Database(os.environ.get('DB_CREDENTIALS'))
    category_data = [r.name for r in db.query('SELECT name FROM Categories')]
    currentMenu = MainMenu()
