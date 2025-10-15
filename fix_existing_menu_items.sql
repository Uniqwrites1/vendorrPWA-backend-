-- Fix existing menu items to have proper status field
-- This updates all items with NULL status to 'available'

-- First, check current state
SELECT
    id,
    name,
    status,
    is_available
FROM menu_items
ORDER BY id;

-- Update all items with NULL status to 'available'
UPDATE menu_items
SET status = 'available'
WHERE status IS NULL OR status = '';

-- Update items where is_available is false to have status 'unavailable'
UPDATE menu_items
SET status = 'unavailable'
WHERE is_available = false;

-- Set default value for future inserts
ALTER TABLE menu_items
ALTER COLUMN status SET DEFAULT 'available';

-- Verify the fix
SELECT
    id,
    name,
    status,
    is_available,
    price
FROM menu_items
ORDER BY category_id, name;

-- Check count by status
SELECT
    status,
    COUNT(*) as count
FROM menu_items
GROUP BY status;
