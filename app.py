# This code imports the Flask library and some functions from it.
from flask import Flask, render_template, url_for, request, flash, redirect, session
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf


from db.db import *

# Create a Flask application instance
app = Flask(__name__)
# Allowed image extensions for uploads
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
UPLOADS_PATH = "."

app.secret_key = 'your_secret_key'  # Required for CSRF protection
csrf = CSRFProtect(app)  # This automatically protects all POST routes
# Create the csrf_token global variable
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf())


# Global variable for site name: Used in templates to display the site name
siteName = "Omapy E-commerce Project"
# Set the site name in the app context
@app.context_processor
def inject_site_name():
    return dict(siteName=siteName)

#Automatically injects username and user_id into ALL templates Uses "Shopper" as fallback
#No duplication
@app.context_processor
def inject_user():
    return {
        "username": session.get("username", "Shopper"),
        "user_id": session.get("user_id")
    }

def is_admin():
    return session.get('user_id') == 8

@app.context_processor
def inject_admin():
    return dict(is_admin=is_admin)

# Helper function to get a username by user ID and provide it to templates 
# eg: {{ product['user']|get_username }})
@app.template_filter()
def get_username(user_id):
    user = get_user_by_id(user_id)
    return user['username'] if user else 'Unknown'

#Dor price,this functionality helps put comma and decimal places and currency symbol too
@app.template_filter('gbp')
def gbp(value):
    try:
        return "£{:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return "£0.00"
    
from datetime import datetime, timedelta 

# Routing Category count in base.html
@app.context_processor
def inject_categories():
    return {
        "categories": get_categories_with_count()
    }






# Routes
#===================
# These define which template is loaded, or action is taken, depending on the URL requested
#===================
#  Routing Home Page
@app.route('/')
def index():
    products = get_all_products(limit=8, order_by='created DESC')  # Fetch the latest 5 products added
    
    return render_template('index.html', title="Welcome to Omapy", products=products)

# Routing About Page
@app.route('/about/')
def about():
   
 return render_template('about.html', title="About Omapy")

# Routing Products Page
@app.route('/products/')
def products():

    user_id = session.get('user_id')  # Get the logged-in user's ID from the session

    # Ensure user is logged in to view products
    if user_id is None:
        flash(category='warning', message='You must be logged in to view this page.')
        return redirect(url_for('login'))
    
    # ✅ If admin → see ALL products
    if is_admin():
        product_list = get_all_products()
        

    # ✅ Normal user → see only their products
    else:
        product_list = get_products_by_user(user_id)
        user = get_user_by_id(user_id) 
 
   
    return render_template('products.html', title="Your Products", products=product_list, products_user=user_id)

# Routing User Products List Page
@app.route('/products/<int:user_id>/')
def userProducts(user_id):
           
   # ✅ If admin → see ALL products
    if is_admin():
        product_list = get_all_products()
        

    # ✅ Normal user → see only their products
    else:
        product_list = get_products_by_user(user_id)
        user = get_user_by_id(user_id)
        
   
    return render_template('products.html', title=f"Products created by {user['username']}",  products=product_list, products_user=user_id)



@app.route('/product/<int:id>/')
def product(id):

    # Get product data
    product_data = get_product_by_id(id)  

    if not product_data:
         flash(category='warning', message='Requested product not found!')
         return redirect(url_for('/'))
    
     # Get related products (same category)
    related_products = get_related_products( product_data['product_category'],product_data['id'])

    return render_template('product.html', title=product_data['product_name'], product=product_data, related_products=related_products)
   
        # If product not found, redirect to products list with a flash message

# Routing Contact Page
@app.route('/shop/')
def shop():
    shopProducts = get_all_products()
    return render_template('shop.html',title="Shop Products",products=shopProducts)


# Routing Contact Page
@app.route('/contact/')
def contact():
   
 return render_template('contact.html', title="Contact Omapy")

#fetch product category
@app.route('/category/<string:category>/')
def category(category):

    products = get_products_by_category(category)

    if not products:
        flash('No products found in this category.', 'info')

    return render_template('product_category.html',title=category,products=products,category=category)

#fetch product search
@app.route('/search_product/')
def search_product():

    query = request.args.get('q', '').strip()
    products = []

    if query:
        products = search_products(query)

    return render_template(
        'search_product.html',
        title=f"Search results for '{query}'" if query else "Search",
        products=products,
        query=query
    )







