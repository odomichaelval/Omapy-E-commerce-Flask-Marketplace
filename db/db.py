import sqlite3
import os
from flask import abort
from werkzeug.security import check_password_hash, generate_password_hash

# This defines which functions are available for import when using 'from db.db import *'
__all__ = [
    "create_user",
    "validate_login",
    "get_user_by_username",
    "get_user_by_id",
    "get_all_products",
    "get_products_by_user",
    "get_product_by_id",
    "get_related_products",
    "create_product",
    "update_product",
    "delete_product",
    "get_categories_with_count",
    "get_products_by_category",
    "search_products",
    "search_users_by_username_prefix",
    "create_transaction",
    "get_transactions_by_product",
    "get_unreviewed_transaction",
    "create_review",
    "get_reviews_by_product",
    "get_reviews_by_product",
    "get_vendor_trust_score"
   
]

# Establish connection to the SQLite database
def get_db_connection():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current file
    DB_PATH = os.path.join(BASE_DIR, 'database.db') # Construct the full path to the database file
    conn = sqlite3.connect(DB_PATH)                 # Connect to the database
    conn.row_factory = sqlite3.Row                  # Enable dictionary-like access to rows
    return conn

#adnin function


# Authentication functions
# =========================================================
# Insert a new user (Register)
def create_user(first_name, last_name, username, email, password, phone , whatsapp, selfie, address, city, postcode):
    hashed_password = generate_password_hash(password)
    conn = get_db_connection()
    conn.execute('INSERT INTO users  (first_name, last_name, username, email, password, phone , whatsapp, selfie, address, city, postcode) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', ( first_name, last_name, username, email, hashed_password, phone , whatsapp, selfie, address, city, postcode))
    conn.commit()
    conn.close()

# Validate user exists with password (Login)
def validate_login(username, password):
    user = get_user_by_username(username)
    if user and check_password_hash(user['password'], password):
        return user
    return None

# Check if a user exists
def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user


# Get user by ID
def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user is None:
        abort(404)
    return user




# Product Display functions
# =========================================================
# Get all products (or filter by user)
def get_all_products(limit=None, order_by='created DESC'):
    conn = get_db_connection()

    query = f"""
        SELECT products.*,
               products.user AS vendor_username
        FROM products
        ORDER BY {order_by}
    """

    if limit:
        query += " LIMIT ?"
        products = conn.execute(query, (limit,)).fetchall()
    else:
        products = conn.execute(query).fetchall()

    conn.close()
    return products



# Get all products (or filter by user)
def get_products_by_user(user=None, limit=None, order_by='product_name ASC'):
    conn = get_db_connection()
    # Construct base query
    query = 'SELECT * FROM products'
    # If user is specified, filter films by that user
    if user:
        query += ' WHERE user = ?'
    # Add ORDER BY to the query if specified
    query += f' ORDER BY {order_by}'
    # Add LIMIT if specified
    if limit:
        query += f' LIMIT {limit}'

    # Execute the query
    if user:
        products = conn.execute(query, (user,)).fetchall()
    else:
        products = conn.execute(query).fetchall()

    conn.close()
    
    return products


