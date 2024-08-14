from motor.motor_asyncio import AsyncIOMotorClient

from config import settings


class Database:
    client = None
    db = None

    @classmethod
    async def connect(cls):
        cls.client = AsyncIOMotorClient(settings.MONGODB_URI)
        cls.db = cls.client[settings.DB_NAME]

    @classmethod
    async def close(cls):
        if cls.client:
            cls.client.close()

    @classmethod
    async def get_collection(cls, name):
        return cls.db[name]

    @classmethod
    async def update_one(cls, collection_name, filter, update, upsert=False):
        collection = await cls.get_collection(collection_name)
        return await collection.update_one(filter, update, upsert=upsert)

    @classmethod
    async def find(cls, collection_name, filter={}, sort=None, skip=0, limit=0):
        collection = await cls.get_collection(collection_name)
        cursor = collection.find(filter)
        if sort:
            cursor = cursor.sort(sort)
        return await cursor.skip(skip).limit(limit).to_list(length=limit)

    @classmethod
    async def find_one(cls, collection_name, filter):
        collection = await cls.get_collection(collection_name)
        return await collection.find_one(filter)

    @classmethod
    async def list_collection_names(cls):
        return await cls.db.list_collection_names()

    @classmethod
    async def count_posts(cls, collection_name: str):
        collection = await cls.get_collection(collection_name)
        return await collection.count_documents({'_id': {'$ne': 'last_update'}})
