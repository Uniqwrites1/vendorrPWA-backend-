-- ============================================
-- Fix menu items status in Production Database
-- Run this in Supabase SQL Editor to make items visible in API
-- ============================================

-- Update all menu items to have status = 'available'
UPDATE menu_items
SET status = 'available'
WHERE status IS NULL OR status = '';

-- Verify the update
SELECT
    'Menu items updated!' as message,
    COUNT(*) as total_items,
    COUNT(CASE WHEN status = 'available' THEN 1 END) as available_items,
    COUNT(CASE WHEN is_featured = true THEN 1 END) as featured_items
FROM menu_items;
