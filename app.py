from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import config

app = Flask(__name__)
app.secret_key = 'ecommerce_secret'

# MySQL Configuration
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
mysql = MySQL(app)

@app.route('/')
def index():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM products")
        products = cur.fetchall()
        return render_template('index.html', products=products)
    except Exception as e:
        flash('Error loading products')
        return render_template('index.html', products=[])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            password = generate_password_hash(request.form['password'])
            address = request.form['address']
            phone = request.form['phone']
            
            cur = mysql.connection.cursor()
            # Check if email already exists
            cur.execute("SELECT email FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                flash('Email already registered')
                return redirect(url_for('register'))
            
            cur.execute(
                "INSERT INTO users (name, email, password, address, phone) VALUES (%s, %s, %s, %s, %s)", 
                (name, email, password, address, phone)
            )
            mysql.connection.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except Exception as e:
            mysql.connection.rollback()
            flash('Registration failed')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password_input = request.form['password']
            
            cur = mysql.connection.cursor()
            cur.execute("SELECT user_id, password FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            
            if user and check_password_hash(user[1], password_input):
                session['user_id'] = user[0]
                flash('Login successful!')
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password')
                return redirect(url_for('login'))
        except Exception as e:
            flash('Login failed')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out')
    return redirect(url_for('index'))

@app.route('/product/<int:id>')
def product_detail(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM products WHERE product_id = %s", (id,))
        product = cur.fetchone()
        if not product:
            flash('Product not found')
            return redirect(url_for('index'))
        return render_template('product.html', product=product)
    except Exception as e:
        flash('Error loading product')
        return redirect(url_for('index'))

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    try:
        # Verify product exists
        cur = mysql.connection.cursor()
        cur.execute("SELECT product_id FROM products WHERE product_id = %s", (product_id,))
        if not cur.fetchone():
            flash('Product not found')
            return redirect(url_for('index'))
            
        if 'cart' not in session:
            session['cart'] = {}
        
        cart = session['cart']
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
        session['cart'] = cart
        flash('Product added to cart')
        return redirect(url_for('cart'))
    except Exception as e:
        flash('Error adding to cart')
        return redirect(url_for('index'))

@app.route('/cart')
def cart():
    try:
        if 'cart' not in session:
            session['cart'] = {}
        
        cart = session['cart']
        if not cart:
            return render_template('cart.html', items=[], cart={})
            
        product_ids = tuple(cart.keys())
        cur = mysql.connection.cursor()
        query = "SELECT * FROM products WHERE product_id IN %s"
        cur.execute(query, (product_ids,))
        items = cur.fetchall()
        
        # Calculate total
        total = 0
        for item in items:
            total += item[3] * cart[str(item[0])]  # item[3] is price
        
        return render_template('cart.html', items=items, cart=cart, total=total)
    except Exception as e:
        flash('Error loading cart')
        return render_template('cart.html', items=[], cart={})

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        flash('Please login to checkout')
        return redirect(url_for('login'))
    
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty')
        return redirect(url_for('cart'))
    
    try:
        user_id = session['user_id']
        cart = session['cart']
        
        # Verify user exists and get user details
        cur = mysql.connection.cursor()
        cur.execute("SELECT user_id, name, address, phone FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()
        if not user:
            flash('User not found')
            return redirect(url_for('login'))
        
        # Calculate total and prepare order items
        total = 0
        order_items = []
        for pid, qty in cart.items():
            cur.execute("SELECT product_id, name, price FROM products WHERE product_id = %s", (pid,))
            product = cur.fetchone()
            if not product:
                flash(f'Product {pid} not found')
                return redirect(url_for('cart'))
            price = product[2]
            subtotal = price * qty
            total += subtotal
            order_items.append({
                'product_id': pid,
                'name': product[1],
                'quantity': qty,
                'price': price,
                'subtotal': subtotal
            })
        
        # Calculate delivery date (3-5 business days from now)
        from datetime import datetime, timedelta
        import random
        order_date = datetime.now()
        delivery_days = random.randint(3, 5)  # Random delivery estimate between 3-5 days
        delivery_date = order_date + timedelta(days=delivery_days)
        
        # Create order
        cur.execute(
            "INSERT INTO orders (user_id, total_amount, status, order_date) VALUES (%s, %s, 'processing', %s)", 
            (user_id, total, order_date)
        )
        order_id = cur.lastrowid
        
        # Add order items
        for item in order_items:
            cur.execute(
                "INSERT INTO order_items (order_id, product_id, product_name, quantity, price, subtotal) VALUES (%s, %s, %s, %s, %s, %s)", 
                (order_id, item['product_id'], item['name'], item['quantity'], item['price'], item['subtotal'])
            )
        
        mysql.connection.commit()
        session.pop('cart', None)
        
        # Format address for display
        user_address = f"{user[1]}, {user[2]}, Phone: {user[3]}"
        
        return render_template('checkout.html', 
                            total=total,
                            order_id=order_id,
                            order_date=order_date,
                            delivery_date=delivery_date,
                            user_address=user_address,
                            payment_method="Credit/Debit Card",  # Default payment method
                            order_items=order_items)
    
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Checkout failed: {str(e)}')
        app.logger.error(f'Checkout error: {str(e)}')
        return redirect(url_for('cart'))
        
        # Verify user exists
        cur = mysql.connection.cursor()
        cur.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        if not cur.fetchone():
            flash('User not found')
            return redirect(url_for('login'))
        
        # Calculate total
        total = 0
        order_items = []
        for pid, qty in cart.items():
            cur.execute("SELECT price FROM products WHERE product_id = %s", (pid,))
            product = cur.fetchone()
            if not product:
                flash(f'Product {pid} not found')
                return redirect(url_for('cart'))
            price = product[0]
            total += price * qty
            order_items.append((pid, qty, price * qty))
        
        # Create order
        cur.execute(
            "INSERT INTO orders (user_id, total_amount, status) VALUES (%s, %s, 'pending')", 
            (user_id, total)
        )
        order_id = cur.lastrowid
        
        # Add order items
        for pid, qty, subtotal in order_items:
            cur.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, subtotal) VALUES (%s, %s, %s, %s)", 
                (order_id, pid, qty, subtotal)
            )
        
        mysql.connection.commit()
        session.pop('cart', None)
        flash('Order placed successfully!')
        return render_template('checkout.html', total=total, order_id=order_id)
    except Exception as e:
        mysql.connection.rollback()
        flash('Checkout failed')
        return redirect(url_for('cart'))

if __name__ == '__main__':
    app.run(debug=True)