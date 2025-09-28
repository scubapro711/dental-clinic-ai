import pytest
from unittest.mock import MagicMock, patch
from src.shared.redis_queue import RedisQueueManager
import json

@pytest.fixture
def mock_redis():
    with patch('redis.from_url') as mock_from_url:
        mock_redis_instance = MagicMock()
        mock_from_url.return_value = mock_redis_instance
        yield mock_redis_instance

@pytest.mark.asyncio
async def test_enqueue_dequeue(mock_redis):
    queue_manager = RedisQueueManager()
    await queue_manager.initialize()

    test_queue = "test_queue"
    test_message = {"test": "message"}

    # Mock Redis zadd and zpopmin
    mock_redis.zadd.return_value = 1
    mock_redis.zpopmin.return_value = [(json.dumps({"data": test_message, "id": "test_id"}), 0)]

    message_id = await queue_manager.enqueue(test_queue, test_message)
    assert message_id is not None

    retrieved_message = await queue_manager.dequeue(test_queue)
    assert retrieved_message["data"] == test_message

    await queue_manager.cleanup()

@pytest.mark.asyncio
async def test_get_queue_stats(mock_redis):
    queue_manager = RedisQueueManager()
    await queue_manager.initialize()

    test_queue = "test_queue"
    mock_redis.zcard.return_value = 5
    mock_redis.hlen.return_value = 2

    stats = await queue_manager.get_queue_stats(test_queue)
    assert stats["pending"] == 5
    assert stats["processing"] == 2

    await queue_manager.cleanup()




@pytest.mark.asyncio
async def test_complete_message(mock_redis):
    queue_manager = RedisQueueManager()
    await queue_manager.initialize()

    test_queue = "test_queue"
    test_message_id = "test_id"
    processing_message = {"id": test_message_id, "data": {"test": "message"}}

    mock_redis.hget.return_value = json.dumps(processing_message)

    await queue_manager.complete_message(test_queue, test_message_id)

    mock_redis.setex.assert_called_once()
    mock_redis.hdel.assert_called_once_with(f"processing:{test_queue}", test_message_id)

    await queue_manager.cleanup()

@pytest.mark.asyncio
async def test_fail_message(mock_redis):
    queue_manager = RedisQueueManager()
    await queue_manager.initialize()

    test_queue = "test_queue"
    test_message_id = "test_id"
    processing_message = {"id": test_message_id, "data": {"test": "message"}}

    mock_redis.hget.return_value = json.dumps(processing_message)

    await queue_manager.fail_message(test_queue, test_message_id, "Test Error")

    mock_redis.hset.assert_called_once()
    mock_redis.hdel.assert_called_once_with(f"processing:{test_queue}", test_message_id)

    await queue_manager.cleanup()

