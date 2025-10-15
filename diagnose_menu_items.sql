-- ============================================
-- Diagnostic: Check menu_items table structure and data
-- Run this in Supabase SQL Editor to see what's wrong
-- ============================================

-- 1. Check if status column exists
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'menu_items'
ORDER BY ordinal_position;

-- 2. Check sample data from menu_items
SELECT
    id,
    name,
    price,
    status,
    is_available,
    is_featured,
    category_id
FROM menu_items
LIMIT 5;

-- 3. Count items by status
SELECT
    status,
    COUNT(*) as count
FROM menu_items
GROUP BY status;
