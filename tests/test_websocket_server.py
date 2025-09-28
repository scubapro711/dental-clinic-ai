"""
Comprehensive Test Suite for WebSocket Server Foundation - Component 1.1
Aggressive testing protocol with 100% coverage requirements

Test Categories:
1. Connection establishment and management
2. Message sending and receiving
3. Concurrent connection handling (100+ clients)
4. Connection drop and recovery
5. Memory leak detection
6. Performance benchmarks
7. Error handling and edge cases
"""

import asyncio
import json
import pytest
import time
import psutil
import gc
from datetime import datetime, timedelta
from typing import List, Dict, Any
from unittest.mock import Mock, patch
from concurrent.futures import ThreadPoolExecutor

import websockets
from fastapi.testclient import TestClient
from fastapi import WebSocket

# Import the server components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'websocket'))

from server import app, manager, ConnectionManager, WebSocketConnection, WebSocketMessage

class TestWebSocketServer:
    """Test suite for WebSocket server foundation"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test"""
        # Reset manager state
        manager.active_connections.clear()
        manager.message_history.clear()
        manager.stats = {
            'total_connections': 0,
            'current_connections': 0,
            'messages_sent': 0,
            'messages_received': 0,
            'errors': 0
        }
        yield
        # Cleanup after test
        manager.active_connections.clear()
        manager.message_history.clear()
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_websocket(self):
        """Mock WebSocket for testing"""
        websocket = Mock(spec=WebSocket)
        websocket.headers = {'user-agent': 'test-client'}
        websocket.client = Mock()
        websocket.client.host = '127.0.0.1'
        
        # Make async methods properly awaitable
        async def mock_accept():
            pass
        async def mock_send_text(data):
            pass
        
        websocket.accept = mock_accept
        websocket.send_text = mock_send_text
        return websocket

class TestConnectionManagement(TestWebSocketServer):
    """Test connection establishment and management"""
    
    @pytest.mark.asyncio
    async def test_connect_new_client(self, mock_websocket):
        """Test connecting a new client"""
        # Act
        client_id = await manager.connect(mock_websocket)
        
        # Assert
        assert client_id is not None
        assert len(client_id) > 0
        assert client_id in manager.active_connections
        assert manager.stats['total_connections'] == 1
        assert manager.stats['current_connections'] == 1
    
    @pytest.mark.asyncio
    async def test_connect_with_predefined_id(self, mock_websocket):
        """Test connecting with predefined client ID"""
        # Arrange
        mock_websocket.accept = Mock()
        mock_websocket.send_text = Mock()
        predefined_id = "test-client-123"
        
        # Act
        client_id = await manager.connect(mock_websocket, predefined_id)
        
        # Assert
        assert client_id == predefined_id
        assert predefined_id in manager.active_connections
        connection = manager.active_connections[predefined_id]
        assert connection.client_id == predefined_id
        assert connection.websocket == mock_websocket
    
    @pytest.mark.asyncio
    async def test_disconnect_client(self, mock_websocket):
        """Test disconnecting a client"""
        # Arrange
        mock_websocket.accept = Mock()
        mock_websocket.send_text = Mock()
        client_id = await manager.connect(mock_websocket)
        
        # Act
        manager.disconnect(client_id)
        
        # Assert
        assert client_id not in manager.active_connections
        assert manager.stats['current_connections'] == 0
    
    @pytest.mark.asyncio
    async def test_disconnect_nonexistent_client(self):
        """Test disconnecting a non-existent client"""
        # Act & Assert (should not raise exception)
        manager.disconnect("nonexistent-client")
        assert manager.stats['current_connections'] == 0
    
    @pytest.mark.asyncio
    async def test_connection_metadata(self, mock_websocket):
        """Test connection metadata storage"""
        # Arrange
        mock_websocket.accept = Mock()
        mock_websocket.send_text = Mock()
        mock_websocket.headers = {'user-agent': 'Mozilla/5.0 Test Browser'}
        
        # Act
        client_id = await manager.connect(mock_websocket)
        
        # Assert
        connection = manager.active_connections[client_id]
        assert connection.user_agent == 'Mozilla/5.0 Test Browser'
        assert connection.ip_address == '127.0.0.1'
        assert isinstance(connection.connected_at, datetime)
        assert isinstance(connection.last_ping, datetime)
        assert connection.subscriptions == []

