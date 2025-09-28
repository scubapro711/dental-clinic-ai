import pytest
from unittest.mock import MagicMock, patch
from src.gateway.services.message_service import MessageService
import json

@pytest.fixture
def mock_redis():
    with patch('redis.from_url') as mock_from_url:
        mock_redis_instance = MagicMock()
        mock_from_url.return_value = mock_redis_instance
        yield mock_redis_instance

@pytest.mark.asyncio
async def test_process_message_async(mock_redis):
    service = MessageService()
    await service.initialize()

    test_message = {"test": "message"}
    mock_redis.zadd.return_value = 1

    message_id = await service.process_message_async(test_message)
    assert message_id is not None

    await service.cleanup()

@pytest.mark.asyncio
async def test_get_message_status(mock_redis):
    service = MessageService()
    await service.initialize()

    test_message_id = "test_id"
    completed_message = {"status": "completed"}
    processing_message = {"status": "processing"}
    failed_message = {"status": "failed"}

    # Test completed
    mock_redis.get.return_value = json.dumps(completed_message)
    status = await service.get_message_status(test_message_id)
    assert status == completed_message

    # Test processing
    mock_redis.get.return_value = None
    mock_redis.hget.return_value = json.dumps(processing_message)
    status = await service.get_message_status(test_message_id)
    assert status == processing_message

    # Test failed
    mock_redis.hget.side_effect = [None, json.dumps(failed_message)]
    status = await service.get_message_status(test_message_id)
    assert status == failed_message

    # Test not found
    mock_redis.hget.side_effect = [None, None]
    status = await service.get_message_status(test_message_id)
    assert status["status"] == "not_found"

    await service.cleanup()

@pytest.mark.asyncio
async def test_get_queue_stats(mock_redis):
    service = MessageService()
    await service.initialize()

    mock_redis.zcard.return_value = 5
    mock_redis.hlen.return_value = 2

    stats = await service.get_queue_stats()
    assert stats["pending"] == 5
    assert stats["processing"] == 2

    await service.cleanup()

