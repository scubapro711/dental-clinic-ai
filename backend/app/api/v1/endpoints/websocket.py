"""
WebSocket endpoint for real-time monitoring and updates.

This module provides WebSocket connections for the Mission Control Dashboard
to receive real-time updates about conversations, agent status, and system events.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set, List
import asyncio
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections and broadcasts events."""

    def __init__(self):
        # Channel-based connections: {channel_name: {websocket1, websocket2, ...}}
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Conversation-specific subscriptions: {conversation_id: {websocket1, ...}}
        self.conversation_subscriptions: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str = "monitoring"):
        """Accept a new WebSocket connection and add it to a channel."""
        await websocket.accept()
        
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        
        self.active_connections[channel].add(websocket)
        logger.info(f"WebSocket connected to channel '{channel}'. Total connections: {len(self.active_connections[channel])}")

    def disconnect(self, websocket: WebSocket, channel: str = "monitoring"):
        """Remove a WebSocket connection from a channel."""
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
            logger.info(f"WebSocket disconnected from channel '{channel}'. Remaining: {len(self.active_connections[channel])}")
        
        # Also remove from any conversation subscriptions
        for conv_id in list(self.conversation_subscriptions.keys()):
            self.conversation_subscriptions[conv_id].discard(websocket)
            if not self.conversation_subscriptions[conv_id]:
                del self.conversation_subscriptions[conv_id]

    async def broadcast(self, message: dict, channel: str = "monitoring"):
        """Broadcast a message to all connections in a channel."""
        if channel not in self.active_connections:
            return
        
        # Add timestamp if not present
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()
        
        message_json = json.dumps(message)
        
        # Send to all active connections
        disconnected = []
        for connection in self.active_connections[channel]:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending message to WebSocket: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection, channel)

    async def send_personal(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()
        
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    def subscribe_conversation(self, websocket: WebSocket, conversation_id: str):
        """Subscribe a WebSocket to updates for a specific conversation."""
        if conversation_id not in self.conversation_subscriptions:
            self.conversation_subscriptions[conversation_id] = set()
        
        self.conversation_subscriptions[conversation_id].add(websocket)
        logger.info(f"WebSocket subscribed to conversation {conversation_id}")

    def unsubscribe_conversation(self, websocket: WebSocket, conversation_id: str):
        """Unsubscribe a WebSocket from a specific conversation."""
        if conversation_id in self.conversation_subscriptions:
            self.conversation_subscriptions[conversation_id].discard(websocket)
            if not self.conversation_subscriptions[conversation_id]:
                del self.conversation_subscriptions[conversation_id]
            logger.info(f"WebSocket unsubscribed from conversation {conversation_id}")

    async def broadcast_to_conversation(self, message: dict, conversation_id: str):
        """Broadcast a message to all subscribers of a specific conversation."""
        if conversation_id not in self.conversation_subscriptions:
            return
        
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()
        
        message_json = json.dumps(message)
        
        disconnected = []
        for connection in self.conversation_subscriptions[conversation_id]:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending conversation message: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.unsubscribe_conversation(connection, conversation_id)


# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/ws/monitoring")
async def websocket_monitoring(websocket: WebSocket):
    """
    WebSocket endpoint for real-time monitoring.
    
    Clients connect to this endpoint to receive real-time updates about:
    - New conversations
    - Conversation updates
    - New messages
    - Escalations
    - Agent status changes
    - Metrics updates
    - System errors
    """
    await manager.connect(websocket, "monitoring")
    
    try:
        # Send welcome message
        await manager.send_personal({
            "type": "connected",
            "message": "Connected to monitoring channel",
            "channels": ["monitoring"]
        }, websocket)
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                event_type = message.get("type")
                
                # Handle different message types
                if event_type == "subscribe":
                    channel = message.get("channel", "monitoring")
                    await manager.connect(websocket, channel)
                    await manager.send_personal({
                        "type": "subscribed",
                        "channel": channel
                    }, websocket)
                
                elif event_type == "subscribe_conversation":
                    conversation_id = message.get("conversation_id")
                    if conversation_id:
                        manager.subscribe_conversation(websocket, conversation_id)
                        await manager.send_personal({
                            "type": "conversation_subscribed",
                            "conversation_id": conversation_id
                        }, websocket)
                
                elif event_type == "unsubscribe_conversation":
                    conversation_id = message.get("conversation_id")
                    if conversation_id:
                        manager.unsubscribe_conversation(websocket, conversation_id)
                        await manager.send_personal({
                            "type": "conversation_unsubscribed",
                            "conversation_id": conversation_id
                        }, websocket)
                
                elif event_type == "ping":
                    await manager.send_personal({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                
                else:
                    logger.warning(f"Unknown message type: {event_type}")
            
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received: {data}")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, "monitoring")
        logger.info("WebSocket disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, "monitoring")


# Helper functions to emit events from other parts of the application

async def emit_conversation_new(conversation: dict):
    """Emit event when a new conversation is created."""
    await manager.broadcast({
        "type": "conversation_new",
        "conversation": conversation
    }, "monitoring")


async def emit_conversation_update(conversation_id: str, updates: dict):
    """Emit event when a conversation is updated."""
    message = {
        "type": "conversation_update",
        "conversation_id": conversation_id,
        "updates": updates
    }
    
    # Broadcast to monitoring channel
    await manager.broadcast(message, "monitoring")
    
    # Also broadcast to conversation-specific subscribers
    await manager.broadcast_to_conversation(message, conversation_id)


async def emit_message_new(conversation_id: str, message_data: dict):
    """Emit event when a new message is sent."""
    message = {
        "type": "message_new",
        "conversation_id": conversation_id,
        "message": message_data
    }
    
    await manager.broadcast(message, "monitoring")
    await manager.broadcast_to_conversation(message, conversation_id)


async def emit_escalation(conversation_id: str, escalation_level: str, reason: str):
    """Emit event when an escalation occurs."""
    message = {
        "type": "escalation",
        "conversation_id": conversation_id,
        "escalation_level": escalation_level,
        "reason": reason
    }
    
    await manager.broadcast(message, "monitoring")
    await manager.broadcast_to_conversation(message, conversation_id)


async def emit_agent_status(status: dict):
    """Emit event when agent status changes."""
    await manager.broadcast({
        "type": "agent_status",
        "status": status
    }, "monitoring")


async def emit_metrics_update(metrics: dict):
    """Emit event when metrics are updated."""
    await manager.broadcast({
        "type": "metrics_update",
        "metrics": metrics
    }, "monitoring")


async def emit_error(error_message: str, error_type: str = "system"):
    """Emit event when an error occurs."""
    await manager.broadcast({
        "type": "error",
        "error_type": error_type,
        "message": error_message
    }, "monitoring")