# Create Product
@app.route('/create/', methods=['GET', 'POST'])
def create():

    user = session.get('user_id')  # Get the logged-in user's ID from the session
    # Ensure user is logged in to add products
    if user is None:
        flash(category='warning', message='You must be logged in to add a product.')
        return redirect(url_for('login'))

    if request.method == 'POST':

        # Get the product name input from the form
        product_name = request.form['product_name']
        product_price = request.form['product_price']
        product_category = request.form['product_category']
        product_brand = request.form['product_brand']
        product_description = request.form['product_description']
        
                # Handle product_image upload
        product_image = None
        if 'product_image' in request.files:
            product_image_file = request.files['product_image']
            # Check it is an image file and save it
            if product_image_file and product_image_file.filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS:
                # Save the file to the static/uploads directory
                product_image_url = f"/static/uploads/{product_image_file.filename}"
                product_image_file.save(f"{UPLOADS_PATH}{product_image_url}")
                product_image = product_image_url  # Use the uploaded file URL in database


              # Handle product_gallery1 upload
        product_gallery1 = None
        if 'product_gallery1' in request.files:
            product_gallery1_file = request.files['product_gallery1']
            # Check it is an gallery1 file and save it
            if product_gallery1_file and product_gallery1_file.filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS:
                # Save the file to the static/uploads directory
                product_gallery1_url = f"/static/uploads/{product_gallery1_file.filename}"
                product_gallery1_file.save(f"{UPLOADS_PATH}{product_gallery1_url}")
                product_gallery1 = product_gallery1_url  # Use the uploaded file URL in database

              # Handle product_gallery2 upload
        product_gallery2 = None
        if 'product_gallery2' in request.files:
            product_gallery2_file = request.files['product_gallery2']
            # Check it is an gallery2 file and save it
            if product_gallery2_file and product_gallery2_file.filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS:
                # Save the file to the static/uploads directory
                product_gallery2_url = f"/static/uploads/{product_gallery2_file.filename}"
                product_gallery2_file.save(f"{UPLOADS_PATH}{product_gallery2_url}")
                product_gallery2 = product_gallery2_url  # Use the uploaded file URL in database

             # Handle product_gallery3 upload
        product_gallery3 = None
        if 'product_gallery3' in request.files:
            product_gallery3_file = request.files['product_gallery3']
            # Check it is an gallery3 file and save it
            if product_gallery3_file and product_gallery3_file.filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS:
                # Save the file to the static/uploads directory
                product_gallery3_url = f"/static/uploads/{product_gallery3_file.filename}"
                product_gallery3_file.save(f"{UPLOADS_PATH}{product_gallery3_url}")
                product_gallery3 = product_gallery3_url  # Use the uploaded file URL in database


        error = None

        if not product_name:
            error = 'Product Name is required!'
        elif not product_price:
            error = 'Product Price is required!'
        elif not product_category:
             error = 'Product Category is required!'
        elif not product_brand:
            error = 'Product Price is required!'
        elif not product_description:
             error = 'Product Category is required!'
        elif not product_image:
            error = 'Product Image is required!'
        elif not product_gallery1:
             error = 'Product Gallery 1 is required!'
        elif not product_gallery2:
             error = 'Product Gallery 2 is required!'
        elif not product_gallery3:
             error = 'Product Gallery 3 is required!'



         # Display appropriate flash messages
        
            
        if error:
            flash(category='danger', message=error)
            return render_template('create.html')
    
          # [TO-DO]: Add real creation logic here (e.g. save to database record)

        create_product(user,  product_name, product_price, product_category,  product_brand, product_description, product_image, product_gallery1, product_gallery2, product_gallery3)
       # create_product(new_product)
        # ===========================

        # Flash a success message
        flash(category='success', message=f" {product_name}  was Successfully created! Well Done ")
        return redirect(url_for('products'))
    
    return render_template('create.html', title="Create product on Omapy")



