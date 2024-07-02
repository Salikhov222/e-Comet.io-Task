import aiohttp
import asyncpg
import logging
from asyncpg import Record
from typing import Dict, List, Any


GITHUB_API_URL = "https://api.github.com"
headers = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

async def fetch_repos(session: aiohttp.ClientSession, url: str) -> Dict:
    """Обращение к API GitHub для парсинга данных"""
    async with session.get(url, headers=headers) as result:
        result.raise_for_status()   # вызов исключения для ошибок HTTP
        return await result.json()
    
async def top_100_repos() -> List[Dict[str, Any]]:
    """Получение топ 100 репозиториев"""
    async with aiohttp.ClientSession() as session:
        url = f"{GITHUB_API_URL}/search/repositories?q=stars:>0&sort=stars&order=desc&per_page=100"
        response = await fetch_repos(session, url)
        return response["items"]
    
async def save_top_100_repos_tp_db(connection: asyncpg.Connection) -> None:
    """Запись данных в БД"""
    repos: List[Dict[str, Any]] = await top_100_repos()
    rows: List[Record] = await connection.fetch("SELECT repo, position_cur FROM top_repos")
    repo_positions = {row['repo']: row['position_cur'] for row in rows}
    insert_list = []
    update_list = []

    for position, item in enumerate(repos, start=1):
        repo = item["full_name"]
        position_cur = position
        position_prev = repo_positions.get(repo, None)

        if repo not in repo_positions:
            insert_list.append((repo,
                                item["owner"]["login"],
                                position_cur,
                                None,
                                item["stargazers_count"],
                                item["watchers_count"],
                                item["forks_count"],
                                item["open_issues_count"],
                                item["language"]))
            
        else:
            update_list.append((repo,
                                item["owner"]["login"],
                                position_cur,
                                position_prev,
                                item["stargazers_count"],
                                item["watchers_count"],
                                item["forks_count"],
                                item["open_issues_count"],
                                item["language"]))

    try:
        async with connection.transaction():
            if update_list:
                for update_data in update_list:
                    await connection.execute("""UPDATE top_repos
                                            SET
                                                owner = $2,
                                                position_cur = $3,
                                                position_prev = $4,
                                                stars = $5,
                                                watchers = $6,
                                                forks = $7,
                                                open_issues = $8,
                                                language = $9
                                            WHERE repo = $1""", *update_data)
            if insert_list:
                await connection.executemany("INSERT INTO top_repos VALUES(DEFAULT, $1, $2, $3, $4, $5, $6, $7, $8, $9)", insert_list)
    except asyncpg.PostgresError as e:
        logging.error(f'Ошибка при выполнении транзакции: {e}')
        raise

