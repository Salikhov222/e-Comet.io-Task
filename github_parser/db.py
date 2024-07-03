import asyncpg
import logging
import os 

from contextlib import asynccontextmanager
from asyncpg import Record
from typing import Dict, List


DATABASE_CONFIG = {
    "host": os.getenv('DB_HOST'),
    "port": os.getenv('DB_PORT'),
    "user": os.getenv('DB_USER'),
    "database": os.getenv('DB_NAME'),
    "password": os.getenv('DB_PASSWORD')
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
                logging.info("Соединение с базой установлено")
                yield connection
                logging.info("Соединение освобождено")
        except asyncpg.PostgresError as e:
            logging.error(f'Ошибка при захвате подключения: {e}')
            raise

# Функции для взаимодействия с БД

async def fetch_existing_repos(connection: asyncpg.Connection) -> Dict[str, int]:
    """Извлечение существующих репозиториев в БД"""
    rows: List[Record] = await connection.fetch("SELECT repo, id, position_cur FROM top_repos ORDER BY stars DESC LIMIT 100")
    return {row['repo']: (row['id'], row['position_cur']) for row in rows}

async def insert_new_repos(connection: asyncpg.Connection, insert_list: List[tuple]) -> None:
    """Вставка новых репозиториев"""
    await connection.executemany(
        """INSERT INTO top_repos(id, repo, owner, stars, watchers, forks, open_issues, language) 
        VALUES(DEFAULT, $1, $2, $3, $4, $5, $6, $7)""", 
        insert_list
    )

async def update_existing_repos(connection: asyncpg.Connection, update_list: List[tuple]) -> None:
    """Обновление существующих репозиториев"""
    for update_data in update_list:
        await connection.execute("""UPDATE top_repos
                                    SET
                                        owner = $2,
                                        stars = $3,
                                        watchers = $4,
                                        forks = $5,
                                        open_issues = $6,
                                        language = $7
                                    WHERE id = $1""", 
                                        *update_data
        )