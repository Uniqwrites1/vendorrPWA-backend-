"""
WebSocket manager for real-time notifications
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time notifications"""

    def __init__(self):
        # Store active connections: {user_id: [websocket1, websocket2, ...]}
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # Store admin connections separately
        self.admin_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, user_id: int, is_admin: bool = False):
        """Accept a new WebSocket connection"""
        await websocket.accept()

        if is_admin:
            self.admin_connections.add(websocket)
            logger.info(f"Admin connected via WebSocket. Total admin connections: {len(self.admin_connections)}")
        else:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)
            logger.info(f"User {user_id} connected via WebSocket. Total user connections: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: int = None, is_admin: bool = False):
        """Remove a WebSocket connection"""
        if is_admin:
            self.admin_connections.discard(websocket)
            logger.info(f"Admin disconnected. Remaining admin connections: {len(self.admin_connections)}")
        elif user_id and user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
                logger.info(f"User {user_id} disconnected. Remaining connections: {len(self.active_connections[user_id])}")
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        """Send a message to a specific user (all their connections)"""
        if user_id in self.active_connections:
            message_json = json.dumps({
                **message,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Send to all connections for this user
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message_json)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
                    disconnected.append(connection)

            # Clean up disconnected connections
            for conn in disconnected:
                self.disconnect(conn, user_id)

    async def send_to_admins(self, message: dict):
        """Send a message to all admin connections"""
        if not self.admin_connections:
            return

        message_json = json.dumps({
            **message,
            "timestamp": datetime.utcnow().isoformat()
        })

        disconnected = []
        for connection in self.admin_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending message to admin: {e}")
                disconnected.append(connection)

        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn, is_admin=True)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected users"""
        message_json = json.dumps({
            **message,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Send to all user connections
        for user_id, connections in list(self.active_connections.items()):
            disconnected = []
            for connection in connections:
                try:
                    await connection.send_text(message_json)
                except Exception as e:
                    logger.error(f"Error broadcasting to user {user_id}: {e}")
                    disconnected.append(connection)

            # Clean up disconnected connections
            for conn in disconnected:
                self.disconnect(conn, user_id)

        # Send to all admin connections
        await self.send_to_admins(message)

    def get_connection_count(self) -> dict:
        """Get count of active connections"""
        return {
            "total_users": len(self.active_connections),
            "total_connections": sum(len(conns) for conns in self.active_connections.values()),
            "admin_connections": len(self.admin_connections)
        }


# Global connection manager instance
manager = ConnectionManager()


# Notification helper functions
async def notify_order_status_change(order_id: int, customer_id: int, new_status: str, order_number: str):
    """Notify customer about order status change"""
    status_messages = {
        "pending_payment": {
            "title": "Order Created",
            "message": f"Order {order_number} created. Please complete payment.",
            "type": "info"
        },
        "payment_confirmed": {
            "title": "Payment Confirmed",
            "message": f"Payment confirmed for order {order_number}. We're preparing your meal!",
            "type": "success"
        },
        "preparing": {
            "title": "Order Preparing",
            "message": f"Your order {order_number} is being prepared by our chefs.",
            "type": "info"
        },
        "almost_ready": {
            "title": "Almost Ready!",
            "message": f"Your order {order_number} is almost ready!",
            "type": "warning"
        },
        "ready_for_pickup": {
            "title": "Order Ready!",
            "message": f"Your order {order_number} is ready for pickup!",
            "type": "success"
        },
        "completed": {
            "title": "Order Completed",
            "message": f"Thank you! Order {order_number} has been completed.",
            "type": "success"
        },
        "cancelled": {
            "title": "Order Cancelled",
            "message": f"Order {order_number} has been cancelled.",
            "type": "error"
        }
    }

    notification = status_messages.get(new_status, {
        "title": "Order Update",
        "message": f"Order {order_number} status changed to {new_status}",
        "type": "info"
    })

    await manager.send_personal_message({
        **notification,
        "notification_type": "order_status",
        "data": {
            "order_id": order_id,
            "order_number": order_number,
            "status": new_status
        }
    }, customer_id)


async def notify_payment_status_change(order_id: int, customer_id: int, payment_status: str, order_number: str):
    """Notify customer about payment status change"""
    payment_messages = {
        "completed": {
            "title": "Payment Successful",
            "message": f"Payment for order {order_number} has been confirmed!",
            "type": "success"
        },
        "failed": {
            "title": "Payment Failed",
            "message": f"Payment for order {order_number} failed. Please try again.",
            "type": "error"
        },
        "refunded": {
            "title": "Payment Refunded",
            "message": f"Payment for order {order_number} has been refunded.",
            "type": "info"
        }
    }

    notification = payment_messages.get(payment_status, {
        "title": "Payment Update",
        "message": f"Payment status for order {order_number} changed to {payment_status}",
        "type": "info"
    })

    await manager.send_personal_message({
        **notification,
        "notification_type": "payment_status",
        "data": {
            "order_id": order_id,
            "order_number": order_number,
            "payment_status": payment_status
        }
    }, customer_id)


async def notify_admin_new_order(order_id: int, order_number: str, customer_name: str, total_amount: float):
    """Notify admin about new order"""
    await manager.send_to_admins({
        "title": "New Order Received",
        "message": f"New order {order_number} from {customer_name} - Total: R{total_amount:.2f}",
        "type": "info",
        "notification_type": "new_order",
        "data": {
            "order_id": order_id,
            "order_number": order_number,
            "customer_name": customer_name,
            "total_amount": total_amount
        }
    })


async def notify_admin_payment_uploaded(order_id: int, order_number: str, customer_name: str):
    """Notify admin about payment proof upload"""
    await manager.send_to_admins({
        "title": "Payment Proof Uploaded",
        "message": f"Customer {customer_name} uploaded payment proof for order {order_number}",
        "type": "warning",
        "notification_type": "payment_proof",
        "data": {
            "order_id": order_id,
            "order_number": order_number,
            "customer_name": customer_name
        }
    })
