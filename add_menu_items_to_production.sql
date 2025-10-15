-- ============================================
-- Add Sample Menu Items to Production Database
-- Run this in Supabase SQL Editor AFTER running create_tables.sql
-- ============================================

-- First, check if categories exist, if not create them
INSERT INTO categories (name, description, display_order)
SELECT 'Noodles', 'Delicious noodle dishes', 1
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE name = 'Noodles');

INSERT INTO categories (name, description, display_order)
SELECT 'Pasta', 'Italian-style pasta dishes', 2
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE name = 'Pasta');

INSERT INTO categories (name, description, display_order)
SELECT 'Meats', 'Grilled and fried meat options', 3
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE name = 'Meats');

INSERT INTO categories (name, description, display_order)
SELECT 'Drinks', 'Refreshing beverages', 4
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE name = 'Drinks');

INSERT INTO categories (name, description, display_order)
SELECT 'Desserts', 'Sweet treats', 5
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE name = 'Desserts');

-- Now insert menu items (only if they don't already exist)
-- Noodles (Category 1)
INSERT INTO menu_items (name, description, price, category_id, is_available, is_featured, preparation_time, image_url)
SELECT 'Chicken Stir-Fry Noodles', 'Stir-fried noodles with grilled chicken and vegetables', 2500, 1, true, true, 20, 'chicken_noodles.jpg'
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Chicken Stir-Fry Noodles');

INSERT INTO menu_items (name, description, price, category_id, is_available, is_featured, preparation_time, image_url)
SELECT 'Seafood Noodles', 'Spicy noodles with prawns, squid, and fish chunks', 2800, 1, true, false, 25, 'seafood_noodles.jpg'
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Seafood Noodles');

INSERT INTO menu_items (name, description, price, category_id, is_available, is_featured, preparation_time, image_url)
SELECT 'Vegetable Noodles', 'Savory noodles mixed with fresh veggies and soy sauce', 2000, 1, true, false, 15, 'veg_noodles.jpg'
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Vegetable Noodles');

-- Pasta (Category 2)
INSERT INTO menu_items (name, description, price, category_id, is_available, is_featured, preparation_time, image_url)
SELECT 'Spaghetti Bolognese', 'Classic pasta with minced beef and tomato sauce', 3000, 2, true, true, 25, 'bolognese.jpg'
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Spaghetti Bolognese');

INSERT INTO menu_items (name, description, price, category_id, is_available, is_featured, preparation_time, image_url)
SELECT 'Jollof Spaghetti', 'Nigerian-style pasta cooked in rich jollof sauce', 2700, 2, true, true, 20, 'jollof_spaghetti.jpg'
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Jollof Spaghetti');

INSERT INTO menu_items (name, description, price, category_id, is_available, is_featured, preparation_time, image_url)
SELECT 'Creamy Alfredo Pasta', 'Pasta in creamy white sauce with chicken strips', 3200, 2, true, false, 25, 'alfredo_pasta.jpg'
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Creamy Alfredo Pasta');

-- Meats (Category 3)
INSERT INTO menu_items (name, description, price, category_id, is_available, is_featured, preparation_time, image_url)
SELECT 'Grilled Chicken', 'Tender grilled chicken marinated with special herbs', 2500, 3, true, true, 30, 'grilled_chicken.jpg'
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Grilled Chicken');

INSERT INTO menu_items (name, description, price, category_id, is_available, is_featured, preparation_time, image_url)
SELECT 'Beef Suya', 'Spicy Nigerian-style grilled beef skewers', 2200, 3, true, true, 25, 'beef_suya.jpg'
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Beef Suya');

INSERT INTO menu_items (name, description, price, category_id, is_available, is_featured, preparation_time, image_url)
SELECT 'Barbecue Ribs', 'Juicy pork ribs in smoky BBQ sauce', 3500, 3, true, false, 35, 'bbq_ribs.jpg'
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Barbecue Ribs');

INSERT INTO menu_items (name, description, price, category_id, is_available, is_featured, preparation_time, image_url)
SELECT 'Peppered Meat', 'Spicy fried beef chunks tossed in rich pepper sauce', 2300, 3, true, false, 20, 'peppered_meat.jpg'
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Peppered Meat');

INSERT INTO menu_items (name, description, price, category_id, is_available, is_featured, preparation_time, image_url)
SELECT 'Peppered Pomo', 'Soft cow skin cooked in savory spicy pepper mix', 1800, 3, true, false, 25, 'peppered_pomo.jpg'
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Peppered Pomo');

-- Drinks (Category 4)
INSERT INTO menu_items (name, description, price, category_id, is_available, is_featured, preparation_time, image_url)
SELECT 'Chapman', 'Refreshing Nigerian mocktail with citrus and bitters', 1200, 4, true, false, 5, 'chapman.jpg'
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Chapman');

INSERT INTO menu_items (name, description, price, category_id, is_available, is_featured, preparation_time, image_url)
SELECT 'Zobo Drink', 'Hibiscus-based drink with ginger and pineapple flavor', 1000, 4, true, false, 5, 'zobo.jpg'
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Zobo Drink');

INSERT INTO menu_items (name, description, price, category_id, is_available, is_featured, preparation_time, image_url)
SELECT 'Fresh Fruit Juice', 'Blend of orange, pineapple, and watermelon juice', 1500, 4, true, false, 5, 'fruit_juice.jpg'
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Fresh Fruit Juice');

-- Desserts (Category 5)
INSERT INTO menu_items (name, description, price, category_id, is_available, is_featured, preparation_time, image_url)
SELECT 'Chocolate Cake', 'Rich moist chocolate cake slice', 1800, 5, true, false, 5, 'chocolate_cake.jpg'
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Chocolate Cake');

INSERT INTO menu_items (name, description, price, category_id, is_available, is_featured, preparation_time, image_url)
SELECT 'Vanilla Ice Cream', 'Creamy vanilla ice cream topped with syrup', 1500, 5, true, false, 5, 'vanilla_icecream.jpg'
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Vanilla Ice Cream');

INSERT INTO menu_items (name, description, price, category_id, is_available, is_featured, preparation_time, image_url)
SELECT 'Fruit Parfait', 'Layered dessert with yogurt, granola, and fresh fruits', 2000, 5, true, false, 10, 'fruit_parfait.jpg'
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Fruit Parfait');

-- Verify the data
SELECT
    'Menu items added successfully!' as status,
    (SELECT COUNT(*) FROM categories) as total_categories,
    (SELECT COUNT(*) FROM menu_items) as total_menu_items,
    (SELECT COUNT(*) FROM menu_items WHERE is_featured = true) as featured_items;
