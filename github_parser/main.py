import asyncio
import aiohttp
import asyncpg
import logging

from db import Database
from parser import save_top_100_repos_tp_db

logging.basicConfig(level=logging.INFO)

async def connect_to_db() -> None:
    async with Database.get_connection() as connection:
        version = connection.get_server_version()
        print(version)

async def main() -> None:
    try:
        async with Database.get_connection() as connection:
            await save_top_100_repos_tp_db(connection)
    finally:
        await Database.close()

if __name__=="__main__":
    asyncio.run(main())
