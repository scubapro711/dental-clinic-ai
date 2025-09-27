"""
Shared Components for the WebSocket Module

This module contains components that are shared between the `server` and
`agent_broadcaster` modules to prevent circular imports.

It defines the `ConnectionManager` class, which is now instantiated here and
imported by both the server and the broadcaster, breaking the dependency loop.
"""

import asyncio
import json
import logging
from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages active WebSocket connections and message broadcasting."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def subscribe(self, websocket: WebSocket):
        """Accepts a new connection and adds it to the active list."""
        await websocket.accept()
        self.active_connections.append(websocket)
        await websocket.send_json({"type": "connection_established", "message": "Welcome!"})
        print(f"New client subscribed. Total clients: {len(self.active_connections)}")

    async def unsubscribe(self, websocket: WebSocket):
        """Removes a connection from the active list."""
        self.active_connections.remove(websocket)
        print(f"Client unsubscribed. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Sends a JSON message to all active connections."""
        disconnected_clients = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except (WebSocketDisconnect, RuntimeError):
                disconnected_clients.append(connection)
        
        # Clean up disconnected clients
        for client in disconnected_clients:
            self.active_connections.remove(client)

# Instantiate a single, shared broadcaster instance
broadcaster = ConnectionManager()

