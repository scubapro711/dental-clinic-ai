import pytest
import asyncio

@pytest.fixture
async def my_fixture():
    await asyncio.sleep(0.01)
    return 42

@pytest.mark.asyncio
async def test_my_async_test(my_fixture):
    assert my_fixture == 42

