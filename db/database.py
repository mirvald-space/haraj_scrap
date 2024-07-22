from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient

from config import settings

# Global variables for MongoDB client and database
client = None
db = None

# Initialize the database connection


async def init_db():
    global client, db
    # Create a new MongoDB client
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    # Select the database
    db = client[settings.DB_NAME]

# Close the database connection


async def close_db():
    global client
    if client:
        # Close the MongoDB client connection
        client.close()

# Get a specific collection from the database


async def get_collection(name):
    return db[name]

# Update a single document in the collection


async def update_one(collection_name, filter, update, upsert=False):
    collection = await get_collection(collection_name)
    # Update a document in the collection with the specified filter and update
    return await collection.update_one(filter, update, upsert=upsert)

# Find documents in the collection with optional sorting, skipping, and limiting


async def find(collection_name, filter={}, sort=None, skip=0, limit=0):
    collection = await get_collection(collection_name)
    cursor = collection.find(filter)
    if sort:
        cursor = cursor.sort(sort)
    if skip:
        cursor = cursor.skip(skip)
    if limit:
        cursor = cursor.limit(limit)
    # Convert the cursor to a list with the specified limit
    return await cursor.to_list(length=limit)

# Find a single document in the collection


async def find_one(collection_name, filter):
    collection = await get_collection(collection_name)
    # Find one document that matches the filter
    return await collection.find_one(filter)

# List all collection names in the database


async def list_collection_names():
    return await db.list_collection_names()

# Count the number of posts matching the query and optional city


async def count_posts(query: str, city: Optional[str]):
    collection = await get_collection('posts')
    filter = {'query': query}
    if city:
        filter['city'] = city
    # Count the number of documents that match the filter
    return await collection.count_documents(filter)

# Get the latest posts sorted by post date


async def get_latest_posts(limit: int):
    collection = await get_collection('posts')
    # Find the latest posts sorted by post date in descending order
    cursor = collection.find().sort([('postDate', -1)]).limit(limit)
    # Convert the cursor to a list with the specified limit
    return await cursor.to_list(length=limit)
