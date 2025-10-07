import os
import databases
import sqlalchemy

DB_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:example@timescaledb:5432/mobility')

database = databases.Database(DB_URL)
engine = sqlalchemy.create_engine(DB_URL)
metadata = sqlalchemy.MetaData()

class Database:
    @staticmethod
    async def connect():
        await database.connect()

    @staticmethod
    async def disconnect():
        await database.disconnect()

    @staticmethod
    async def execute(query, values=None):
        return await database.execute(query=query, values=values or {})

    @staticmethod
    async def fetch_one(query, values=None):
        return await database.fetch_one(query=query, values=values or {})

    @staticmethod
    async def fetch_all(query, values=None):
        return await database.fetch_all(query=query, values=values or {})
