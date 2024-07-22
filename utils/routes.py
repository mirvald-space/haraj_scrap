from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Query

from db.models import Post, PostDetail
from utils.decorators import handle_exceptions
from utils.handlers import get_post_handler, search_posts_handler

# Create an API router instance
router = APIRouter()

# New root endpoint


@router.get("/")
@handle_exceptions
async def root():
    return {"message": "The server is running successfully"}

# Route for searching posts


@router.get("/search/", response_model=List[Post])
@handle_exceptions
async def search_posts(
    background_tasks: BackgroundTasks,
    query: str = Query(..., min_length=1),
    city: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    return await search_posts_handler(query, city, page, limit, background_tasks)

# Route for fetching a specific post by ID


@router.get("/post/{post_id}", response_model=PostDetail)
@handle_exceptions
async def get_post(post_id: str):
    return await get_post_handler(post_id)
