from fastapi import FastAPI
from fastapi_admin.app import app as admin_app
from fastapi_admin.enums import Method
from fastapi_admin.file_upload import FileUpload
from fastapi_admin.providers.login import UsernamePasswordProvider
from fastapi_admin.resources import Field, Link, Model, ToolbarAction
from tortoise.models import Model as TortoiseModel
from tortoise import fields
import os

# Admin configuration
ADMIN_SECRET_KEY = "your-secret-key-change-in-production"

# File upload configuration
upload = FileUpload(uploads_dir="uploads")

# Define Tortoise models for admin (these would match your actual database models)
class User(TortoiseModel):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=100, unique=True)
    first_name = fields.CharField(max_length=50)
    last_name = fields.CharField(max_length=50)
    role = fields.CharField(max_length=20, default="customer")
    is_active = fields.BooleanField(default=True)
    is_verified = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "users"

class MenuItem(TortoiseModel):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    description = fields.TextField()
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    category = fields.CharField(max_length=50)
    is_available = fields.BooleanField(default=True)
    image_url = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "menu_items"

class Order(TortoiseModel):
    id = fields.IntField(pk=True)
    user_id = fields.IntField()
    status = fields.CharField(max_length=20, default="pending")
    total_amount = fields.DecimalField(max_digits=10, decimal_places=2)
    payment_status = fields.CharField(max_length=20, default="pending")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "orders"

# Admin Resources Configuration
@admin_app.register
class UserResource(Model):
    label = "Users"
    model = User
    icon = "fas fa-users"
    page_pre_title = "User Management"
    page_title = "Users"
    filters = [
        Field(name="role", label="Role"),
        Field(name="is_active", label="Active"),
        Field(name="is_verified", label="Verified"),
    ]
    fields = [
        Field(name="id", label="ID"),
        Field(name="email", label="Email"),
        Field(name="first_name", label="First Name"),
        Field(name="last_name", label="Last Name"),
        Field(name="role", label="Role"),
        Field(name="is_active", label="Active"),
        Field(name="is_verified", label="Verified"),
        Field(name="created_at", label="Created At"),
    ]

@admin_app.register
class MenuItemResource(Model):
    label = "Menu Items"
    model = MenuItem
    icon = "fas fa-utensils"
    page_pre_title = "Menu Management"
    page_title = "Menu Items"
    filters = [
        Field(name="category", label="Category"),
        Field(name="is_available", label="Available"),
    ]
    fields = [
        Field(name="id", label="ID"),
        Field(name="name", label="Name"),
        Field(name="description", label="Description"),
        Field(name="price", label="Price"),
        Field(name="category", label="Category"),
        Field(name="is_available", label="Available"),
        Field(name="image_url", label="Image URL"),
        Field(name="created_at", label="Created At"),
    ]

@admin_app.register
class OrderResource(Model):
    label = "Orders"
    model = Order
    icon = "fas fa-shopping-cart"
    page_pre_title = "Order Management"
    page_title = "Orders"
    filters = [
        Field(name="status", label="Status"),
        Field(name="payment_status", label="Payment Status"),
    ]
    fields = [
        Field(name="id", label="ID"),
        Field(name="user_id", label="User ID"),
        Field(name="status", label="Status"),
        Field(name="total_amount", label="Total Amount"),
        Field(name="payment_status", label="Payment Status"),
        Field(name="created_at", label="Created At"),
    ]

# Login provider
@admin_app.register
class AdminLoginProvider(UsernamePasswordProvider):
    async def login(
        self,
        username: str,
        password: str,
    ) -> bool:
        # Simple hardcoded admin login (change this in production)
        if username == "admin" and password == "admin123":
            return True
        return False

    async def is_authenticated(self, request) -> bool:
        token = request.session.get("token")
        return token == "admin-authenticated"

    async def get_admin_user(self, request):
        return {
            "username": "admin",
            "avatar": "/static/admin-avatar.png"
        }

# Toolbar actions
@admin_app.register
class DashboardLink(Link):
    label = "Dashboard"
    icon = "fas fa-tachometer-alt"
    url = "/admin"

@admin_app.register
class APIDocsLink(Link):
    label = "API Documentation"
    icon = "fas fa-book"
    url = "/docs"
    target = "_blank"

# Initialize admin
def setup_admin():
    admin_app.add_admin_path("/admin")
    return admin_app
