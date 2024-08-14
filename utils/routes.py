from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Query

from db.models import PostDetail, SearchResponse
from utils.handlers import (
    get_post_handler,
    search_posts_handler,
    update_database_handler,
)

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "The server is running successfully"}


@router.get("/search/", response_model=SearchResponse)
async def search_posts(
    query: str = Query(..., min_length=1),
    city: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    return await search_posts_handler(query, city, page, limit)


@router.get("/post/{post_id}", response_model=PostDetail)
async def get_post(post_id: str):
    return await get_post_handler(post_id)


@router.post("/update")
async def update_database(background_tasks: BackgroundTasks):
    background_tasks.add_task(update_database_handler)
    return {"message": "Database update initiated"}
