from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Query

from db.models import Post, PostDetail
from utils.decorators import handle_exceptions
from utils.handlers import get_post_handler, search_posts_handler

# Create an API router instance
router = APIRouter()

# Route for searching posts


@router.get("/search/", response_model=List[Post])
@handle_exceptions
async def search_posts(
    background_tasks: BackgroundTasks,  # Background tasks for asynchronous execution
    # Search query string, required with a minimum length of 1
    query: str = Query(..., min_length=1),
    city: Optional[str] = None,  # Optional city filter for search
    # Pagination page number, default is 1, must be >= 1
    page: int = Query(1, ge=1),
    # Limit on the number of results, default is 20, must be between 1 and 100
    limit: int = Query(20, ge=1, le=100)
):
    # Call the handler to perform the search and return the results
    return await search_posts_handler(query, city, page, limit, background_tasks)

# Route for fetching a specific post by ID


@router.get("/post/{post_id}", response_model=PostDetail)
@handle_exceptions
async def get_post(post_id: str):
    # Call the handler to get post details and return the result
    return await get_post_handler(post_id)
