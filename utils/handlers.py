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
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def search_posts_handler(query: str, city: Optional[str], page: int, limit: int, background_tasks: BackgroundTasks):
    try:
        # logger.debug(f"Searching posts: query={query}, city={
        #              city}, page={page}, limit={limit}")

        collection_name = f"posts_{query.replace(' ', '_').lower()}"
        if city:
            city_key = get_city_key(city)
            city_translation = settings.CITY_TRANSLATIONS.get(
                city_key, city_key)
            collection_name += f"_{city_translation}"

        skip = (page - 1) * limit
        posts = await find(collection_name, {'_id': {'$ne': 'last_update'}}, [("postDate", -1)], skip, limit)

        if len(posts) >= limit:
            return posts

        logger.info(
            "Not enough posts found in database, starting parsing process...")
        parsing_task = asyncio.create_task(parse_and_store_posts(query, city))
        background_tasks.add_task(lambda: parsing_task)

        async def check_posts():
            # Minimum of 10 posts or the requested number if less than 10
            min_posts = min(10, limit)
            while len(posts) < limit:
                await asyncio.sleep(0.5)
                new_posts = await find(collection_name, {'_id': {'$ne': 'last_update'}}, [("postDate", -1)], skip, limit)
                if len(new_posts) >= min_posts:
                    return new_posts
            return posts

        # Set timeout
        return await asyncio.wait_for(check_posts(), timeout=10.0)

    except asyncio.TimeoutError:
        logger.warning("Timeout reached while waiting for posts")
        return posts  # Retrieve what we can find
    except Exception as e:
        logger.exception(f"Error in search_posts_handler: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


async def get_post_handler(post_id: str):
    post = await get_post_service(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post
