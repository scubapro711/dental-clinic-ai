from .shared.redis_queue import RedisQueueManager

async def get_queue_manager():
    # This is a placeholder for a more complex dependency injection system
    queue_manager = RedisQueueManager()
    await queue_manager.initialize()
    try:
        yield queue_manager
    finally:
        await queue_manager.cleanup()

