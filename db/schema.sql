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
    product_condition TEXT,
    product_description TEXT,
    product_image TEXT,
    product_gallery1 TEXT,
    product_gallery2 TEXT,
    product_gallery3 TEXT
);

CREATE TABLE transactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  vendor_id INTEGER NOT NULL REFERENCES users(id),
  buyer_id INTEGER NOT NULL REFERENCES users(id),
  product_id INTEGER NOT NULL REFERENCES products(id),
  UNIQUE(buyer_id, product_id)
);

CREATE TABLE reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  transaction_id INTEGER NOT NULL UNIQUE REFERENCES transactions(id),
  reviewer_id INTEGER NOT NULL REFERENCES users(id),
  vendor_id INTEGER NOT NULL REFERENCES users(id),
  product_id INTEGER NOT NULL REFERENCES products(id),
  rating INTEGER NOT NULL,
  review_text TEXT NOT NULL,
  sentiment_label TEXT,
  sentiment_score REAL
);
