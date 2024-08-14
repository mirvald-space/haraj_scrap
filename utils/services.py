import asyncio
import logging
import math
import urllib
from datetime import datetime
from typing import Optional

import aiohttp

from config import settings
from db.database import Database

logger = logging.getLogger(__name__)


class PostService:
    @staticmethod
    async def fetch_page(session, search_query, city_key, page):
        variables = {
            'search': search_query,
            'page': page,
            'city': city_key
        }
        json_data = {
            'query': settings.SEARCH_QUERY,
            'variables': variables,
        }
        for _ in range(settings.MAX_RETRIES):
            try:
                async with session.post(settings.API_URL, json=json_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['data']['search']['items'], data['data']['search']['pageInfo']['hasNextPage']
                    logger.warning(f"Unexpected response status: {
                                   response.status}")
                    return [], False
            except Exception as e:
                logger.error(f"Request failed: {str(e)}")
                await asyncio.sleep(settings.RETRY_DELAY)
        raise Exception("Max retries exceeded")

    @staticmethod
    async def fetch_data_from_source(search_query: str, city: Optional[str] = None):
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT)) as session:
            page, all_items = 1, []
            city_key = PostService.get_city_key(city) if city else None
            semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_REQUESTS)
            while True:
                async with semaphore:
                    items, has_next_page = await PostService.fetch_page(session, search_query, city_key, page)
                all_items.extend(items)
                if not has_next_page:
                    break
                page += 1
            return all_items

    @staticmethod
    def get_city_key(city: str) -> str:
        decoded_city = urllib.parse.unquote(city)
        return next((arabic for arabic, english in settings.CITY_TRANSLATIONS.items()
                     if decoded_city.lower() == english.lower() or decoded_city == arabic), decoded_city)

    @staticmethod
    async def parse_and_store_posts(search_query: str, city: Optional[str] = None):
        try:
            items = await PostService.fetch_data_from_source(search_query, city)
            collection_name = f"posts_{search_query.replace(' ', '_').lower()}"
            if city:
                city_key = PostService.get_city_key(city)
                collection_name += f"_{
                    settings.CITY_TRANSLATIONS.get(city_key, city_key)}"
            for item in items:
                post_data = {
                    'URL': f"https://haraj.com.sa/en/{item['URL']}",
                    'bodyHTML': item['bodyHTML'],
                    'id': str(item['id']),
                    'city': item['city'],
                    'postDate': datetime.fromtimestamp(int(item['postDate'])),
                    'title': item['title'],
                    'updateDate': datetime.fromtimestamp(int(item['updateDate'])),
                    'firstImage': item['imagesList'][0] if item['imagesList'] else None,
                    'commentCount': item.get('commentCount', 0),
                    'tags': item.get('tags', []),
                    'authorUsername': item.get('authorUsername'),
                    'price': {
                        'formattedPrice': item.get('price', {}).get('formattedPrice')
                    } if item.get('price') else None
                }
                await Database.update_one(collection_name, {'id': post_data['id']}, {'$set': post_data}, upsert=True)
            await Database.update_one(collection_name, {'_id': 'last_update'}, {'$set': {'timestamp': datetime.utcnow()}}, upsert=True)
            logger.info(f"Database updated successfully: {
                        len(items)} items stored in {collection_name}")
        except Exception as e:
            logger.exception(f"Error updating database: {str(e)}")
            raise

    @staticmethod
    async def search_posts(query: str, city: Optional[str], page: int, limit: int):
        collection_name = f"posts_{query.replace(' ', '_').lower()}"
        if city:
            city_key = PostService.get_city_key(city)
            collection_name += f"_{
                settings.CITY_TRANSLATIONS.get(city_key, city_key)}"

        collections = await Database.list_collection_names()
        if collection_name not in collections or await Database.count_posts(collection_name) == 0:
            await PostService.parse_and_store_posts(query, city)
            await asyncio.sleep(5)

        skip = (page - 1) * limit
        posts = await Database.find(collection_name, {'_id': {'$ne': 'last_update'}}, [("postDate", -1)], skip, limit)
        total_count = await Database.count_posts(collection_name)

        return {
            "posts": posts,
            "is_complete": len(posts) >= limit,
            "total_count": total_count,
            "current_page": page,
            "total_pages": math.ceil(total_count / limit),
            "has_previous_page": page > 1,
            "has_next_page": page < math.ceil(total_count / limit),
            "message": "Data successfully retrieved." if posts else "No posts available for this page."
        }

    @staticmethod
    async def get_post(post_id: str):
        collections = await Database.list_collection_names()
        for collection_name in collections:
            if collection_name.startswith("posts_"):
                post = await Database.find_one(collection_name, {"id": post_id})
                if post:
                    return post
        return None

    @staticmethod
    async def update_all_collections():
        collections = await Database.list_collection_names()
        for collection_name in collections:
            if collection_name.startswith("posts_"):
                parts = collection_name.split('_')
                search_query = parts[1]
                city = parts[2] if len(parts) > 2 else None
                await PostService.parse_and_store_posts(search_query, city)