# Edit A Product Page
@app.route('/update/<int:id>/', methods=('GET', 'POST'))
def update(id):
    
     # Get product data
    product = get_product_by_id(id)

     # Check for errors
    error = None
       
    if product is None:     # If product not found, add error message
        error = 'product not found!'
        flash(category='warning', message=error)
    elif product['user'] != session.get('user_id') and not is_admin():    # Check user is only accessing their own products
        error = 'You do not have permission to edit this product.'
        flash(category='danger', message=error)
    # If there was an error, redirect to products list
    if error:
        return redirect(url_for('products'))


    # If the request method is POST, process the form submission
    if request.method == 'POST':

        # Get the product name input from the form
        product_name = request.form['product_name']
        product_price = request.form['product_price']
        product_category = request.form['product_category']
        product_brand = request.form['product_brand']
        product_description = request.form['product_description']

                # Handle product image upload
        product_image = product['product_image']  # Default to existing product_image
        if 'product_image' in request.files:
            product_image_file = request.files['product_image']
            # Check it is an image file and save it
            if product_image_file and product_image_file.filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS:
                # Save the file to the static/uploads directory
                product_image_url = f"/static/uploads/{product_image_file.filename}"
                product_image_file.save(f"{UPLOADS_PATH}{product_image_url}")
                product_image = product_image_url  # Use the uploaded file URL in database

        # Handle product image upload
        product_gallery1 = product['product_gallery1']  # Default to existing product_gallery1
        if 'product_gallery1' in request.files:
            product_gallery1_file = request.files['product_gallery1']
            # Check it is an gallery1 file and save it
            if product_gallery1_file and product_gallery1_file.filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS:
                # Save the file to the static/uploads directory
                product_gallery1_url = f"/static/uploads/{product_gallery1_file.filename}"
                product_gallery1_file.save(f"{UPLOADS_PATH}{product_gallery1_url}")
                product_gallery1 = product_gallery1_url  # Use the uploaded file URL in database
        
        # Handle product image upload
        product_gallery2 = product['product_gallery2']  # Default to existing product_gallery2
        if 'product_gallery2' in request.files:
            product_gallery2_file = request.files['product_gallery2']
            # Check it is an gallery2 file and save it
            if product_gallery2_file and product_gallery2_file.filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS:
                # Save the file to the static/uploads directory
                product_gallery2_url = f"/static/uploads/{product_gallery2_file.filename}"
                product_gallery2_file.save(f"{UPLOADS_PATH}{product_gallery2_url}")
                product_gallery2 = product_gallery2_url  # Use the uploaded file URL in database

        # Handle product image upload
        product_gallery3 = product['product_gallery3']  # Default to existing product_gallery3
        if 'product_gallery3' in request.files:
            product_gallery3_file = request.files['product_gallery3']
            # Check it is an gallery3 file and save it
            if product_gallery3_file and product_gallery3_file.filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS:
                # Save the file to the static/uploads directory
                product_gallery3_url = f"/static/uploads/{product_gallery3_file.filename}"
                product_gallery3_file.save(f"{UPLOADS_PATH}{product_gallery3_url}")
                product_gallery3 = product_gallery3_url  # Use the uploaded file URL in database


        error = None

        if not product_name:
            error = 'Product Name is required!'
        elif not product_price:
            error = 'Product Price is required!'
        elif not product_category:
             error = 'Product Category is required!'
        elif not product_brand:
            error = 'Product Price is required!'
        elif not product_description:
             error = 'Product Category is required!'
        elif not product_image:
            error = 'Product Image is required!'
        elif not product_gallery1:
             error = 'Product Gallery 1 is required!'
        elif not product_gallery2:
             error = 'Product Gallery 2 is required!'
        elif not product_gallery3:
             error = 'Product Gallery 3 is required!'



         # Display appropriate flash messages
        
            
        if error:
            flash(category='danger', message=error)
            return render_template('update.html', id=id)
    
          # [TO-DO]: Add real creation logic here (e.g. save to database record)
                # Use the database function to update the product
        update_product(id, product_name, product_price, product_category,  product_brand, product_description, product_image, product_gallery1, product_gallery2, product_gallery3)
        

        #update_product(id, updated_fields)
        # ===========================

        # Flash a success message
        flash(category='success', message=f" {product_name}  was Successfully Updated! Well Done ")
        return redirect(url_for('update', id=id))
    
    return render_template('update.html', title="Update product on Omapy", product=product)

# Delete A Product
@app.route('/delete/<int:id>', methods=('POST',))
def delete(id):

        # Get the product
    product = get_product_by_id(id)
    # Check for errors
    error = None
    if product is None:     # If product not found, add error message
        error = 'Product not found!'
        flash(category='warning', message=error)
    elif product['user'] != session.get('user_id') and not is_admin():    # Check user is only accessing their own products
        error = 'You do not have permission to delete this product.'
        flash(category='danger', message=error)

    # If there was an error, redirect to products list
    if error:
        return redirect(url_for('products'))

    # Use the database function to delete the product
    delete_product(id)

    flash(category='success', message='Product deleted successfully!')
    return redirect(url_for('products'))










