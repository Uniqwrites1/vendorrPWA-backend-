"""
WebSocket router for real-time notifications
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException
from sqlalchemy.orm import Session
import logging

from ..core.database import get_db
from ..models.database_models import User, UserRole
from ..auth.auth import decode_access_token
from ..websockets import manager

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_websocket_user(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Verify WebSocket connection token and get user"""
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if not user_id:
            await websocket.close(code=1008, reason="Invalid token")
            return None

        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            await websocket.close(code=1008, reason="User not found")
            return None

        return user
    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        await websocket.close(code=1008, reason="Authentication failed")
        return None


@router.websocket("/ws/notifications")
async def websocket_notifications_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    WebSocket endpoint for customer notifications.
    Connect with: ws://localhost:8000/ws/notifications?token={jwt_token}
    """
    from ..core.database import SessionLocal
    user = None
    user_id = None
    is_admin = False

    try:
        # Verify token and get user (use DB session only for authentication)
        db = SessionLocal()
        try:
            payload = decode_access_token(token)
            user_id = payload.get("sub")

            if not user_id:
                await websocket.close(code=1008, reason="Invalid token")
                return

            user = db.query(User).filter(User.id == int(user_id)).first()
            if not user:
                await websocket.close(code=1008, reason="User not found")
                return

            # Store user info and close DB session
            user_id = user.id
            is_admin = user.role == UserRole.ADMIN
        finally:
            db.close()

        # Connect the WebSocket
        await manager.connect(websocket, user_id, is_admin=is_admin)

        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to notifications",
            "user_id": user_id,
            "is_admin": is_admin
        })

        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                # Handle ping/pong for keepalive
                if data == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket loop: {e}")
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id if user_id else 'unknown'}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if user_id:
            manager.disconnect(websocket, user_id, is_admin=is_admin)


@router.websocket("/ws/admin")
async def websocket_admin_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    WebSocket endpoint specifically for admin dashboard.
    Connect with: ws://localhost:8000/ws/admin?token={jwt_token}
    """
    from ..core.database import SessionLocal
    user_id = None

    try:
        # Verify token and get user (use DB session only for authentication)
        db = SessionLocal()
        try:
            payload = decode_access_token(token)
            user_id = payload.get("sub")

            if not user_id:
                await websocket.close(code=1008, reason="Invalid token")
                return

            user = db.query(User).filter(User.id == int(user_id)).first()
            if not user or user.role != UserRole.ADMIN:
                await websocket.close(code=1008, reason="Admin access required")
                return

            # Store user ID and close DB session
            user_id = user.id
        finally:
            db.close()

        # Connect the WebSocket as admin
        await manager.connect(websocket, user_id, is_admin=True)

        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to admin notifications",
            "user_id": user_id
        })

        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in admin WebSocket loop: {e}")
                break

    except WebSocketDisconnect:
        logger.info(f"Admin WebSocket disconnected for user {user_id if user_id else 'unknown'}")
    except Exception as e:
        logger.error(f"Admin WebSocket error: {e}")
    finally:
        if user_id:
            manager.disconnect(websocket, user_id, is_admin=True)


@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics (for debugging)"""
    return manager.get_connection_count()
