-- Create app_settings table for storing application configuration
CREATE TABLE IF NOT EXISTS app_settings (
    id SERIAL PRIMARY KEY,
    whatsapp_link VARCHAR(500) DEFAULT 'https://wa.me/qr/EKAYKJ7XOVOTP1',
    whatsapp_enabled BOOLEAN DEFAULT true,
    restaurant_name VARCHAR(200) DEFAULT 'Vendorr',
    restaurant_phone VARCHAR(50) DEFAULT '+234 906 455 4795',
    restaurant_email VARCHAR(200) DEFAULT 'vendorr1@gmail.com',
    restaurant_address TEXT DEFAULT 'Red Brick Faculty of Arts University of Jos',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_app_settings_updated_at BEFORE UPDATE
    ON app_settings FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert default settings if table is empty
INSERT INTO app_settings (
    whatsapp_link,
    whatsapp_enabled,
    restaurant_name,
    restaurant_phone,
    restaurant_email,
    restaurant_address
)
SELECT
    'https://wa.me/qr/EKAYKJ7XOVOTP1',
    true,
    'Vendorr',
    '+234 906 455 4795, +234 916 492 3056',
    'vendorr1@gmail.com',
    'Red Brick Faculty of Arts University of Jos'
WHERE NOT EXISTS (SELECT 1 FROM app_settings);

-- Grant appropriate permissions
GRANT SELECT, INSERT, UPDATE ON app_settings TO authenticated;
GRANT SELECT, INSERT, UPDATE ON app_settings TO anon;

-- Comment on table and columns
COMMENT ON TABLE app_settings IS 'Application-wide configuration settings';
COMMENT ON COLUMN app_settings.whatsapp_link IS 'WhatsApp business link for floating button';
COMMENT ON COLUMN app_settings.whatsapp_enabled IS 'Toggle to show/hide WhatsApp button';
COMMENT ON COLUMN app_settings.restaurant_name IS 'Restaurant business name';
COMMENT ON COLUMN app_settings.restaurant_phone IS 'Restaurant contact phone number(s)';
COMMENT ON COLUMN app_settings.restaurant_email IS 'Restaurant contact email';
COMMENT ON COLUMN app_settings.restaurant_address IS 'Restaurant physical address';
