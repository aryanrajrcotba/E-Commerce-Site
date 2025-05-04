-- Drop and recreate the database
DROP DATABASE IF EXISTS ecommerce_db;
CREATE DATABASE ecommerce_db;
USE ecommerce_db;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    address TEXT,
    phone VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL,
    category VARCHAR(100),
    image_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Create cart table
CREATE TABLE IF NOT EXISTS cart (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    total_amount DECIMAL(10,2) NOT NULL,
    order_status ENUM('Pending', 'Shipped', 'Delivered', 'Cancelled') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create order_items table
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create payments table
CREATE TABLE IF NOT EXISTS payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    user_id INT,
    amount DECIMAL(10,2) NOT NULL,
    payment_status ENUM('Pending', 'Completed', 'Failed') DEFAULT 'Pending',
    payment_method ENUM('Credit Card', 'Debit Card', 'PayPal', 'UPI', 'Net Banking'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Sample users
INSERT INTO users (name, email, password, address, phone) VALUES
('Alice Johnson', 'alice@example.com', 'password123', '123 Main St, Cityville', '1234567890'),
('Bob Smith', 'bob@example.com', 'securepass', '456 Elm St, Townville', '9876543210');

-- Sample products
INSERT INTO products (name, description, price, stock, category, image_url) VALUES
('Wireless Mouse', 'Ergonomic wireless mouse with USB receiver', 25.99, 150, 'Electronics', 'images/mouse.jpg'),
('Mechanical Keyboard', 'RGB backlit mechanical keyboard with blue switches', 69.50, 100, 'Electronics', 'images/keyboard.jpg'),
('Gaming Chair', 'Adjustable gaming chair with lumbar support', 199.99, 50, 'Furniture', 'images/gaming_chair.jpg'),
('Smartphone', '6.5" display, 128GB storage, 5G enabled smartphone', 599.00, 200, 'Mobile Phones', 'images/smartphone.jpg'),
('Bluetooth Speaker', 'Portable waterproof Bluetooth speaker', 45.75, 80, 'Audio', 'images/speaker.jpg');

-- Sample cart (adding to cart)
INSERT INTO cart (user_id, product_id, quantity) VALUES
(1, 1, 1),  -- Alice adds 1 Wireless Mouse
(1, 2, 1),  -- Alice adds 1 Mechanical Keyboard
(2, 4, 1);  -- Bob adds 1 Smartphone

-- Sample orders
INSERT INTO orders (user_id, total_amount, order_status) VALUES
(1, 95.49, 'Shipped'),
(2, 599.00, 'Pending');

-- Sample order items
INSERT INTO order_items (order_id, product_id, quantity, subtotal) VALUES
(1, 1, 1, 25.99),
(1, 2, 1, 69.50),
(2, 4, 1, 599.00);

-- Sample payments
INSERT INTO payments (order_id, user_id, amount, payment_status, payment_method) VALUES
(1, 1, 95.49, 'Completed', 'Credit Card'),
(2, 2, 599.00, 'Pending', 'PayPal');