class TestMessageHandling(TestWebSocketServer):
    """Test message sending and receiving"""
    
    @pytest.mark.asyncio
    async def test_send_personal_message(self, mock_websocket):
        """Test sending message to specific client"""
        # Arrange
        mock_websocket.accept = Mock()
        mock_websocket.send_text = Mock()
        client_id = await manager.connect(mock_websocket)
        
        message = {
            'type': 'test_message',
            'payload': {'data': 'test_data'}
        }
        
        # Act
        result = await manager.send_personal_message(message, client_id)
        
        # Assert
        assert result is True
        assert manager.stats['messages_sent'] == 2  # 1 welcome + 1 test message
        mock_websocket.send_text.assert_called()
        
        # Check message format
        call_args = mock_websocket.send_text.call_args_list[-1][0][0]
        sent_message = json.loads(call_args)
        assert sent_message['type'] == 'test_message'
        assert sent_message['payload']['data'] == 'test_data'
        assert 'timestamp' in sent_message
        assert 'message_id' in sent_message
    
    @pytest.mark.asyncio
    async def test_send_message_to_nonexistent_client(self):
        """Test sending message to non-existent client"""
        # Arrange
        message = {'type': 'test', 'payload': {}}
        
        # Act
        result = await manager.send_personal_message(message, "nonexistent")
        
        # Assert
        assert result is False
    
    @pytest.mark.asyncio
    async def test_broadcast_message(self, mock_websocket):
        """Test broadcasting message to all clients"""
        # Arrange
        mock_websocket.accept = Mock()
        mock_websocket.send_text = Mock()
        
        # Connect multiple clients
        client_ids = []
        for i in range(3):
            ws = Mock(spec=WebSocket)
            ws.accept = Mock()
            ws.send_text = Mock()
            ws.headers = {'user-agent': f'test-client-{i}'}
            ws.client = Mock()
            ws.client.host = '127.0.0.1'
            
            client_id = await manager.connect(ws)
            client_ids.append(client_id)
        
        message = {
            'type': 'broadcast_test',
            'payload': {'message': 'hello_all'}
        }
        
        # Act
        sent_count = await manager.broadcast(message)
        
        # Assert
        assert sent_count == 3
        assert manager.stats['messages_sent'] == 6  # 3 welcome + 3 broadcast
    
    @pytest.mark.asyncio
    async def test_broadcast_with_exclusion(self, mock_websocket):
        """Test broadcasting with client exclusion"""
        # Arrange
        mock_websocket.accept = Mock()
        mock_websocket.send_text = Mock()
        
        # Connect multiple clients
        client_ids = []
        for i in range(3):
            ws = Mock(spec=WebSocket)
            ws.accept = Mock()
            ws.send_text = Mock()
            ws.headers = {'user-agent': f'test-client-{i}'}
            ws.client = Mock()
            ws.client.host = '127.0.0.1'
            
            client_id = await manager.connect(ws)
            client_ids.append(client_id)
        
        message = {
            'type': 'broadcast_test',
            'payload': {'message': 'hello_others'}
        }
        
        # Act
        sent_count = await manager.broadcast(message, exclude_client=client_ids[0])
        
        # Assert
        assert sent_count == 2  # Excluded one client
    
    @pytest.mark.asyncio
    async def test_handle_ping_message(self, mock_websocket):
        """Test handling ping message"""
        # Arrange
        mock_websocket.accept = Mock()
        mock_websocket.send_text = Mock()
        client_id = await manager.connect(mock_websocket)
        
        ping_message = json.dumps({
            'type': 'ping',
            'payload': {}
        })
        
        # Act
        await manager.handle_message(ping_message, client_id)
        
        # Assert
        assert manager.stats['messages_received'] == 1
        # Should have sent pong response
        call_args = mock_websocket.send_text.call_args_list[-1][0][0]
        response = json.loads(call_args)
        assert response['type'] == 'pong'
    
    @pytest.mark.asyncio
    async def test_handle_subscription_message(self, mock_websocket):
        """Test handling subscription message"""
        # Arrange
        mock_websocket.accept = Mock()
        mock_websocket.send_text = Mock()
        client_id = await manager.connect(mock_websocket)
        
        subscribe_message = json.dumps({
            'type': 'subscribe',
            'payload': {'channels': ['agent_status', 'appointments']}
        })
        
        # Act
        await manager.handle_message(subscribe_message, client_id)
        
        # Assert
        connection = manager.active_connections[client_id]
        assert 'agent_status' in connection.subscriptions
        assert 'appointments' in connection.subscriptions
    
    @pytest.mark.asyncio
    async def test_handle_invalid_json(self, mock_websocket):
        """Test handling invalid JSON message"""
        # Arrange
        mock_websocket.accept = Mock()
        mock_websocket.send_text = Mock()
        client_id = await manager.connect(mock_websocket)
        
        invalid_message = "invalid json {"
        
        # Act
        await manager.handle_message(invalid_message, client_id)
        
        # Assert
        # Should have sent error response
        call_args = mock_websocket.send_text.call_args_list[-1][0][0]
        response = json.loads(call_args)
        assert response['type'] == 'error'
        assert 'Invalid JSON' in response['payload']['message']

