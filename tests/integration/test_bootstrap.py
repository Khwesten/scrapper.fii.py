#!/usr/bin/env python3

import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.scheduler import FiiBootstrap, FiiScheduler, bootstrap_and_start_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

async def test_bootstrap_only():
    """Test only the bootstrap functionality"""
    print("=" * 60)
    print("🧪 Testing FiiBootstrap.initial_seed() only")
    print("=" * 60)
    
    bootstrap = FiiBootstrap()
    await bootstrap.initial_seed()
    print("✅ Bootstrap test completed")

async def test_scheduler_only():
    """Test only the scheduler functionality"""
    print("=" * 60)
    print("🧪 Testing FiiScheduler start/stop only")
    print("=" * 60)
    
    scheduler = FiiScheduler()
    scheduler.start()
    print("✅ Scheduler started")
    
    # Let it run for 2 seconds to see if it starts properly
    await asyncio.sleep(2)
    
    scheduler.stop()
    print("✅ Scheduler stopped")

async def test_full_bootstrap():
    """Test the full bootstrap_and_start_scheduler function"""
    print("=" * 60)
    print("🧪 Testing bootstrap_and_start_scheduler() function")
    print("=" * 60)
    
    scheduler = await bootstrap_and_start_scheduler()
    print("✅ Full bootstrap completed")
    
    # Let it run for 3 seconds
    await asyncio.sleep(3)
    
    scheduler.stop()
    print("✅ Full test completed")

async def main():
    print("🚀 Starting Bootstrap Tests")
    print("Choose test to run:")
    print("1. Bootstrap only")
    print("2. Scheduler only") 
    print("3. Full bootstrap")
    
    choice = input("Enter choice (1-3): ").strip()
    
    try:
        if choice == "1":
            await test_bootstrap_only()
        elif choice == "2":
            await test_scheduler_only()
        elif choice == "3":
            await test_full_bootstrap()
        else:
            print("❌ Invalid choice")
            return
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
