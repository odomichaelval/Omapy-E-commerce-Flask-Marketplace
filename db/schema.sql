DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS products;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  username TEXT UNIQUE NOT NULL,
  email TEXT NOT NULL,
  password TEXT NOT NULL,
  phone TEXT,
  whatsapp TEXT,
  selfie TEXT,
  address TEXT,
  city TEXT,
  postcode TEXT

  
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user INTEGER NOT NULL REFERENCES users(id),
    product_name TEXT NOT NULL,
    product_price INTEGER NOT NULL,
    product_category TEXT,
    product_brand TEXT,
    product_description TEXT,
    product_image TEXT,
    product_gallery1 TEXT,
    product_gallery2 TEXT,
    product_gallery3 TEXT
);
