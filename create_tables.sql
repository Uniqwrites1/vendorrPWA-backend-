-- Vendorr PWA Database Schema for PostgreSQL
-- Run this in Supabase SQL Editor to create all tables

-- Drop existing tables if they exist (be careful in production!)
DROP TABLE IF EXISTS bank_transfer_confirmations CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS menu_items CASCADE;
DROP TABLE IF EXISTS menu_categories CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    hashed_password VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(13) DEFAULT 'customer',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    profile_image VARCHAR(255),
    google_id VARCHAR(100) UNIQUE,
    facebook_id VARCHAR(100) UNIQUE,
    dietary_preferences TEXT,
    notification_preferences TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_google_id ON users(google_id);
CREATE INDEX idx_users_facebook_id ON users(facebook_id);

-- Create Menu Categories Table
CREATE TABLE menu_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    icon VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create Menu Items Table
CREATE TABLE menu_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price FLOAT NOT NULL,
    category_id INTEGER REFERENCES menu_categories(id),
    image_url VARCHAR(255),
    thumbnail_url VARCHAR(255),
    calories INTEGER,
    ingredients TEXT,
    allergens TEXT,
    dietary_tags TEXT,
    is_available BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    status VARCHAR(12),
    preparation_time INTEGER DEFAULT 15,
    spice_level INTEGER,
    customizable BOOLEAN DEFAULT FALSE,
    customization_options TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_menu_items_category_id ON menu_items(category_id);

-- Create Orders Table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES users(id),
    status VARCHAR(17) DEFAULT 'pending_payment',
    payment_status VARCHAR(9) DEFAULT 'pending',
    subtotal FLOAT DEFAULT 0,
    tax_amount FLOAT DEFAULT 0,
    tip_amount FLOAT DEFAULT 0,
    total_amount FLOAT NOT NULL,
    customer_name VARCHAR(200),
    customer_phone VARCHAR(20),
    customer_email VARCHAR(255),
    notes TEXT,
    estimated_ready_time TIMESTAMP WITH TIME ZONE,
    actual_ready_time TIMESTAMP WITH TIME ZONE,
    payment_method VARCHAR(50),
    payment_reference VARCHAR(100),
    bank_transfer_receipt VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_order_number ON orders(order_number);

-- Create Order Items Table
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    menu_item_id INTEGER REFERENCES menu_items(id),
    quantity INTEGER NOT NULL,
    unit_price FLOAT NOT NULL,
    total_price FLOAT NOT NULL,
    customizations TEXT,
    notes TEXT
);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_menu_item_id ON order_items(menu_item_id);

-- Create Reviews Table
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES users(id),
    menu_item_id INTEGER REFERENCES menu_items(id),
    order_id INTEGER REFERENCES orders(id),
    rating INTEGER NOT NULL,
    comment TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    helpful_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_reviews_customer_id ON reviews(customer_id);
CREATE INDEX idx_reviews_menu_item_id ON reviews(menu_item_id);

-- Create Notifications Table
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    order_id INTEGER REFERENCES orders(id),
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50),
    is_read BOOLEAN DEFAULT FALSE,
    is_sent BOOLEAN DEFAULT FALSE,
    push_notification_data TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_order_id ON notifications(order_id);

