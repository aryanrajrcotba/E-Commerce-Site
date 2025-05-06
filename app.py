from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import config
from datetime import datetime, timedelta
import random
import os
from decimal import Decimal

app = Flask(__name__)
app.secret_key = os.urandom(24)

# MySQL Configuration
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
mysql = MySQL(app)

# Helper function to get user details
def get_user_details(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    return cur.fetchone()

@app.route('/')
def index():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM products")
        products = cur.fetchall()
        print(f"Number of products fetched: {len(products)}")  # Debug print
        if not products:
            print("No products found in database")  # Debug print
        return render_template('index.html', products=products)
    except Exception as e:
        print(f"Error in index route: {str(e)}")  # Debug print
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
    session.pop('cart', None)
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

@app.route('/add_to_cart/<int:product_id>', methods=['POST', 'GET'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        flash('Please login to add items to cart')
        return redirect(url_for('login'))
    user_id = session['user_id']
    quantity = int(request.form.get('quantity', 1))
    cur = mysql.connection.cursor()
    cur.execute("SELECT stock FROM products WHERE product_id = %s", (product_id,))
    product = cur.fetchone()
    if not product:
        flash('Product not found')
        return redirect(url_for('index'))
    if product[0] < quantity:
        flash('Not enough stock')
        return redirect(url_for('index'))
    cur.execute("""
        INSERT INTO cart (user_id, product_id, quantity)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE quantity = quantity + %s
    """, (user_id, product_id, quantity, quantity))
    mysql.connection.commit()
    flash('Product added to cart')
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    if 'user_id' not in session:
        flash('Please login to view cart')
        return redirect(url_for('login'))
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT c.product_id, c.quantity, p.name, p.price, p.image_url
        FROM cart c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id = %s
    """, (user_id,))
    cart_items = cur.fetchall()
    subtotal = sum(item[1] * item[3] for item in cart_items)
    tax = subtotal * Decimal('0.1')
    total = subtotal + tax
    return render_template('cart.html', cart_items=cart_items, subtotal=subtotal, tax=tax, total=total)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401
    user_id = session['user_id']
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity', 0))
    cur = mysql.connection.cursor()
    if quantity <= 0:
        cur.execute("DELETE FROM cart WHERE user_id = %s AND product_id = %s", (user_id, product_id))
    else:
        cur.execute("UPDATE cart SET quantity = %s WHERE user_id = %s AND product_id = %s", (quantity, user_id, product_id))
    mysql.connection.commit()
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        flash('Please login to checkout')
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    # Fetch cart items from the database
    cur.execute("""
        SELECT c.product_id, c.quantity, p.name, p.price, p.image_url
        FROM cart c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id = %s
    """, (user_id,))
    cart_items = cur.fetchall()
    if not cart_items:
        flash('Your cart is empty')
        return redirect(url_for('cart'))

    subtotal = sum(item[1] * item[3] for item in cart_items)
    tax = subtotal * Decimal('0.1')
    total = subtotal + tax

    # Get user details
    user = get_user_details(user_id)
    if not user:
        flash('User not found')
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            # Create order
            cur.execute(
                "INSERT INTO orders (user_id, total_amount, order_status) VALUES (%s, %s, %s)",
                (user_id, total, 'Processing')
            )
            order_id = cur.lastrowid

            # Add order items
            for item in cart_items:
                cur.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, subtotal) VALUES (%s, %s, %s, %s)",
                    (order_id, item[0], item[1], item[1] * item[3])
                )
                # Update product stock
                cur.execute(
                    "UPDATE products SET stock = stock - %s WHERE product_id = %s",
                    (item[1], item[0])
                )

            # Update payment record with selected payment method
            payment_method = request.form.get('payment_method', 'Not Specified')
            cur.execute(
                "UPDATE payments SET payment_method = %s WHERE order_id = %s",
                (payment_method, order_id)
            )

            # Clear the user's cart
            cur.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
            mysql.connection.commit()
            flash('Order placed successfully!')
            return redirect(url_for('order_confirmation', order_id=order_id))
        except Exception as e:
            mysql.connection.rollback()
            flash('Error placing order. Please try again.')
            return redirect(url_for('checkout'))

    return render_template('checkout.html',
        cart_items=cart_items,
        subtotal=subtotal,
        tax=tax,
        total=total,
        user=user
    )

@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    if 'user_id' not in session:
        flash('Please login to view order')
        return redirect(url_for('login'))
    try:
        cur = mysql.connection.cursor()
        # Fetch order and payment info
        cur.execute("""
            SELECT o.order_id, o.created_at, o.total_amount, o.order_status, 
                   p.payment_status, p.payment_method
            FROM orders o
            LEFT JOIN payments p ON o.order_id = p.order_id
            WHERE o.order_id = %s AND o.user_id = %s
        """, (order_id, session['user_id']))
        order = cur.fetchone()
        if not order:
            flash('Order not found')
            return redirect(url_for('index'))
        # Fetch order items
        cur.execute("""
            SELECT oi.product_id, oi.quantity, oi.subtotal, p.name, p.price, p.image_url
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s
        """, (order_id,))
        items = cur.fetchall()
        return render_template('order_confirmation.html', order=order, items=items)
    except Exception as e:
        flash('Error loading order details')
        return redirect(url_for('index'))

@app.route('/orders')
def orders():
    if 'user_id' not in session:
        flash('Please login to view orders')
        return redirect(url_for('login'))
    try:
        user_id = session['user_id']
        cur = mysql.connection.cursor()
        
        # Debug print
        print(f"Fetching orders for user_id: {user_id}")
        
        # Fetch all orders for the user with payment information
        cur.execute("""
            SELECT 
                o.order_id, 
                o.created_at, 
                o.total_amount, 
                o.order_status, 
                COALESCE(p.payment_status, 'Pending') as payment_status, 
                COALESCE(p.payment_method, 'Not Specified') as payment_method
            FROM orders o
            LEFT JOIN payments p ON o.order_id = p.order_id
            WHERE o.user_id = %s
            ORDER BY o.created_at DESC
        """, (user_id,))
        orders = cur.fetchall()
        
        # Debug print
        print(f"Found {len(orders)} orders")
        
        # Fetch order items for each order
        order_items = {}
        for order in orders:
            order_id = order[0]
            cur.execute("""
                SELECT 
                    oi.product_id, 
                    oi.quantity, 
                    oi.subtotal, 
                    p.name, 
                    p.price, 
                    p.image_url
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = %s
            """, (order_id,))
            items = cur.fetchall()
            order_items[order_id] = items
            
            # Debug print
            print(f"Order {order_id} has {len(items)} items")
        
        return render_template('orders.html', 
                             orders=orders, 
                             order_items=order_items,
                             timedelta=timedelta)  # Pass timedelta to template
    except Exception as e:
        print(f"Error in orders route: {str(e)}")  # Debug print
        flash('Error loading orders')
        return render_template('orders.html', orders=[], order_items={})

@app.route('/products')
def products():
    try:
        cur = mysql.connection.cursor()
        search_query = request.args.get('search', '')
        
        if search_query:
            cur.execute("""
                SELECT * FROM products 
                WHERE name LIKE %s OR description LIKE %s
            """, (f'%{search_query}%', f'%{search_query}%'))
        else:
            cur.execute("SELECT * FROM products")
            
        products = cur.fetchall()
        return render_template('products.html', products=products)
    except Exception as e:
        flash('Error loading products')
        return render_template('products.html', products=[])

@app.route('/test_db')
def test_db():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM products")
        count = cur.fetchone()[0]
        return f"Database connection successful! Found {count} products."
    except Exception as e:
        return f"Database connection failed: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)