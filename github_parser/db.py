from contextlib import asynccontextmanager
import asyncpg
import logging


DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "database": "github_stats",
    "password": "postgres"
}

class Database:
    _pool: asyncpg.pool.Pool = None     # статическое поле для хранения пула подключений 

    @classmethod
    async def initialize(cls):
        """Инициализация пула подключений, если он еще не был инициализирован"""
        try:
            if cls._pool is None:
                cls._pool = await asyncpg.create_pool(**DATABASE_CONFIG)
        except Exception as e:
            logging.error(f'Ошибка при инициализации пула подключений: {e}')
            raise
    
    @classmethod
    async def close(cls):
        """Закрытие пула подключений"""
        if cls._pool is not None:
            await cls._pool.close()
            cls._pool = None
            logging.info("Соединение с базой данных закрыто.")
    
    @classmethod
    @asynccontextmanager
    async def get_connection(cls):
        """Захват подключения из пула и инициализация в случае необходимости"""
        if cls._pool is None:
            await cls.initialize()
        try:
            async with cls._pool.acquire() as connection:
                yield connection
        except asyncpg.PostgresError as e:
            logging.error(f'Ошибка при захвате подключения: {e}')
            raise
