import logging
from typing import Optional

from fastapi import HTTPException

from db.database import Database
from utils.services import PostService

logger = logging.getLogger(__name__)


async def search_posts_handler(query: str, city: Optional[str], page: int, limit: int):
    try:
        return await PostService.search_posts(query, city, page, limit)
    except Exception as e:
        logger.exception(f"Error in search_posts_handler: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def get_post_handler(post_id: str):
    post = await PostService.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


async def update_database_handler():
    try:
        await PostService.update_all_collections()
        return {"message": "Database update completed successfully"}
    except Exception as e:
        logger.exception(f"Error in update_database_handler: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error updating database: {str(e)}")
