#!/usr/bin/env python3
"""
AI Agents Health Check Server
שרת בדיקת בריאות לסוכני הבינה המלאכותית

Simple HTTP server for health checks in Docker container.
"""

import asyncio
import json
import logging
from datetime import datetime
from aiohttp import web, web_request
import aiohttp_cors

logger = logging.getLogger(__name__)

class HealthCheckServer:
    """Simple health check server for AI Agents service"""
    
    def __init__(self, port: int = 8001):
        self.port = port
        self.app = None
        self.runner = None
        self.site = None
        self.start_time = datetime.now()
        
    async def health_handler(self, request: web_request.Request) -> web.Response:
        """Health check endpoint"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        health_data = {
            "status": "healthy",
            "service": "ai-agents",
            "uptime_seconds": uptime,
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0"
        }
        
        return web.json_response(health_data)
    
    async def status_handler(self, request: web_request.Request) -> web.Response:
        """Detailed status endpoint"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        status_data = {
            "service": "AI Agents Service",
            "status": "running",
            "uptime_seconds": uptime,
            "start_time": self.start_time.isoformat(),
            "current_time": datetime.now().isoformat(),
            "components": {
                "message_processor": "active",
                "redis_queue": "connected",
                "ai_engine": "crewai",
                "agents": ["receptionist", "scheduler", "confirmation"]
            }
        }
        
        return web.json_response(status_data)
    
    async def start(self):
        """Start the health check server"""
        try:
            # Create web application
            self.app = web.Application()
            
            # Add CORS support
            cors = aiohttp_cors.setup(self.app, defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                    allow_methods="*"
                )
            })
            
            # Add routes
            self.app.router.add_get('/health', self.health_handler)
            self.app.router.add_get('/status', self.status_handler)
            
            # Add CORS to all routes
            for route in list(self.app.router.routes()):
                cors.add(route)
            
            # Create runner and start server
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            self.site = web.TCPSite(self.runner, '0.0.0.0', self.port)
            await self.site.start()
            
            logger.info(f"Health check server started on port {self.port}")
            
        except Exception as e:
            logger.error(f"Error starting health check server: {e}")
            raise
    
    async def stop(self):
        """Stop the health check server"""
        try:
            if self.site:
                await self.site.stop()
            if self.runner:
                await self.runner.cleanup()
            
            logger.info("Health check server stopped")
            
        except Exception as e:
            logger.error(f"Error stopping health check server: {e}")

# Global health server instance
health_server = HealthCheckServer()

async def start_health_server():
    """Start the health check server"""
    await health_server.start()

async def stop_health_server():
    """Stop the health check server"""
    await health_server.stop()
