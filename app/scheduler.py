import asyncio
import logging
from datetime import datetime, timedelta
from typing import List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.usecases.fii_scrape_usecase import FiiScrapeUseCase

logger = logging.getLogger(__name__)

class FiiBootstrap:
    
    def __init__(self):
        self.popular_fiis = [
            "BCRI11", "BPFF11", "CPTS11", "HFOF11", "KISU11",
            "MFII11", "MXRF11", "RBFF11", "RECR11", "VISC11",
            "VINO11", "VILG11", "HGRU11", "HGLG11", "XPML11",
            "KNRI11", "RBRR11", "IRDM11", "ALZR11", "BBFI11"
        ]
    
    async def initial_seed(self):
        try:
            logger.info("🌱 Starting initial database seed...")
            usecase = FiiScrapeUseCase()
            
            existing_fiis = await usecase.fii_repository.list()
            if len(existing_fiis) > 0:
                logger.info(f"📊 Database already has {len(existing_fiis)} FIIs, skipping initial seed")
                return
            
            # Add small delay to allow API to fully start
            await asyncio.sleep(5)
            
            try:
                scraped_fiis = await usecase.execute()
                logger.info(f"✅ Initial seed completed: {len(scraped_fiis)} FIIs added from gateway")
            except Exception as gateway_error:
                logger.warning(f"⚠️ Gateway failed, using popular FIIs fallback: {gateway_error}")
                scraped_fiis = await usecase.execute(tickers=self.popular_fiis)
                logger.info(f"✅ Initial seed completed with fallback: {len(scraped_fiis)} FIIs added")
            
        except Exception as e:
            logger.error(f"❌ Initial seed failed: {e}")


class FiiScheduler:
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
    
    async def scheduled_update(self):
        try:
            logger.info("🔄 Starting scheduled FII update...")
            usecase = FiiScrapeUseCase()
            
            existing_fiis = await usecase.fii_repository.list()
            existing_tickers = [fii.ticker for fii in existing_fiis]
            
            if not existing_tickers:
                logger.info("📊 No FIIs in database, running full scrape from gateway")
                bootstrap = FiiBootstrap()
                try:
                    scraped_fiis = await usecase.execute()
                    logger.info(f"✅ Full scrape completed: {len(scraped_fiis)} FIIs updated from gateway")
                except Exception as gateway_error:
                    logger.warning(f"⚠️ Gateway failed, using popular FIIs fallback: {gateway_error}")
                    scraped_fiis = await usecase.execute(tickers=bootstrap.popular_fiis)
                    logger.info(f"✅ Fallback scrape completed: {len(scraped_fiis)} FIIs updated")
            else:
                logger.info(f"📊 Updating {len(existing_tickers)} existing FIIs and discovering new ones")
                try:
                    scraped_fiis = await usecase.execute()
                    logger.info(f"✅ Scheduled update completed: {len(scraped_fiis)} FIIs updated from gateway")
                except Exception as gateway_error:
                    logger.warning(f"⚠️ Gateway failed, updating existing FIIs only: {gateway_error}")
                    scraped_fiis = await usecase.execute(tickers=existing_tickers)
                    logger.info(f"✅ Existing FIIs updated: {len(scraped_fiis)} FIIs")
            
        except Exception as e:
            logger.error(f"❌ Scheduled update failed: {e}")
    
    def start(self):
        self.scheduler.add_job(
            self.scheduled_update,
            trigger=IntervalTrigger(hours=8),
            id='fii_update',
            max_instances=1,
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("📅 FII Scheduler started - Updates every 8h")
    
    def stop(self):
        self.scheduler.shutdown()
        logger.info("📅 FII Scheduler stopped")


async def bootstrap_and_start_scheduler():
    bootstrap = FiiBootstrap()
    await bootstrap.initial_seed()
    
    scheduler = FiiScheduler()
    scheduler.start()
    return scheduler


fii_scheduler = FiiScheduler()