# Get a product by its ID
def get_product_by_id(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    return product

# Get related products by category (exclude current product)
def get_related_products(category, current_product_id, limit=6):
    conn = get_db_connection()
    products = conn.execute(
        '''
        SELECT * FROM products
        WHERE product_category = ?
        AND id != ?
        LIMIT ?
        ''',
        (category, current_product_id, limit)
    ).fetchall()
    conn.close()
    return products

# Create a new product
def create_product(user_id, product_name, product_price, product_category, product_condition, product_description, product_image, product_gallery1, product_gallery2, product_gallery3):
    conn = get_db_connection()
    conn.execute("INSERT INTO products (user, product_name, product_price, product_category,  product_condition, product_description, product_image, product_gallery1, product_gallery2, product_gallery3 ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (user_id, product_name, product_price, product_category, product_condition, product_description, product_image, product_gallery1, product_gallery2, product_gallery3)
                )
    conn.commit()

# Update a product by its ID
def update_product(product_id, product_name, product_price, product_category, product_condition, product_description, product_image, product_gallery1, product_gallery2, product_gallery3):
    conn = get_db_connection()
    conn.execute('UPDATE products SET product_name = ?, product_price = ?, product_category = ?, product_condition = ?, product_description = ?, product_image = ?, product_gallery1 = ?, product_gallery2 = ?, product_gallery3 = ? WHERE id = ?',
                 (product_name, product_price, product_category, product_condition, product_description, product_image, product_gallery1, product_gallery2, product_gallery3,product_id))
    conn.commit()
    conn.close()

# Delete a film by its ID
def delete_product(product_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()

# fetch and count catgories
def get_categories_with_count():
    conn = get_db_connection()
    categories = conn.execute("""
        SELECT product_category, COUNT(*) as total
        FROM products
        GROUP BY product_category
        ORDER BY product_category ASC
    """).fetchall()
    conn.close()
    return categories


# fetch product category
def get_products_by_category(category, limit=None, order_by='created DESC'):
    conn = get_db_connection()

    query = '''
        SELECT *
        FROM products
        WHERE product_category = ?
        ORDER BY {}
    '''.format(order_by)

    if limit:
        query += ' LIMIT ?'
        products = conn.execute(query, (category, limit)).fetchall()
    else:
        products = conn.execute(query, (category,)).fetchall()

    conn.close()
    return products

#search for product
def search_products(keyword):
    conn = get_db_connection()
    products = conn.execute("""
        SELECT *
        FROM products
        WHERE product_name LIKE ?
        ORDER BY created DESC
    """, (f"%{keyword}%",)).fetchall()
    conn.close()
    return products

# Reviews & Transactions functions
# =========================================================

# Live username search for the "Confirm Sale" buyer picker
def search_users_by_username_prefix(prefix, exclude_user_id=None, limit=8):
    conn = get_db_connection()
    if exclude_user_id:
        rows = conn.execute(
            "SELECT id, username FROM users WHERE username LIKE ? AND id != ? ORDER BY username LIMIT ?",
            (f"{prefix}%", exclude_user_id, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, username FROM users WHERE username LIKE ? ORDER BY username LIMIT ?",
            (f"{prefix}%", limit)
        ).fetchall()
    conn.close()
    return rows


# Vendor confirms a sale to a specific buyer for a specific product
def create_transaction(vendor_id, buyer_id, product_id):
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO transactions (vendor_id, buyer_id, product_id) VALUES (?, ?, ?)",
            (vendor_id, buyer_id, product_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # this buyer was already confirmed for this product
    finally:
        conn.close()


# All confirmed buyers for a product - vendor-only display ("Sold to: ...")
def get_transactions_by_product(product_id):
    conn = get_db_connection()
    rows = conn.execute(
        """SELECT transactions.*, users.username AS buyer_username
           FROM transactions JOIN users ON transactions.buyer_id = users.id
           WHERE product_id = ?
           ORDER BY transactions.created DESC""",
        (product_id,)
    ).fetchall()
    conn.close()
    return rows


# Checks if this user has a confirmed, not-yet-reviewed purchase of this
# product - determines whether the "Leave a Review" option should show
def get_unreviewed_transaction(buyer_id, product_id):
    conn = get_db_connection()
    row = conn.execute(
        """SELECT transactions.* FROM transactions
           LEFT JOIN reviews ON reviews.transaction_id = transactions.id
           WHERE transactions.buyer_id = ? AND transactions.product_id = ?
           AND reviews.id IS NULL
           LIMIT 1""",
        (buyer_id, product_id)
    ).fetchone()
    conn.close()
    return row


def create_review(transaction_id, reviewer_id, vendor_id, product_id, rating, review_text, sentiment_label, sentiment_score):
    conn = get_db_connection()
    conn.execute(
        """INSERT INTO reviews
           (transaction_id, reviewer_id, vendor_id, product_id, rating, review_text, sentiment_label, sentiment_score)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (transaction_id, reviewer_id, vendor_id, product_id, rating, review_text, sentiment_label, sentiment_score)
    )
    conn.commit()
    conn.close()


# Public - visible to everyone, registered or not
def get_reviews_by_product(product_id):
    conn = get_db_connection()
    rows = conn.execute(
        """SELECT reviews.*, users.username AS reviewer_username
           FROM reviews JOIN users ON reviews.reviewer_id = users.id
           WHERE reviews.product_id = ?
           ORDER BY reviews.created DESC""",
        (product_id,)
    ).fetchall()
    conn.close()
    return rows

# Aggregates a vendor's reviews into a trust score summary.
# Pure aggregation of data already stored - no new AI model runs here,
# it just summarises sentiment/rating values VADER already produced
# per review at submission time.
def get_vendor_trust_score(vendor_id):
    conn = get_db_connection()

    rows = conn.execute(
        "SELECT rating, sentiment_label FROM reviews WHERE vendor_id = ?",
        (vendor_id,)
    ).fetchall()
    conn.close()

    total = len(rows)
    if total == 0:
        return {
            "total_reviews": 0,
            "average_rating": None,
            "positive_pct": 0,
            "neutral_pct": 0,
            "negative_pct": 0,
        }

    avg_rating = sum(r['rating'] for r in rows) / total

    positive_count = sum(1 for r in rows if r['sentiment_label'] == 'Positive')
    neutral_count = sum(1 for r in rows if r['sentiment_label'] == 'Neutral')
    negative_count = sum(1 for r in rows if r['sentiment_label'] == 'Negative')

    return {
        "total_reviews": total,
        "average_rating": round(avg_rating, 1),
        "positive_pct": round((positive_count / total) * 100),
        "neutral_pct": round((neutral_count / total) * 100),
        "negative_pct": round((negative_count / total) * 100),
    }






