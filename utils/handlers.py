import asyncio
import logging
import traceback
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

        async def get_available_posts():
            while True:
                total_posts = await count_posts(query, city)
                posts = await find(collection_name, {'_id': {'$ne': 'last_update'}}, [("postDate", -1)], skip, limit)

                if posts or total_posts < limit:
                    return posts, total_posts

                if not background_tasks.tasks:
                    logger.info(
                        "Not enough posts found in database, starting parsing process...")
                    parsing_task = asyncio.create_task(
                        parse_and_store_posts(query, city))
                    background_tasks.add_task(lambda: parsing_task)

                await asyncio.sleep(0.5)

        posts, total_posts = await asyncio.wait_for(get_available_posts(), timeout=30.0)

        # Возвращаем список постов
        return posts

    except asyncio.TimeoutError:
        logger.warning(f"Timeout reached while waiting for posts")
        raise HTTPException(
            status_code=504, detail="Timeout while fetching posts. Try again later.")
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
