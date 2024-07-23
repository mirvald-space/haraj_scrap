import asyncio
import logging
from typing import List, Optional

from fastapi import BackgroundTasks, HTTPException

from config import settings
from db.database import count_posts, find, get_latest_posts
from utils.services import (
    get_city_key,
    get_post_service,
    parse_and_store_posts,
    search_posts_service,
    update_all_collections,
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def search_posts_handler(query: str, city: Optional[str], page: int, limit: int, background_tasks: BackgroundTasks):
    try:
        collection_name = f"posts_{query.replace(' ', '_').lower()}"
        if city:
            city_key = get_city_key(city)
            city_translation = settings.CITY_TRANSLATIONS.get(
                city_key, city_key)
            collection_name += f"_{city_translation}"

        skip = (page - 1) * limit

        async def get_exact_posts():
            while True:
                posts = await find(collection_name, {'_id': {'$ne': 'last_update'}}, [("postDate", -1)], skip, limit)
                if len(posts) >= limit:
                    return posts[:limit]

                if not background_tasks.tasks:
                    logger.info(
                        "Not enough posts found in database, starting parsing process...")
                    parsing_task = asyncio.create_task(
                        parse_and_store_posts(query, city))
                    background_tasks.add_task(lambda: parsing_task)

                # Небольшая пауза перед следующей проверкой
                await asyncio.sleep(0.5)

        # Устанавливаем таймаут в 30 секунд
        return await asyncio.wait_for(get_exact_posts(), timeout=30.0)

    except asyncio.TimeoutError:
        logger.warning(f"Timeout reached while waiting for {limit} posts")
        raise HTTPException(status_code=504, detail=f"Timeout while fetching {
                            limit} posts. Try a smaller limit or try again later.")
    except Exception as e:
        logger.exception(f"Error in search_posts_handler: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")

    except Exception as e:
        logger.exception(f"Error in search_posts_handler: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


async def get_post_handler(post_id: str):
    post = await get_post_service(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# handler for updating the database


async def update_database_handler():
    try:
        await update_all_collections()
        return {"message": "Database update completed successfully"}
    except Exception as e:
        logger.exception(f"Error in update_database_handler: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error updating database: {str(e)}")
