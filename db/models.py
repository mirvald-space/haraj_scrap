from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field


class Price(BaseModel):
    formattedPrice: Optional[str] = Field(
        None, description="Formatted price of the item")


class Post(BaseModel):
    id: Union[str, int]
    bodyHTML: str
    title: str
    URL: str
    city: str
    postDate: datetime
    updateDate: datetime
    firstImage: Optional[str] = None
    commentCount: int
    tags: Optional[List[str]] = None
    authorUsername: Optional[str] = None
    price: Optional[Price] = None


class PostDetail(Post):
    pass


class SearchResponse(BaseModel):
    posts: List[Post]
    is_complete: bool
    total_count: int
    current_page: int
    total_pages: int
    has_previous_page: bool
    has_next_page: bool
    message: str
