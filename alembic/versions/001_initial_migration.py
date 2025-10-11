"""
First migration for Vendorr database - Complete schema

Revision ID: 001
Revises:
Create Date: 2025-09-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create enums
    user_role_enum = postgresql.ENUM('customer', 'kitchen_staff', 'counter_staff', 'manager', 'admin', name='userrole')
    user_role_enum.create(op.get_bind())

    order_status_enum = postgresql.ENUM('pending_payment', 'payment_confirmed', 'preparing', 'almost_ready', 'ready_for_pickup', 'completed', 'cancelled', name='orderstatus')
    order_status_enum.create(op.get_bind())

    payment_status_enum = postgresql.ENUM('pending', 'confirmed', 'rejected', name='paymentstatus')
    payment_status_enum.create(op.get_bind())

    menu_item_status_enum = postgresql.ENUM('available', 'unavailable', 'out_of_stock', name='menuitemstatus')
    menu_item_status_enum.create(op.get_bind())

    # Users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, index=True, nullable=False),
        sa.Column('phone', sa.String(20), unique=True, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('role', user_role_enum, nullable=False, server_default='customer'),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('profile_image', sa.String(255)),
        sa.Column('google_id', sa.String(100)),
        sa.Column('facebook_id', sa.String(100)),
        sa.Column('dietary_preferences', sa.Text),
        sa.Column('notification_preferences', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('last_login', sa.DateTime(timezone=True))
    )

    # Menu Categories table
    op.create_table('menu_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('display_order', sa.Integer, server_default='0'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('icon', sa.String(100)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True))
    )

    # Menu Items table
    op.create_table('menu_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('price', sa.Float, nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('menu_categories.id'), nullable=False),
        sa.Column('image_url', sa.String(255)),
        sa.Column('thumbnail_url', sa.String(255)),
        sa.Column('calories', sa.Integer),
        sa.Column('ingredients', sa.Text),
        sa.Column('allergens', sa.Text),
        sa.Column('dietary_tags', sa.Text),
        sa.Column('spice_level', sa.Integer, server_default='0'),
        sa.Column('status', menu_item_status_enum, server_default='available'),
        sa.Column('prep_time_minutes', sa.Integer, server_default='15'),
        sa.Column('is_daily_special', sa.Boolean, server_default='false'),
        sa.Column('customization_options', sa.Text),
        sa.Column('popularity_score', sa.Float, server_default='0.0'),
        sa.Column('total_orders', sa.Integer, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True))
    )

    # Orders table
    op.create_table('orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('order_number', sa.String(20), unique=True, nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', order_status_enum, nullable=False, server_default='pending_payment'),
        sa.Column('order_type', sa.String(20), server_default='pickup'),
        sa.Column('subtotal', sa.Float, nullable=False),
        sa.Column('tax_amount', sa.Float, server_default='0.0'),
        sa.Column('discount_amount', sa.Float, server_default='0.0'),
        sa.Column('total_amount', sa.Float, nullable=False),
        sa.Column('estimated_prep_time', sa.Integer),
        sa.Column('scheduled_time', sa.DateTime(timezone=True)),
        sa.Column('ready_time', sa.DateTime(timezone=True)),
        sa.Column('pickup_time', sa.DateTime(timezone=True)),
        sa.Column('customer_name', sa.String(200)),
        sa.Column('customer_phone', sa.String(20)),
        sa.Column('customer_email', sa.String(255)),
        sa.Column('special_instructions', sa.Text),
        sa.Column('qr_code', sa.String(255)),
        sa.Column('promo_code', sa.String(50)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True))
    )

    # Order Items table
    op.create_table('order_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('orders.id'), nullable=False),
        sa.Column('menu_item_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('menu_items.id'), nullable=False),
        sa.Column('quantity', sa.Integer, nullable=False, server_default='1'),
        sa.Column('unit_price', sa.Float, nullable=False),
        sa.Column('total_price', sa.Float, nullable=False),
        sa.Column('customizations', sa.Text),
        sa.Column('special_instructions', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )

    # Payments table
    op.create_table('payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('orders.id'), nullable=False),
        sa.Column('amount', sa.Float, nullable=False),
        sa.Column('payment_method', sa.String(50), server_default='bank_transfer'),
        sa.Column('status', payment_status_enum, nullable=False, server_default='pending'),
        sa.Column('transfer_reference', sa.String(255)),
        sa.Column('proof_of_payment_url', sa.String(255)),
        sa.Column('bank_account_last_4', sa.String(4)),
        sa.Column('confirmed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('confirmation_notes', sa.Text),
        sa.Column('confirmed_at', sa.DateTime(timezone=True)),
        sa.Column('rejection_reason', sa.Text),
        sa.Column('rejected_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True))
    )

    # Notifications table
    op.create_table('notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('orders.id')),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('notification_type', sa.String(50), nullable=False),
        sa.Column('is_read', sa.Boolean, server_default='false'),
        sa.Column('is_push_sent', sa.Boolean, server_default='false'),
        sa.Column('push_sent_at', sa.DateTime(timezone=True)),
        sa.Column('metadata', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('read_at', sa.DateTime(timezone=True))
    )

    # Reviews table
    op.create_table('reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('menu_item_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('menu_items.id')),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('orders.id')),
        sa.Column('rating', sa.Integer, nullable=False),
        sa.Column('title', sa.String(255)),
        sa.Column('comment', sa.Text),
        sa.Column('photos', sa.Text),
        sa.Column('is_approved', sa.Boolean, server_default='true'),
        sa.Column('is_featured', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True))
    )

    # Staff Accounts table
    op.create_table('staff_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('employee_id', sa.String(50), unique=True),
        sa.Column('department', sa.String(100)),
        sa.Column('shift_start', sa.String(5)),
        sa.Column('shift_end', sa.String(5)),
        sa.Column('permissions', sa.Text),
        sa.Column('is_on_duty', sa.Boolean, server_default='false'),
        sa.Column('last_activity', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True))
    )

    # Create indexes for better performance
    op.create_index('idx_orders_status', 'orders', ['status'])
    op.create_index('idx_orders_created_at', 'orders', ['created_at'])
    op.create_index('idx_menu_items_category', 'menu_items', ['category_id'])
    op.create_index('idx_menu_items_status', 'menu_items', ['status'])
    op.create_index('idx_payments_status', 'payments', ['status'])
    op.create_index('idx_notifications_user_read', 'notifications', ['user_id', 'is_read'])

def downgrade():
    # Drop indexes
    op.drop_index('idx_notifications_user_read')
    op.drop_index('idx_payments_status')
    op.drop_index('idx_menu_items_status')
    op.drop_index('idx_menu_items_category')
    op.drop_index('idx_orders_created_at')
    op.drop_index('idx_orders_status')

    # Drop tables
    op.drop_table('staff_accounts')
    op.drop_table('reviews')
    op.drop_table('notifications')
    op.drop_table('payments')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('menu_items')
    op.drop_table('menu_categories')
    op.drop_table('users')

    # Drop enums
    op.execute('DROP TYPE menuitemstatus')
    op.execute('DROP TYPE paymentstatus')
    op.execute('DROP TYPE orderstatus')
    op.execute('DROP TYPE userrole')
