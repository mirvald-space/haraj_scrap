import logging
import signal
import sys
from contextlib import asynccontextmanager

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI

from config import settings
from db.database import Database
from utils.routes import router
from utils.services import PostService

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database connection...")
    await Database.connect()
    logger.info("Database connection initialized.")

    logger.info("Starting scheduler...")
    scheduler.start()
    scheduler.add_job(
        PostService.update_all_collections,
        IntervalTrigger(hours=1),
        id='periodic_update',
        replace_existing=True
    )
    logger.info("Scheduled task 'update_all_collections' to run every hour.")

    try:
        yield
    finally:
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()
        logger.info("Scheduler shut down.")

        logger.info("Closing database connection...")
        await Database.close()
        logger.info("Database connection closed.")

app = FastAPI(lifespan=lifespan)
app.include_router(router)


def signal_handler(sig, frame):
    logger.info("Received shutdown signal. Initiating graceful shutdown...")
    scheduler.shutdown(wait=False)
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        logger.info("Starting the Haraj Scraper Backend...")
        uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down...")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        logger.info("Application shutdown complete.")
