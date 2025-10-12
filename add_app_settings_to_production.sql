-- ============================================
-- Add App Settings Table to Production Database
-- Run this in Supabase SQL Editor
-- ============================================

-- Create App Settings Table
CREATE TABLE IF NOT EXISTS app_settings (
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

-- Insert default settings (only if table is empty)
INSERT INTO app_settings (whatsapp_link, whatsapp_enabled, restaurant_name, restaurant_phone, restaurant_email, restaurant_address)
SELECT
    'https://wa.me/qr/EKAYKJ7XOVOTP1',
    true,
    'Vendorr',
    '+234 906 455 4795, +234 916 492 3056',
    'vendorr1@gmail.com',
    'Red Brick, Faculty of Arts, University of Jos, Jos, Plateau State'
WHERE NOT EXISTS (SELECT 1 FROM app_settings);

-- Verify the settings were created
SELECT
    'App settings table created successfully!' as status,
    COUNT(*) as settings_count
FROM app_settings;
