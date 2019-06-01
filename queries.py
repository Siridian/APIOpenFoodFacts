import os

import requests
import records

DB = records.Database(os.environ.get('DB_CREDENTIALS'))


### update_db.py ###

def get_id(table, name):
    if table == "Stores":
        return DB.query('''SELECT id FROM Stores
                           WHERE name = :name
                        ''',
                        name=name
                       )
    elif table == "Categories":
        return DB.query('''SELECT id FROM Categories
                           WHERE name = :name
                        ''',
                        name=name
                       )

def get_last_id():
    return DB.query('SELECT LAST_INSERT_ID()')


def add_product(name, grade, link, description):
    return DB.query('''INSERT INTO Products (name, grade, link, description) 
                       VALUES (:name, :grade, :link, :description)
                    ''',
                    name=name,
                    grade=grade,
                    link=link,
                    description=description
                   )

def add_store(name):
    return DB.query('''INSERT IGNORE INTO Stores (name) 
                       VALUES (:name)
                    ''',
                    name=name
                   )

def add_association(table, product_id, other_id):
    if table == "Product_Stores":      
        return DB.query('''INSERT IGNORE INTO Product_Stores
                           VALUES (:p_id, :o_id)
                        ''',
                        p_id=product_id,
                        o_id=other_id
                       )
                       
    elif table == "Product_Categories":        
        return DB.query('''INSERT IGNORE INTO Product_Categories
                           VALUES (:p_id, :o_id)
                        ''',
                        p_id=product_id,
                        o_id=other_id
                       )


### main.py ###

def get_categories():
    return DB.query('SELECT name FROM Categories')

def get_products_in_category(category):    
    return DB.query('''SELECT Products.id, Products.name
                       FROM Products 
                       INNER JOIN Product_Categories on Products.id = Product_Categories.product_id 
                       INNER JOIN Categories on Product_Categories.category_id = Categories.id 
                       WHERE Categories.name = :category
                    ''',
                    category=category
                   )


def get_product_details(id):
    return DB.query('''SELECT Products.id, Products.name, Products.grade, Products.link, Products.description, Stores.name as store_name 
                       FROM Products 
                       LEFT JOIN Product_Stores on Products.id = Product_Stores.product_id 
                       INNER JOIN Stores on Product_Stores.store_id = Stores.id 
                       WHERE Products.id = :id
                    ''',
                    id=id
                   )


def get_matching_product(grade, id):
    return DB.query('''SELECT Products.id, Products.name, Products.grade, Products.link, Products.description, Stores.name as store_name
                       FROM Products 
                       LEFT JOIN Product_Stores on Products.id = Product_Stores.product_id 
                       INNER JOIN Stores on Product_Stores.store_id = Stores.id 
                       INNER JOIN Product_Categories on Products.id = Product_Categories.product_id
                       WHERE Products.grade < :grade 
                       AND Product_Categories.category_id IN (
                            SELECT category_id
                            FROM Product_Categories
                            WHERE product_id = :id
                       )
                       LIMIT 1
                    ''',
                    grade=grade,
                    id=id
                   )

def add_bookmark(base_id, substitute_id):
    return DB.query('INSERT IGNORE INTO Bookmarks VALUES (:base_id, :substitute_id)',
            base_id=base_id,
            substitute_id=substitute_id)

def get_bookmarks():
    return DB.query('''SELECT bp.id as base_id, bp.name as base_name, sp.id as substitute_id, sp.name as substitute_name
                       FROM Products as bp
                       INNER JOIN Bookmarks on bp.id = Bookmarks.product_id
                       INNER JOIN Products as sp on Bookmarks.substitute_id = sp.id
                    ''')

def remove_bookmark(base_id, substitute_id):
    return DB.query('''DELETE FROM Bookmarks 
                       WHERE product_id = :base_id 
                       AND substitute_id = :substitute_id
                    ''',
                    base_id=base_id,
                    substitute_id=substitute_id
                   )