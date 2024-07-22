import asyncio
import logging
import urllib.parse
from datetime import datetime, timedelta
from typing import List, Optional

import aiohttp

import config
from config import settings
from db.database import count_posts, find, find_one, list_collection_names, update_one

logger = logging.getLogger(__name__)

# Function to get the city key for translating city names


def get_city_key(city: str) -> str:
    decoded_city = urllib.parse.unquote(city)
    for arabic, english in settings.CITY_TRANSLATIONS.items():
        if decoded_city.lower() == english.lower() or decoded_city == arabic:
            return arabic
    return decoded_city

# Asynchronous function to fetch a page of search results from the API


async def fetch_page(session, search_query, city_key, page):
    variables = {
        'search': search_query,
        'page': page,
    }
    if city_key:
        variables['city'] = city_key

    json_data = {
        'query': settings.SEARCH_QUERY,
        'variables': variables,
    }

    retries = 0
    while retries < settings.MAX_RETRIES:
        try:
            # Send a POST request to the API with search parameters
            async with session.post(settings.API_URL, json=json_data) as response:
                if response.status == 200:
                    # Parse the JSON response
                    data = await response.json()
                    return data['data']['search']['items'], data['data']['search']['pageInfo']['hasNextPage']
                else:
                    logger.warning(f"Unexpected response status: {
                                   response.status}")
                    return [], False
        except Exception as e:
            retries += 1
            logger.error(
                f"Request failed ({retries}/{settings.MAX_RETRIES}): {str(e)}")
            if retries < settings.MAX_RETRIES:
                await asyncio.sleep(settings.RETRY_DELAY)
            else:
                raise

# Asynchronous function to fetch all data from the source with pagination


async def fetch_data_from_source(search_query: str, city: Optional[str] = None):
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT)) as session:
        page = 1
        has_next_page = True
        all_items = []
        city_key = get_city_key(city) if city else None

        semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_REQUESTS)
        tasks = []

        while has_next_page:
            async with semaphore:
                tasks.append(fetch_page(session, search_query, city_key, page))
                page += 1

            if len(tasks) >= settings.MAX_CONCURRENT_REQUESTS or not has_next_page:
                results = await asyncio.gather(*tasks)
                for items, next_page in results:
                    all_items.extend(items)
                    has_next_page = next_page

                tasks = []

        return all_items

# Asynchronous function to parse the fetched data and store it in the database


async def parse_and_store_posts(search_query: str, city: Optional[str] = None):
    try:
        items = await fetch_data_from_source(search_query, city)
        collection_name = f"posts_{search_query.replace(' ', '_').lower()}"
        if city:
            city_key = get_city_key(city)
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
                'firstImage': item['imagesList'][0] if item['imagesList'] else None
            }
            # Update the post data in the database, or insert if it doesn't exist
            await update_one(collection_name, {'id': post_data['id']}, {'$set': post_data}, upsert=True)

        # Update the last update timestamp in the database
        await update_one(collection_name, {'_id': 'last_update'}, {'$set': {'timestamp': datetime.utcnow()}}, upsert=True)
        logger.info(f"Database updated successfully: {len(items)} items")
    except Exception as e:
        logger.exception(f"Error updating database: {str(e)}")
        raise

# Asynchronous function to update the database with new posts


async def update_database(search_query: str, city: Optional[str] = None):
    await parse_and_store_posts(search_query, city)

# Asynchronous function to update all collections in the database


async def update_all_collections():
    collections = await list_collection_names()
    for collection_name in collections:
        if collection_name.startswith("posts_"):
            parts = collection_name.split('_')
            search_query = parts[1]
            city = None
            if len(parts) > 2:
                city = parts[2]
            await update_database(search_query, city)

# Service function to handle searching posts


async def search_posts_service(query: str, city: Optional[str], page: int, limit: int, background_tasks):
    try:
        logger.debug(f"Searching posts in service: query={
                     query}, city={city}, page={page}, limit={limit}")
        collection_name = f"posts_{query.replace(' ', '_').lower()}"
        if city:
            city_key = get_city_key(city)
            collection_name += f"_{
                settings.CITY_TRANSLATIONS.get(city_key, city_key)}"

        logger.debug(f"Collection name: {collection_name}")

        skip = (page - 1) * limit
        posts = await find(collection_name, {'_id': {'$ne': 'last_update'}}, [("postDate", -1)], skip, limit)

        if len(posts) >= limit:
            return posts

        logger.info(
            "Not enough posts found in database, starting parsing process...")
        background_tasks.add_task(parse_and_store_posts, query, city)

        while len(posts) < limit:
            await asyncio.sleep(1)
            posts = await find(collection_name, {'_id': {'$ne': 'last_update'}}, [("postDate", -1)], skip, limit)
            if len(posts) >= limit:
                return posts

        return posts
    except Exception as e:
        logger.exception(f"Error in search_posts_service: {str(e)}")
        raise

# Service function to handle fetching a specific post by ID


async def get_post_service(post_id: str):
    collections = await list_collection_names()
    for collection_name in collections:
        if collection_name.startswith("posts_"):
            post = await find_one(collection_name, {"id": post_id})
            if post:
                return post
    return None
