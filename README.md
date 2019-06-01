=== OPENFOODFACTS BROWSER ===

Project version : 1.0 (01/06/2019)

Endless hours of pythonic fun brought to you by V.S. Studios !



*** Installation ***

This project uses pipenv ; everything you need is within the root folder

Simply run 'pipenv install' in the root folder to install all dependencies



*** Configuration ***

First, create a .env file in the root folder, then set a DB_CREDENTIALS variable to connect to a database of your own.
DB_CREDENTIALS must follow this pattern : mysql+mysqlconnector://user:password@host:port/dbname

Then download the required data using 'pipenv run python update_db.py'. You need to do this only once !


*** Launch ***

Simply run the main script using 'pipenv run python main.py'



*** How to use ***

The application lets you browse through five categories of food products. 

Chose one specific product among your chosen category, and get detailed informations on a healthier substitute of the same category !

You may then bookmark the result to easily find them again later.

Bookmarked substitutes are saved in the database ; you may access them at any time through the main menu.