class TestConcurrentConnections(TestWebSocketServer):
    """Test concurrent connection handling"""
    
    @pytest.mark.asyncio
    async def test_100_concurrent_connections(self):
        """Test handling 100+ concurrent connections"""
        # Arrange
        connection_count = 150
        client_ids = []
        
        # Act
        for i in range(connection_count):
            ws = Mock(spec=WebSocket)
            ws.accept = Mock()
            ws.send_text = Mock()
            ws.headers = {'user-agent': f'test-client-{i}'}
            ws.client = Mock()
            ws.client.host = '127.0.0.1'
            
            client_id = await manager.connect(ws)
            client_ids.append(client_id)
        
        # Assert
        assert len(manager.active_connections) == connection_count
        assert manager.stats['current_connections'] == connection_count
        assert manager.stats['total_connections'] == connection_count
        
        # Test broadcast to all connections
        message = {'type': 'load_test', 'payload': {'test': True}}
        sent_count = await manager.broadcast(message)
        assert sent_count == connection_count
    
    @pytest.mark.asyncio
    async def test_concurrent_message_sending(self):
        """Test concurrent message sending performance"""
        # Arrange
        connection_count = 50
        message_count = 100
        
        # Connect clients
        client_ids = []
        for i in range(connection_count):
            ws = Mock(spec=WebSocket)
            ws.accept = Mock()
            ws.send_text = Mock()
            ws.headers = {'user-agent': f'test-client-{i}'}
            ws.client = Mock()
            ws.client.host = '127.0.0.1'
            
            client_id = await manager.connect(ws)
            client_ids.append(client_id)
        
        # Act - Send messages concurrently
        start_time = time.time()
        
        tasks = []
        for i in range(message_count):
            for client_id in client_ids:
                message = {
                    'type': 'performance_test',
                    'payload': {'message_id': i, 'client_id': client_id}
                }
                task = manager.send_personal_message(message, client_id)
                tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Assert
        total_messages = connection_count * message_count
        successful_sends = sum(1 for result in results if result)
        
        assert successful_sends == total_messages
        
        # Performance check - should handle messages quickly
        duration = end_time - start_time
        messages_per_second = total_messages / duration
        assert messages_per_second > 1000  # Should handle 1000+ messages per second

class TestPerformanceAndMemory(TestWebSocketServer):
    """Test performance benchmarks and memory leak detection"""
    
    @pytest.mark.asyncio
    async def test_message_latency(self, mock_websocket):
        """Test message sending latency"""
        # Arrange
        mock_websocket.accept = Mock()
        mock_websocket.send_text = Mock()
        client_id = await manager.connect(mock_websocket)
        
        message = {'type': 'latency_test', 'payload': {'data': 'x' * 1000}}
        
        # Act
        start_time = time.time()
        await manager.send_personal_message(message, client_id)
        end_time = time.time()
        
        # Assert
        latency_ms = (end_time - start_time) * 1000
        assert latency_ms < 100  # Should be under 100ms
    
    @pytest.mark.asyncio
    async def test_memory_usage_with_many_connections(self):
        """Test memory usage with many connections"""
        # Arrange
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        connection_count = 100
        client_ids = []
        
        # Act - Create many connections
        for i in range(connection_count):
            ws = Mock(spec=WebSocket)
            ws.accept = Mock()
            ws.send_text = Mock()
            ws.headers = {'user-agent': f'test-client-{i}'}
            ws.client = Mock()
            ws.client.host = '127.0.0.1'
            
            client_id = await manager.connect(ws)
            client_ids.append(client_id)
        
        peak_memory = process.memory_info().rss
        
        # Disconnect all
        for client_id in client_ids:
            manager.disconnect(client_id)
        
        # Force garbage collection
        gc.collect()
        await asyncio.sleep(0.1)  # Allow cleanup
        
        final_memory = process.memory_info().rss
        
        # Assert
        memory_per_connection = (peak_memory - initial_memory) / connection_count
        memory_leak = final_memory - initial_memory
        
        # Each connection should use reasonable memory (< 10KB)
        assert memory_per_connection < 10 * 1024
        
        # Memory leak should be minimal (< 1MB)
        assert memory_leak < 1024 * 1024
    
    @pytest.mark.asyncio
    async def test_message_history_management(self, mock_websocket):
        """Test message history size management"""
        # Arrange
        mock_websocket.accept = Mock()
        mock_websocket.send_text = Mock()
        client_id = await manager.connect(mock_websocket)
        
        # Act - Send many messages to fill history
        for i in range(1200):  # More than the 1000 limit
            message = {'type': 'history_test', 'payload': {'id': i}}
            await manager.send_personal_message(message, client_id)
        
        # Assert
        assert len(manager.message_history) == 1000  # Should be capped at 1000
        
        # Check that oldest messages were removed
        first_message = manager.message_history[0]
        assert first_message.payload['id'] >= 200  # First 200 should be removed

