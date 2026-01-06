import sqlite3
from werkzeug.security import generate_password_hash
from test_data import products_data # Import the test data


# This script should be run once to set up the database schema and initial data

# Database will be created in the same directory as this script and named 'database.db'
connection = sqlite3.connect('database.db')

# This opens the schema.sql file and executes its contents to create the necessary tables
with open('schema.sql') as f:
    connection.executescript(f.read())

# Create a cursor object to execute SQL commands
cur = connection.cursor()

# Insert initial data into the user table
cur.execute("INSERT INTO users (first_name, last_name, username, email, password, phone , whatsapp, selfie, address, city, postcode) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ('Michael','Odo','admin', 'admin@gmail.com', generate_password_hash('password'), '12345', '+4412345', 'https://r2-us-west.photoai.com/1726204507-41c93c794ee27f57a83004455c8b6482-1.png', '5 Courtleet Way Bulwell', 'Nottingham', 'Ng6 8ff' )
            )

cur.execute("INSERT INTO users (first_name, last_name, username, email, password, phone , whatsapp, selfie, address, city, postcode) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ('Alex','Oluchi','user1', 'user1@gmail.com', generate_password_hash('password'), '12345', '+4412345', 'https://r2-us-west.photoai.com/1726204507-41c93c794ee27f57a83004455c8b6482-1.png', '5 Courtleet Way Bulwell', 'Nottingham', 'Ng6 8ff' )
            )

# Create films based on films_data in test_data.py
for product in products_data:
    cur.execute("INSERT INTO products (user, product_name, product_price, product_category,  product_brand, product_description, product_image, product_gallery1, product_gallery2, product_gallery3 ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (2, product['product_name'], product['product_price'], product['product_category'], product['product_brand'], product['product_description'],  product['product_image'], product['product_gallery1'], product['product_gallery2'], product['product_gallery3'])
                )

# Commit the changes to the database and close the connection
connection.commit()
connection.close()