-- Create Bank Transfer Confirmations Table
CREATE TABLE bank_transfer_confirmations (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    sender_name VARCHAR(200),
    transfer_amount FLOAT NOT NULL,
    transfer_date TIMESTAMP WITH TIME ZONE,
    reference_number VARCHAR(100),
    confirmed_by INTEGER REFERENCES users(id),
    confirmed_at TIMESTAMP WITH TIME ZONE,
    confirmation_notes TEXT,
    receipt_image_path VARCHAR(255),
    is_confirmed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_bank_transfers_order_id ON bank_transfer_confirmations(order_id);

-- Create Admin User (password: @Samson001)
INSERT INTO users (email, hashed_password, first_name, last_name, role, is_active, is_verified, created_at)
VALUES (
    'admin@vendorr.com',
    '$2b$12$UTSbHhkXTiMgzJ50dHKWoOXCoYaPuTynste6.8Pe52Sa2kHBvST4i',
    'Admin',
    'User',
    'admin',
    true,
    true,
    NOW()
);

-- Insert Sample Menu Categories
INSERT INTO menu_categories (name, description, display_order, is_active, icon) VALUES
('Noodles', 'Delicious noodles with various toppings', 1, true, '🍜'),
('Pasta', 'Italian/Nigerian pasta dishes with rich sauces', 2, true, '🍝'),
('Meats', 'Delicious sides to complement your meal', 3, true, '🍖'),
('Drinks', 'Refreshing beverages', 4, true, '🥤'),
('Desserts', 'Sweet treats to end your meal', 5, true, '🍰');

-- Insert Sample Menu Items

-- Noodles (Category 1)
INSERT INTO menu_items (name, description, price, category_id, is_available, is_featured, preparation_time, image_url) VALUES
('Chicken Stir-Fry Noodles', 'Stir-fried noodles with grilled chicken and vegetables', 2500, 1, true, true, 20, 'chicken_noodles.jpg'),
('Seafood Noodles', 'Spicy noodles with prawns, squid, and fish chunks', 2800, 1, true, false, 25, 'seafood_noodles.jpg'),
('Vegetable Noodles', 'Savory noodles mixed with fresh veggies and soy sauce', 2000, 1, true, false, 15, 'veg_noodles.jpg');

-- Pasta (Category 2)
INSERT INTO menu_items (name, description, price, category_id, is_available, is_featured, preparation_time, image_url) VALUES
('Spaghetti Bolognese', 'Classic pasta with minced beef and tomato sauce', 3000, 2, true, true, 25, 'bolognese.jpg'),
('Jollof Spaghetti', 'Nigerian-style pasta cooked in rich jollof sauce', 2700, 2, true, true, 20, 'jollof_spaghetti.jpg'),
('Creamy Alfredo Pasta', 'Pasta in creamy white sauce with chicken strips', 3200, 2, true, false, 25, 'alfredo_pasta.jpg');

-- Meats (Category 3)
INSERT INTO menu_items (name, description, price, category_id, is_available, is_featured, preparation_time, image_url) VALUES
('Grilled Chicken', 'Tender grilled chicken marinated with special herbs', 2500, 3, true, true, 30, 'grilled_chicken.jpg'),
('Beef Suya', 'Spicy Nigerian-style grilled beef skewers', 2200, 3, true, true, 25, 'beef_suya.jpg'),
('Barbecue Ribs', 'Juicy pork ribs in smoky BBQ sauce', 3500, 3, true, false, 35, 'bbq_ribs.jpg'),
('Peppered Meat', 'Spicy fried beef chunks tossed in rich pepper sauce', 2300, 3, true, false, 20, 'peppered_meat.jpg'),
('Peppered Pomo', 'Soft cow skin cooked in savory spicy pepper mix', 1800, 3, true, false, 25, 'peppered_pomo.jpg');

-- Drinks (Category 4)
INSERT INTO menu_items (name, description, price, category_id, is_available, is_featured, preparation_time, image_url) VALUES
('Chapman', 'Refreshing Nigerian mocktail with citrus and bitters', 1200, 4, true, false, 5, 'chapman.jpg'),
('Zobo Drink', 'Hibiscus-based drink with ginger and pineapple flavor', 1000, 4, true, false, 5, 'zobo.jpg'),
('Fresh Fruit Juice', 'Blend of orange, pineapple, and watermelon juice', 1500, 4, true, false, 5, 'fruit_juice.jpg');

-- Desserts (Category 5)
INSERT INTO menu_items (name, description, price, category_id, is_available, is_featured, preparation_time, image_url) VALUES
('Chocolate Cake', 'Rich moist chocolate cake slice', 1800, 5, true, false, 5, 'chocolate_cake.jpg'),
('Vanilla Ice Cream', 'Creamy vanilla ice cream topped with syrup', 1500, 5, true, false, 5, 'vanilla_icecream.jpg'),
('Fruit Parfait', 'Layered dessert with yogurt, granola, and fresh fruits', 2000, 5, true, false, 10, 'fruit_parfait.jpg');

-- Create App Settings Table
CREATE TABLE app_settings (
    id SERIAL PRIMARY KEY,
    whatsapp_link VARCHAR(500),
    whatsapp_enabled BOOLEAN DEFAULT TRUE,
    restaurant_name VARCHAR(200) DEFAULT 'Vendorr',
    restaurant_phone VARCHAR(50) DEFAULT '+234 906 455 4795',
    restaurant_email VARCHAR(255) DEFAULT 'vendorr1@gmail.com',
    restaurant_address TEXT DEFAULT 'Red Brick, Faculty of Arts, University of Jos',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Insert default settings
INSERT INTO app_settings (whatsapp_link, whatsapp_enabled, restaurant_name, restaurant_phone, restaurant_email, restaurant_address)
VALUES (
    'https://wa.me/qr/EKAYKJ7XOVOTP1',
    true,
    'Vendorr',
    '+234 906 455 4795, +234 916 492 3056',
    'vendorr1@gmail.com',
    'Red Brick, Faculty of Arts, University of Jos, Jos, Plateau State'
);

-- Success message
SELECT 'Database schema created successfully! Admin user: admin@vendorr.com, password: @Samson001' as message;