# Route vendor page

@app.route('/vendor/<int:user_id>')
def vendor_profile(user_id):

    # Restrict access if not logged in
    if 'user_id' not in session:
        flash('You must be registered to message vendor.', 'warning')
        return redirect(url_for('register'))

    # Fetch vendor by ID
    vendor_data = get_user_by_id(user_id)

    if not vendor_data:
        flash('Requested vendor not found!', 'warning')
        return redirect(url_for('index'))

    return render_template( 'vendor.html',  title=vendor_data['username'], vendor=vendor_data )






# Routing Register Page
@app.route('/register/', methods=('GET', 'POST'))
def register():

    if request.method == 'POST':
        
        # Get the username and password from the form
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        repassword = request.form['repassword']
        phone = request.form['phone']
        whatsapp = request.form['whatsapp']

             # Handle product_image upload
        selfie = None
        if 'selfie' in request.files:
            selfie_file = request.files['selfie']
            # Check it is an image file and save it
            if selfie_file and selfie_file.filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS:
                # Save the file to the static/uploads directory
                selfie_url = f"/static/uploads/{selfie_file.filename}"
                selfie_file.save(f"{UPLOADS_PATH}{selfie_url}")
                selfie = selfie_url  # Use the uploaded file URL in database

        address = request.form['address']
        city = request.form['city']
        postcode = request.form['postcode']

        error = None

        if not first_name:
            error = 'First Name is required!'
        elif not last_name:
            error = 'Last Name is required!'
        elif not username:
            error = 'Username is required!'
        elif not email:
            error = 'Email is required!'
        elif not phone:
            error = 'Phone Number is required!'
        elif not whatsapp:
            error = 'Whatsapp Number is required!'
        elif not selfie:
            error = 'A selfie picture is required!'
        elif not address:
            error = 'Address is required!'
        elif not city:
            error = 'City is required!'
        elif not postcode:
            error = 'Post Code is required!'
        elif not password or not repassword:
            error = 'Password is required!'
        elif password != repassword:
            error = 'Passwords do not match!'
        elif get_user_by_username(username):
            error = 'Username already exists! Please choose a different one.'

            # Display appropriate flash messages
        if error:
            flash(category='danger', message=f"Registration failed: {error}")
        else:
            create_user(first_name, last_name, username, email, password, phone , whatsapp, selfie, address, city, postcode)
            flash(category='success', message=f"Registration successful! Welcome {username}!")
            return redirect(url_for('login'))

        # If no errors, insert the new user
        
            
       
                      

    
        # If the request method is GET, just render the registration form
    return render_template('register.html', title="Register on Omapy")





# Login
@app.route('/login/', methods=('GET', 'POST'))
def login():

    # If the request method is POST, process the login form
    if request.method == 'POST':

        # Get the username and password from the form
        username = request.form['username']
        password = request.form['password']

        # Simple validation checks
        error = None
        if not username:
            error = 'Username is required!'
        elif not password:
            error = 'Password is required!'
        
        # [TO-DO]: Add real authentication logic here
        
                # Validate user credentials
        if error is None:
            user = validate_login(username, password)
            if user is None:
                error = 'Invalid username or password!'
            else:
                session.clear()
                session['user_id'] = user['id']
                session['username'] = user['username']


        # Display appropriate flash messages
        if error is None:
            flash(category='success', message=f"Login successful! Welcome back {username}!")
            return redirect(url_for('index')) 
        else:
            flash(category='danger', message=f"Login failed: {error}")
        
    # If the request method is GET, render the login form
    return render_template('login.html', title="Login on Omapy")


# Logout
@app.route('/logout/')
def logout():
    # Clear the session and redirect to the index page with a flash message
    session.clear()
    flash(category='info', message='You have been logged out.')
    return redirect(url_for('index'))











# Run application
#=========================================================
# This code executes when the script is run directly.
if __name__ == '__main__':
    print("Starting Flask application...")
    print("Open Your Application in Your Browser: http://localhost:81")
    # The app will run on port 81, accessible from any local IP address
    app.run(host='0.0.0.0', port=81, debug=True)


