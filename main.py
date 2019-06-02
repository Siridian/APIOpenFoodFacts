#! /usr/bin/env python3
# coding: utf-8


'''This is the main module. Run this to browse through your database using
numerical keys. Make sure to run update_db before the first use of this
module, otherwise your database willbe empty !
'''

import queries


class Menu():
    '''The Menu class is never instatiated. It serves as a template for all the
    other classes, which represents actual menus used throughout the script
    '''

    def __init__(self):
        '''Constructor initalizes title, options, then calls display method'''

        self.title = "title"
        self.options = []
        self.display()

    def display(self):
        '''Display method prints title, options, then calls read_input method'''

        print(self.title)
        for count, option in enumerate(self.options, 1):
            print(str(count) + " - " + option)
        self.read_input()

    def read_input(self):
        '''read_input method uses the user's input to call proceed method'''

        choice = input()
        if int(choice) in range(1, len(self.options) + 1):
            self.proceed(choice)
        else:
            print("Invalid input.")
            self.display()

    def proceed(self, choice):
        '''proceed method processes user's input and act upon it
        usually by redirecting the user to the next menu'''

        pass

    def describe_product(self, info):
        '''describe_product is called by the display method of some menus
        it displays detailed informations on a given product'''

        print("Nom du produit : " + info['name'])
        print("Score nutritionnel : " + info['grade'].upper())
        if info['link']:
            print("Lien vers le site : " + info['link'])
        if info['description']:
            print("Description : " + info['description'])
        if info['store_name']:
            print("Enseigne(s) proposant ce produit : " + info[('store_name')])
        print('\n')


class MainMenu(Menu):
    '''The Main Menu is the first menu encountered by the user
    It redirects the latter to either the Category Menu for a query
    or to the Bookmark Menu to find a bookmarked substitute'''

    def __init__(self):
        '''Constructor initalizes title, options, then calls display method'''

        self.title = "Menu Principal"
        self.options = ["Trouver un substitut à un aliment",
                        "Retrouver mes aliments substitués"]
        self.display()

    def proceed(self, choice):
        '''The proceed method of the Main Menu redirects the user to the chosen menu'''
        if choice == "1":
            currentMenu = CategoryMenu()
        elif choice == "2":
            currentMenu = BookmarkMenu()


class CategoryMenu(Menu):
    '''The Category Menu allows the user the chose which category of food
    products to look into to find a subsitute'''

    def __init__(self):
        '''Constructor initalizes title, options, then calls display method'''

        self.title = "Choisissez une catégorie"
        self.options = category_data
        self.display()

    def proceed(self, choice):
        '''The proceed method of the category Menu redirects the user to the
        list of the food products found in the chosen category'''

        currentMenu = FoodMenu(self.options[int(choice) - 1])


class FoodMenu(Menu):
    '''The Food Menu displays the existing food products belonging to the
    previously chosen category'''

    def __init__(self, category):
        '''Constructor initalizes title, options, then calls display method'''

        self.data = queries.get_products_in_category(category)
        self.options = [r.name for r in self.data]
        self.ids = [r.id for r in self.data]
        self.title = category
        if self.data:
            self.display()
        else:
            print("Aucun aliment n'appartenant à cette catégorie n'a été trouvé")

    def proceed(self, choice):
        '''The proceed method of the food menu redirects the user to the
        details of the chosen product'''
        currentMenu = FoodDetail(self.ids[int(choice) - 1])


class FoodDetail(Menu):
    '''The food detail Menu displays detailed information on a chosen product,
    as well as that of a substitute of that product'''

    def __init__(self, food_id):
        '''Constructor initalizes title, options, then calls display method'''

        self.options = ["Enregistrer l'aliment et son substitut",
                        "Quitter l'application"]
        self.ids = []
        self.display(food_id)

    def display(self, food_id):
        '''Display method prints title, options, then calls read_input method
        In Food Detail Menu, it also gives information about a product and
        its substitute using describe_product()'''

        print('\n ### Produit sélectionné ### \n')
        base_info = queries.get_product_details(food_id)[0]
        self.describe_product(base_info)
        try:
            print('### Substitut proposé ### \n')
            substitute_info = queries.get_matching_product(
                base_info['grade'], base_info['id'])[0]
            self.describe_product(substitute_info)
            for count, option in enumerate(self.options, 1):
                print(str(count) + " - " + option)
            self.ids = [base_info['id'], substitute_info['id']]
            self.read_input()
        except IndexError:
            print('Aucun substitut plus sain n\'a été trouvé dans la base de données')

    def proceed(self, choice):
        '''The proceed method of the Food detail menu allows the user to 
        bookmark the product and its substitute before exiting the app'''

        if choice == "1":
            queries.add_bookmark(*self.ids)
        elif choice == "2":
            pass


class BookmarkMenu(Menu):
    '''The Bookmark Menu displays every bookmarked substitute saved thus far'''

    def __init__(self):
        '''Constructor initalizes title, options, then calls display method'''

        bookmarks = queries.get_bookmarks()
        self.options = ["{} => {}".format(
            bookmark.base_name, bookmark.substitute_name) for bookmark in bookmarks]
        self.ids = [(bookmark.base_id, bookmark.substitute_id)
                    for bookmark in bookmarks]
        self.title = 'Substituts enregistrés'
        self.display()

    def display(self):
        '''Display method prints title, options, then calls read_input method'''

        if not self.options:
            print("Aucun substitut n'est inscrit dans la base de données")
        else:
            super().display()

    def proceed(self, choice):
        '''The proceed method redirects the user to the details of a chosen
        bookmark'''

        currentMenu = BookmarkDetail(
            self.ids[int(choice) - 1], self.options[int(choice) - 1])


class BookmarkDetail(Menu):
    '''The Bookmark detail displays informations about the bookmarked
    product and substitute'''

    def __init__(self, bookmark_ids, bookmark_names):
        '''Constructor initalizes title, options, then calls display method'''

        self.options = ["Retour aux substituts",
                        "Effacer ce substitut",
                        "Quitter l'application"]
        self.title = '{} => {}'.format(bookmark_names[0], bookmark_names[1])
        self.bookmark_ids = bookmark_ids
        self.display()

    def display(self):
        '''Display method prints title, options, then calls read_input method
        In Bookmark Detail, it also gives information about a product and
        its substitute using describe_product()'''

        print(self.title)

        base_info = queries.get_product_details(self.bookmark_ids[0])[0]
        self.describe_product(base_info)

        substitute_info = queries.get_product_details(self.bookmark_ids[1])[0]
        self.describe_product(substitute_info)

        for count, option in enumerate(self.options, 1):
            print(str(count) + " - " + option)

        self.read_input()

    def proceed(self, choice):
        '''The proceed method of the bookmark detail allows the user to either
        return to the bookmark menu, delete the current bookmark, or simply
        leave the app'''

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