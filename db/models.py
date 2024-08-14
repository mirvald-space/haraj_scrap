from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field

# Base model for a post


class Price(BaseModel):
    formattedPrice: Optional[str] = Field(
        None, description="Formatted price of the item")


class Post(BaseModel):
    id: Union[str, int]  # ID can be either string or integer
    bodyHTML: str  # HTML content of the post
    title: str  # Title of the post
    URL: str  # URL of the post
    city: str  # City related to the post
    postDate: datetime  # Date when the post was created
    updateDate: datetime  # Date when the post was last updated
    firstImage: Optional[str] = None  # Optional field for the first image URL
    commentCount: int  # Number of comments on the post
    tags: Optional[List[str]] = None
    authorUsername: Optional[str] = None
    price: Optional[Price] = None
# Detailed model for a post extending the base Post model


class PostDetail(Post):
    bodyHTML: str  # HTML content of the post


class SearchResponse(BaseModel):
    posts: List[Post]
    is_complete: bool
    total_count: int
    current_page: int
    total_pages: int
    has_previous_page: bool
    has_next_page: bool
    message: str
