-- Drop and recreate the database
-- DROP DATABASE IF EXISTS ecommerce;
-- CREATE DATABASE ecommerce;
USE ecommerce;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    phone VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    category VARCHAR(50) NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    seller_id INT,
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
);

-- Create cart table
CREATE TABLE IF NOT EXISTS cart (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    UNIQUE KEY unique_cart_item (user_id, product_id)
);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    order_status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    seller_approval_status VARCHAR(20) DEFAULT 'Pending',
    seller_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
);

-- Create order_items table
CREATE TABLE IF NOT EXISTS order_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Create payments table
CREATE TABLE IF NOT EXISTS payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    user_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    payment_method VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Create sellers table
CREATE TABLE IF NOT EXISTS sellers (
    seller_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample products
INSERT INTO products (name, description, price, stock, category, image_url) VALUES
('iPhone 13 Pro', 'Latest Apple iPhone with A15 Bionic chip, Pro camera system, and Super Retina XDR display.', 999.99, 50, 'Electronics', 'https://images.unsplash.com/photo-1632661674596-79bd3e16b0c0?w=500'),
('Samsung Galaxy S21', 'Powerful Android smartphone with 5G capability, triple camera system, and 120Hz display.', 799.99, 45, 'Electronics', 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=500'),
('MacBook Pro M1', 'Apple\'s revolutionary laptop with M1 chip, Retina display, and all-day battery life.', 1299.99, 30, 'Electronics', 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500'),
('Sony WH-1000XM4', 'Premium noise-cancelling headphones with exceptional sound quality and long battery life.', 349.99, 60, 'Electronics', 'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=500'),
('Nike Air Max 270', 'Comfortable and stylish sneakers with Air cushioning and breathable mesh upper.', 150.00, 100, 'Fashion', 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500'),
('Adidas Ultraboost', 'Responsive running shoes with Boost midsole and Primeknit upper.', 180.00, 75, 'Fashion', 'https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=500'),
('Levi\'s 501 Jeans', 'Classic straight-leg jeans with button fly and iconic Levi\'s quality.', 59.99, 200, 'Fashion', 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=500'),
('The North Face Jacket', 'Waterproof and insulated jacket perfect for outdoor adventures.', 199.99, 40, 'Fashion', 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=500'),
('Dyson V11 Vacuum', 'Cordless vacuum cleaner with powerful suction and intelligent cleaning modes.', 599.99, 25, 'Home', 'https://images.unsplash.com/photo-1589003077984-894e133dabab?w=500'),
('Instant Pot Duo', '7-in-1 multi-cooker for pressure cooking, slow cooking, and more.', 89.99, 80, 'Home', 'https://images.unsplash.com/photo-1584990347449-a2d4c2c9d0a9?w=500'),
('KitchenAid Mixer', 'Professional stand mixer with 10 speeds and multiple attachments.', 299.99, 35, 'Home', 'https://images.unsplash.com/photo-1581235720704-06d3acfcb36f?w=500'),
('Philips Hue Starter Kit', 'Smart lighting system with color-changing bulbs and bridge.', 199.99, 50, 'Home', 'https://images.unsplash.com/photo-1558002038-1055907df827?w=500');

-- Insert sample user (password: test123)
INSERT INTO users (name, email, password, address, phone) VALUES
('Test User', 'test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYpR1IOBY5GJQHy', '123 Test Street, Test City, TC 12345', '1234567890');

-- Insert sample seller (password: seller123)
INSERT INTO sellers (name, email, password, phone) VALUES
('Test Seller', 'seller@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYpR1IOBY5GJQHy', '9876543210');

-- Insert new seller (password: 123456)
INSERT INTO sellers (name, email, password, phone) VALUES
('Aryan Raj', 'aryanraj@gmail.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '9876543210');

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

-- Insert a sample payment method for demonstration
INSERT INTO payments (order_id, user_id, amount, payment_status, payment_method) VALUES
(1, 1, 95.49, 'Completed', 'Credit Card'),
(2, 2, 599.00, 'Pending', 'PayPal');

SELECT * FROM products;
INSERT INTO cart (user_id, product_id, quantity) VALUES
(1, 1, 1),
(1, 2, 1),
(2, 4, 1);
SELECT * FROM cart;

-- If the item is not in the cart, insert it
INSERT INTO cart (user_id, product_id, quantity)
VALUES (1, 3, 2)
ON DUPLICATE KEY UPDATE quantity = quantity + 2;

UPDATE cart SET quantity = 5
WHERE user_id = 1 AND product_id = 3;

SELECT c.product_id, c.quantity, p.name, p.price, p.image_url
FROM cart c
JOIN products p ON c.product_id = p.product_id
WHERE c.user_id = 1;

DELETE FROM cart WHERE user_id = 1 AND product_id = 3;

DELETE FROM cart WHERE user_id = 1;

DELETE FROM orders
WHERE order_id IN (
    SELECT o.order_id
    FROM orders o
    LEFT JOIN payments p ON o.order_id = p.order_id
    WHERE p.order_id IS NULL
);

INSERT INTO payments (order_id, user_id, amount, payment_status, payment_method)
SELECT o.order_id, o.user_id, o.total_amount, 'Pending', 'Pay on Delivery'
FROM orders o
LEFT JOIN payments p ON o.order_id = p.order_id
WHERE p.order_id IS NULL;

-- Place Order Feature
-- 1. Create new order
INSERT INTO orders (user_id, total_amount, order_status)
SELECT 
    c.user_id,
    SUM(p.price * c.quantity) as total_amount,
    'Processing' as order_status
FROM cart c
JOIN products p ON c.product_id = p.product_id
WHERE c.user_id = 1
GROUP BY c.user_id;

-- 2. Get the last inserted order_id
SET @new_order_id = LAST_INSERT_ID();

-- 3. Insert order items from cart
INSERT INTO order_items (order_id, product_id, quantity, subtotal)
SELECT 
    @new_order_id,
    c.product_id,
    c.quantity,
    (p.price * c.quantity) as subtotal
FROM cart c
JOIN products p ON c.product_id = p.product_id
WHERE c.user_id = 1;

-- 4. Create payment record with default values
INSERT INTO payments (order_id, user_id, amount, payment_status, payment_method)
SELECT 
    @new_order_id,
    user_id,
    total_amount,
    'Pending',
    'Not Specified'
FROM orders 
WHERE order_id = @new_order_id;

-- 5. Update product stock
UPDATE products p
JOIN cart c ON p.product_id = c.product_id
SET p.stock = p.stock - c.quantity
WHERE c.user_id = 1;

-- 6. Clear the cart after successful order placement
DELETE FROM cart WHERE user_id = 1;

-- 7. Update payment method if provided
UPDATE payments 
SET payment_method = 'Credit Card'  -- This should be dynamic based on user selection
WHERE order_id = @new_order_id;

-- 8. Update order status to 'Processing'
UPDATE orders 
SET order_status = 'Processing'
WHERE order_id = @new_order_id;

-- 9. Add a trigger to automatically create payment record for new orders
DELIMITER //
CREATE TRIGGER after_order_insert
AFTER INSERT ON orders
FOR EACH ROW
BEGIN
    INSERT INTO payments (order_id, user_id, amount, payment_status, payment_method)
    VALUES (NEW.order_id, NEW.user_id, NEW.total_amount, 'Pending', 'Not Specified');
END//
DELIMITER ;

-- 10. Add a trigger to update order status when payment status changes
DELIMITER //
CREATE TRIGGER after_payment_update
AFTER UPDATE ON payments
FOR EACH ROW
BEGIN
    IF NEW.payment_status = 'Completed' THEN
        UPDATE orders SET order_status = 'Processing' WHERE order_id = NEW.order_id;
    END IF;
END//
DELIMITER ;

-- Update sample products with seller_id
UPDATE products SET seller_id = 1 WHERE product_id IN (1, 2, 3, 4);

-- Add seller approval trigger
DELIMITER //
CREATE TRIGGER after_seller_approval
AFTER UPDATE ON orders
FOR EACH ROW
BEGIN
    IF NEW.seller_approval_status = 'Approved' THEN
        UPDATE orders SET order_status = 'Processing' WHERE order_id = NEW.order_id;
    ELSEIF NEW.seller_approval_status = 'Rejected' THEN
        UPDATE orders SET order_status = 'Cancelled' WHERE order_id = NEW.order_id;
    END IF;
END//
DELIMITER ;

-- Add seller dashboard view
CREATE VIEW seller_dashboard AS
SELECT 
    o.order_id,
    o.created_at,
    o.total_amount,
    o.order_status,
    o.seller_approval_status,
    p.payment_status,
    p.payment_method,
    u.name as customer_name,
    u.email as customer_email,
    u.phone as customer_phone,
    u.address as customer_address
FROM orders o
JOIN payments p ON o.order_id = p.order_id
JOIN users u ON o.user_id = u.user_id
WHERE o.seller_id IS NOT NULL;

-- Add seller orders view
CREATE VIEW seller_orders AS
SELECT 
    o.order_id,
    o.created_at,
    o.total_amount,
    o.order_status,
    o.seller_approval_status,
    p.payment_status,
    p.payment_method,
    u.name as customer_name,
    GROUP_CONCAT(CONCAT(pr.name, ' (', oi.quantity, ')') SEPARATOR ', ') as products
FROM orders o
JOIN payments p ON o.order_id = p.order_id
JOIN users u ON o.user_id = u.user_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products pr ON oi.product_id = pr.product_id
WHERE o.seller_id IS NOT NULL
GROUP BY o.order_id;

