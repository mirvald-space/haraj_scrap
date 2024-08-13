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

        async def get_posts():
            return await find(collection_name, {'_id': {'$ne': 'last_update'}}, [("postDate", -1)], skip, limit)

        posts = await get_posts()
        total_count = await count_posts(collection_name)

        # Check if data is still being processed
        if not posts and total_count == 0:
            logger.debug("No posts found, waiting for data to be processed...")
            background_tasks.add_task(parse_and_store_posts, query, city)
            return None  # Indicate that data is being processed

        # Check if the requested page is beyond available data
        if skip >= total_count:
            return {
                "posts": [],
                "is_complete": True,
                "total_count": total_count,
                "has_next_page": False,
                "message": "No more posts available"
            }

        return {
            "posts": posts,
            "is_complete": len(posts) < limit,
            "total_count": total_count,
            "has_next_page": skip + len(posts) < total_count
        }

    except Exception as e:
        logger.exception(f"Error in search_posts_handler: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


async def continue_parsing(query: str, city: Optional[str], target_count: int):
    while True:
        initial_count = await count_posts(query, city)
        if initial_count >= target_count:
            break
        await parse_and_store_posts(query, city)
        new_count = await count_posts(query, city)
        if new_count <= initial_count:
            # If the number of posts has not increased, stop parsing
            break
        # Wait a minute for the next parsing attempt
        await asyncio.sleep(60)


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
