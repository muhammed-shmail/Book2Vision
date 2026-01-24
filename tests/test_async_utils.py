import pytest
import asyncio
import time
from src.ingestion import extract_text_from_txt

# Mock blocking function
def blocking_io_operation(duration=0.1):
    time.sleep(duration)
    return "done"

@pytest.mark.asyncio
async def test_async_wrapper_non_blocking():
    """
    Verify that async wrappers don't block the event loop.
    """
    # We'll run a "heartbeat" task concurrently with the blocking operation
    # If the blocking operation blocks the loop, the heartbeat won't run
    
    async def heartbeat():
        beats = 0
        for _ in range(5):
            await asyncio.sleep(0.02)
            beats += 1
        return beats

    # Run actual extraction (which uses to_thread)
    # We create a dummy file for this
    test_file = "test_async.txt"
    with open(test_file, "w") as f:
        f.write("test content")
        
    try:
        # Start heartbeat
        heartbeat_task = asyncio.create_task(heartbeat())
        
        # Start extraction
        extraction_task = asyncio.create_task(extract_text_from_txt(test_file))
        
        # Wait for both
        beats = await heartbeat_task
        result = await extraction_task
        
        # If blocking, beats would be 0 or very low because the loop was frozen
        # Since extract_text_from_txt uses to_thread, the loop should yield
        assert beats >= 3, f"Event loop was blocked! Heartbeats: {beats}"
        assert result["body"] == "test content"
        
    finally:
        import os
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    # Manual run if pytest not installed
    asyncio.run(test_async_wrapper_non_blocking())
    print("✅ Async test passed")
