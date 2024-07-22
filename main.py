import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI

from db.database import close_db, init_db
from utils.routes import router
from utils.services import update_all_collections

# Logging Setup
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the scheduler for periodic tasks
scheduler = AsyncIOScheduler()

# Context manager for application lifespan


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database connection...")
    await init_db()  # Establish database connection
    logger.info("Database connection initialized.")

    logger.info("Starting scheduler...")
    scheduler.start()  # Start the scheduler
    # Add a job to update all collections every hour
    scheduler.add_job(
        update_all_collections,
        IntervalTrigger(hours=1),
        id='periodic_update',
        replace_existing=True
    )
    logger.info("Scheduled task 'update_all_collections' to run every hour.")

    try:
        yield
    finally:
        # Shutdown
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()  # Shutdown the scheduler
        logger.info("Scheduler shut down.")

        logger.info("Closing database connection...")
        await close_db()  # Close database connection
        logger.info("Database connection closed.")

# Create FastAPI app with the custom lifespan context manager
app = FastAPI(lifespan=lifespan)
# Include the application routes from the router
app.include_router(router)

# Data update function with logging


async def update_all_collections():
    logger.info("Starting the data collection process...")
    try:
        # Logic for data update
        logger.info("Data collection process completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred during data collection: {e}")

if __name__ == "__main__":
    import signal
    import sys

    import uvicorn

    # Graceful shutdown handler
    def handle_exit(*args):
        logger.info("Shutting down gracefully...")
        sys.exit(0)

    # Register signal handlers for graceful shutdown
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, handle_exit)

    try:
        logger.info("Starting the script...")
        uvicorn.run(app, host="0.0.0.0", port=8000)  # Run the application
    except KeyboardInterrupt:
        handle_exit()
    finally:
        logger.info("Script has been stopped.")
