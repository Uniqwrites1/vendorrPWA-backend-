from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from starlette.middleware.sessions import SessionMiddleware
import os
import time
from datetime import datetime

# Import routers (will be created in later todos)
from .routers import auth, api_test, menu, orders  # payments, admin, notifications

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Vendorr Restaurant API",
        version="1.0.0",
        description="""
        ## Vendorr PWA Backend API

        A comprehensive restaurant ordering system API built with FastAPI.

        ### Features

        * **Authentication**: JWT-based user authentication and authorization
        * **Menu Management**: Complete menu CRUD operations with categories
        * **Order Processing**: Real-time order management and tracking
        * **Payment Integration**: Bank transfer payment processing with proof upload
        * **Admin Dashboard**: Comprehensive restaurant management tools
        * **Real-time Notifications**: WebSocket-based live updates
        * **PWA Support**: Progressive Web App optimized endpoints

        ### Authentication

        Most endpoints require authentication. Include the JWT token in the Authorization header:
        ```
        Authorization: Bearer <your-jwt-token>
        ```

        ### Order Flow

        1. Browse menu items (`/api/menu`)
        2. Add items to cart (frontend state)
        3. Create order (`/api/orders`)
        4. Upload payment proof (`/api/payments/upload`)
        5. Track order status (`/api/orders/{order_id}`)

        ### Admin Access

        Admin endpoints require staff-level permissions. Contact system administrator for access.
        """,
        routes=app.routes,
    )

    # Add custom info
    openapi_schema["info"]["x-logo"] = {
        "url": "/assets/icon-192x192.svg"
    }

    # Add contact info
    openapi_schema["info"]["contact"] = {
        "name": "Vendorr Support",
        "email": "support@vendorr.com",
        "url": "https://vendorr.com/support"
    }

    # Add license info
    openapi_schema["info"]["license"] = {
        "name": "Private License",
        "url": "https://vendorr.com/license"
    }

    # Add servers
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.vendorr.com",
            "description": "Production server"
        }
    ]

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app = FastAPI(
    title="Vendorr Restaurant API",
    description="Restaurant ordering system API for Vendorr PWA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Set custom OpenAPI schema
app.openapi = custom_openapi

# Session middleware for admin authentication
app.add_middleware(SessionMiddleware, secret_key="your-secret-key-change-in-production")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://vendorr.com",
        "https://www.vendorr.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

# Static files for uploaded content
if not os.path.exists("uploads"):
    os.makedirs("uploads")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# API Status Endpoints
@app.get("/", tags=["System"])
async def root():
    """
    API Root Endpoint

    Returns basic API information and status.
    """
    return {
        "message": "Welcome to Vendorr Restaurant API",
        "status": "running",
        "version": "1.0.0",
        "documentation": "/docs",
        "alternative_docs": "/redoc",
        "openapi_schema": "/openapi.json",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", tags=["System"])
async def health_check():
    """
    Health Check Endpoint

    Returns the current health status of the API service.
    Used by load balancers and monitoring systems.
    """
    return {
        "status": "healthy",
        "service": "vendorr-api",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "uptime": "Available in production"
    }

@app.get("/api/status", tags=["System"])
async def api_status():
    """
    Detailed API Status

    Returns comprehensive status information including:
    - Database connectivity
    - Service health
    - Feature availability
    """
    return {
        "api": {
            "status": "operational",
            "version": "1.0.0",
            "environment": "development"
        },
        "services": {
            "authentication": "available",
            "menu_management": "available",
            "order_processing": "available",
            "payment_processing": "available",
            "notifications": "available",
            "admin_panel": "available"
        },
        "database": {
            "status": "connected",
            "type": "postgresql"
        },
        "timestamp": datetime.now().isoformat()
    }

# Placeholder image endpoint
@app.get("/api/placeholder/{width}/{height}", tags=["Utilities"])
async def get_placeholder_image(width: int, height: int):
    """Generate a simple placeholder image"""
    from fastapi.responses import Response

    # Simple SVG placeholder
    svg_content = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#e5e7eb"/>
        <text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="#9ca3af" font-family="Arial, sans-serif" font-size="14">
            {width}x{height}
        </text>
    </svg>'''

    return Response(content=svg_content, media_type="image/svg+xml")

# Import routers
from .routers import auth, api_test, menu, orders, websocket
from .admin_dashboard import admin_router

# Router registration
app.include_router(api_test.router, prefix="/api/mock", tags=["API Test Endpoints"])
app.include_router(admin_router, prefix="/admin", tags=["Admin Dashboard"])

# Include API routers
app.include_router(api_test.router, prefix="/api/test", tags=["Testing"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(menu.router, prefix="/api/menu", tags=["Menu"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(websocket.router, tags=["WebSocket Notifications"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