class TestErrorHandling(TestWebSocketServer):
    """Test error handling and edge cases"""
    
    @pytest.mark.asyncio
    async def test_websocket_disconnect_during_send(self, mock_websocket):
        """Test handling WebSocket disconnect during message send"""
        # Arrange
        mock_websocket.accept = Mock()
        mock_websocket.send_text = Mock(side_effect=Exception("Connection lost"))
        client_id = await manager.connect(mock_websocket)
        
        # Act
        result = await manager.send_personal_message(
            {'type': 'test', 'payload': {}}, 
            client_id
        )
        
        # Assert
        assert result is False
        assert manager.stats['errors'] > 0
    
    @pytest.mark.asyncio
    async def test_stale_connection_cleanup(self, mock_websocket):
        """Test cleanup of stale connections"""
        # Arrange
        mock_websocket.accept = Mock()
        mock_websocket.send_text = Mock()
        client_id = await manager.connect(mock_websocket)
        
        # Make connection appear stale
        connection = manager.active_connections[client_id]
        connection.last_ping = datetime.now() - timedelta(minutes=10)
        
        # Act
        cleaned_count = await manager.cleanup_stale_connections()
        
        # Assert
        assert cleaned_count == 1
        assert client_id not in manager.active_connections
    
    @pytest.mark.asyncio
    async def test_connection_with_invalid_headers(self):
        """Test connection with invalid or missing headers"""
        # Arrange
        ws = Mock(spec=WebSocket)
        ws.accept = Mock()
        ws.send_text = Mock()
        ws.headers = {}  # No headers
        ws.client = None  # No client info
        
        # Act
        client_id = await manager.connect(ws)
        
        # Assert
        assert client_id is not None
        connection = manager.active_connections[client_id]
        assert connection.user_agent is None
        assert connection.ip_address is None
    
    def test_stats_accuracy(self):
        """Test statistics accuracy"""
        # Test initial stats
        stats = manager.get_stats()
        assert stats['total_connections'] == 0
        assert stats['current_connections'] == 0
        assert stats['messages_sent'] == 0
        assert stats['messages_received'] == 0
        assert stats['errors'] == 0
        assert 'uptime_seconds' in stats
        assert 'active_clients' in stats
        assert 'message_history_size' in stats

class TestAPIEndpoints(TestWebSocketServer):
    """Test HTTP API endpoints"""
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'stats' in data
    
    def test_stats_endpoint(self, client):
        """Test statistics endpoint"""
        response = client.get("/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert 'total_connections' in data
        assert 'current_connections' in data
        assert 'messages_sent' in data
        assert 'messages_received' in data
        assert 'errors' in data
        assert 'uptime_seconds' in data

# Performance benchmarks
class TestPerformanceBenchmarks:
    """Performance benchmark tests"""
    
    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_connection_throughput(self):
        """Benchmark connection establishment throughput"""
        connection_count = 1000
        start_time = time.time()
        
        # Create connections
        for i in range(connection_count):
            ws = Mock(spec=WebSocket)
            ws.accept = Mock()
            ws.send_text = Mock()
            ws.headers = {'user-agent': f'benchmark-client-{i}'}
            ws.client = Mock()
            ws.client.host = '127.0.0.1'
            
            await manager.connect(ws)
        
        end_time = time.time()
        duration = end_time - start_time
        connections_per_second = connection_count / duration
        
        print(f"Connection throughput: {connections_per_second:.2f} connections/second")
        assert connections_per_second > 100  # Should handle 100+ connections per second
    
    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_message_throughput(self):
        """Benchmark message sending throughput"""
        # Setup
        ws = Mock(spec=WebSocket)
        ws.accept = Mock()
        ws.send_text = Mock()
        ws.headers = {'user-agent': 'benchmark-client'}
        ws.client = Mock()
        ws.client.host = '127.0.0.1'
        
        client_id = await manager.connect(ws)
        
        message_count = 10000
        message = {'type': 'benchmark', 'payload': {'data': 'test'}}
        
        start_time = time.time()
        
        # Send messages
        for i in range(message_count):
            await manager.send_personal_message(message, client_id)
        
        end_time = time.time()
        duration = end_time - start_time
        messages_per_second = message_count / duration
        
        print(f"Message throughput: {messages_per_second:.2f} messages/second")
        assert messages_per_second > 5000  # Should handle 5000+ messages per second

if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        __file__,
        "-v",
        "--cov=server",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-fail-under=100"
    ])
