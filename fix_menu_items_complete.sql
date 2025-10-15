-- ============================================
-- COMPREHENSIVE FIX for menu_items status
-- Run this in Supabase SQL Editor
-- ============================================

-- Step 1: Update all existing menu items to have status = 'available'
UPDATE menu_items
SET status = 'available'
WHERE status IS NULL OR status = '' OR status != 'available';

-- Step 2: Set default value for status column (for future inserts)
ALTER TABLE menu_items
ALTER COLUMN status SET DEFAULT 'available';

-- Step 3: Make sure all items are marked as available
UPDATE menu_items
SET is_available = true
WHERE is_available IS NULL;

-- Step 4: Verify the fix
SELECT
    '✅ Menu items fixed!' as message,
    COUNT(*) as total_items,
    COUNT(CASE WHEN status = 'available' THEN 1 END) as items_with_available_status,
    COUNT(CASE WHEN is_available = true THEN 1 END) as items_marked_available,
    COUNT(CASE WHEN is_featured = true THEN 1 END) as featured_items
FROM menu_items;

-- Step 5: Show sample items to verify
SELECT
    id,
    name,
    price,
    status,
    is_available,
    is_featured
FROM menu_items
LIMIT 5;
