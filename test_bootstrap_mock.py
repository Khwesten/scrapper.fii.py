#!/usr/bin/env python3

import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.scheduler import FiiBootstrap, FiiScheduler, bootstrap_and_start_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Mock the usecase to avoid DB connections
class MockFiiScrapeUseCase:
    def __init__(self):
        self.fii_repository = MockRepository()
    
    async def execute(self, tickers=None):
        print(f"🎭 MOCK: Executing scrape with tickers: {tickers}")
        if tickers:
            return [f"FII-{ticker}" for ticker in tickers[:3]]  # Return mock data
        else:
            return ["FII-MOCK1", "FII-MOCK2", "FII-MOCK3"]  # Return mock data

class MockRepository:
    def __init__(self):
        self.has_data = False
    
    async def list(self):
        if self.has_data:
            return ["EXISTING1", "EXISTING2"]
        return []  # Empty DB

# Monkey patch the import
import app.scheduler
import app.usecases.fii_scrape_usecase
app.usecases.fii_scrape_usecase.FiiScrapeUseCase = MockFiiScrapeUseCase

async def test_bootstrap_mock():
    """Test bootstrap with mocked dependencies"""
    print("=" * 60)
    print("🧪 Testing Bootstrap with Mock (No DB/Gateway)")
    print("=" * 60)
    
    print("\n1️⃣ Testing FiiBootstrap.initial_seed() - Empty DB")
    bootstrap = FiiBootstrap()
    await bootstrap.initial_seed()
    
    print("\n2️⃣ Testing FiiBootstrap.initial_seed() - With existing data")
    bootstrap2 = FiiBootstrap()
    # Mock that DB has data
    original_usecase = MockFiiScrapeUseCase
    class MockWithDataUseCase(MockFiiScrapeUseCase):
        def __init__(self):
            super().__init__()
            self.fii_repository.has_data = True
    
    app.usecases.fii_scrape_usecase.FiiScrapeUseCase = MockWithDataUseCase
    await bootstrap2.initial_seed()
    
    print("\n3️⃣ Testing FiiScheduler start/stop")
    scheduler = FiiScheduler()
    scheduler.start()
    await asyncio.sleep(1)  # Let it initialize
    scheduler.stop()
    
    print("\n4️⃣ Testing bootstrap_and_start_scheduler()")
    # Reset to empty DB
    app.usecases.fii_scrape_usecase.FiiScrapeUseCase = original_usecase
    
    scheduler = await bootstrap_and_start_scheduler()
    await asyncio.sleep(1)
    scheduler.stop()
    
    print("\n✅ All mock tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_bootstrap_mock())
