import asyncio
import aiohttp
import time
import os

BASE_URL = "http://localhost:8000"
CONCURRENT_UPLOADS = 5

async def upload_book(session, i):
    filename = f"stress_test_{i}.txt"
    content = f"This is stress test file number {i}. It checks if the server can handle multiple uploads without blocking."
    
    with open(filename, "w") as f:
        f.write(content)
        
    try:
        start = time.time()
        with open(filename, "rb") as f:
            data = aiohttp.FormData()
            data.add_field('file', f, filename=filename)
            
            async with session.post(f"{BASE_URL}/api/upload", data=data) as response:
                text = await response.text()
                duration = time.time() - start
                status = response.status
                print(f"Upload {i}: Status {status} in {duration:.2f}s")
                return status == 200
    except Exception as e:
        print(f"Upload {i} failed: {e}")
        return False
    finally:
        if os.path.exists(filename):
            os.remove(filename)

async def check_health(session):
    """Check if server is responsive during uploads"""
    start = time.time()
    async with session.get(f"{BASE_URL}/health") as response:
        await response.text()
        duration = time.time() - start
        print(f"❤️ Health Check: {duration:.2f}s")
        return duration < 1.0 # Should be fast

async def run_stress_test():
    print(f"🚀 Starting Stress Test with {CONCURRENT_UPLOADS} concurrent uploads...")
    
    async with aiohttp.ClientSession() as session:
        # Start uploads
        upload_tasks = [upload_book(session, i) for i in range(CONCURRENT_UPLOADS)]
        
        # Start health checks concurrently
        health_tasks = [check_health(session) for _ in range(3)]
        
        # Run everything
        results = await asyncio.gather(*upload_tasks, *health_tasks)
        
        uploads = results[:CONCURRENT_UPLOADS]
        healths = results[CONCURRENT_UPLOADS:]
        
        print("\n=== Results ===")
        print(f"Successful Uploads: {sum(uploads)}/{CONCURRENT_UPLOADS}")
        print(f"Responsive Health Checks: {sum(healths)}/{len(healths)}")
        
        if all(uploads) and all(healths):
            print("✅ STRESS TEST PASSED: Server remained responsive.")
        else:
            print("⚠️ STRESS TEST FAILED: Some requests failed or were slow.")

if __name__ == "__main__":
    asyncio.run(run_stress_test())
