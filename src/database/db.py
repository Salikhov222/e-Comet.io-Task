import asyncpg
import logging

from datetime import date
from contextlib import asynccontextmanager
from typing import List

from src.config import get_postgres_uri


class Database:
    _pool: asyncpg.pool.Pool = None     # статическое поле для хранения пула подключений 

    @classmethod
    async def initialize(cls):
        """Инициализация пула подключений, если он еще не был инициализирован"""
        try:
            if cls._pool is None:
                print(get_postgres_uri())
                cls._pool = await asyncpg.create_pool(get_postgres_uri())
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

    @classmethod
    async def fetch_top_100_repos(cls, sort_by: str) -> List:
        """Извлечение из БД информации о топ 100 репозиториев"""
        async with cls.get_connection() as connection:
            query = f"""
            SELECT repo, owner, position_cur, position_prev, stars, watchers, forks, open_issues, language
            FROM top_repos
            WHERE position_cur <= 100
            ORDER BY {sort_by} DESC
            """
            rows = await connection.fetch(query)
            if not rows:
                return []
            return rows
        
    @classmethod
    async def fetch_repo_activity(cls, owner: str, repo: str, since: date, until: date) -> List:
        """Извлечение из БД информации об активности репозитория по дням"""
        async with cls.get_connection() as connection:
            repo = f"{owner}/{repo}"
            repo_id_data = await connection.fetch(
                "SELECT id FROM top_repos WHERE repo = $1 ORDER BY stars DESC LIMIT 100",
                repo
            )
            if not repo_id_data:
                return None
            repo_id = repo_id_data[0]["id"]

            activity = await connection.fetch(
                """SELECT date, commits, authors
                FROM repo_activity
                WHERE repo_id = $1 AND date BETWEEN $2 AND $3
                ORDER BY date""",
                repo_id, since, until
            )
            return activity 
            

