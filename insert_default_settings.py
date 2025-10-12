from app.core.database import SessionLocal
from app.models.database_models import AppSettings

db = SessionLocal()

# Check if settings already exist
existing = db.query(AppSettings).first()

if not existing:
    settings = AppSettings(
        whatsapp_link='https://wa.me/qr/EKAYKJ7XOVOTP1',
        whatsapp_enabled=True,
        restaurant_name='Vendorr',
        restaurant_phone='+234 906 455 4795, +234 916 492 3056',
        restaurant_email='vendorr1@gmail.com',
        restaurant_address='Red Brick, Faculty of Arts, University of Jos, Jos, Plateau State'
    )
    db.add(settings)
    db.commit()
    print('✅ Default settings inserted successfully')
else:
    print('ℹ️  Settings already exist in database')

db.close()
