import aiohttp
import os

from typing import Dict, List, Any


GITHUB_API_URL = "https://api.github.com"
headers = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

async def fetch_data(session: aiohttp.ClientSession, url: str) -> Dict:
    """Обращение к API GitHub для парсинга данных"""
    async with session.get(url, headers=headers) as result:
        result.raise_for_status()   # вызов исключения для ошибок HTTP
        return await result.json()
    
async def top_100_repos() -> List[Dict[str, Any]]:
    """Получение топ 100 репозиториев"""
    async with aiohttp.ClientSession() as session:
        url = f"{GITHUB_API_URL}/search/repositories?q=stars:>0&sort=stars&order=desc&per_page=100"
        response = await fetch_data(session, url)
        return response["items"]

async def repo_commits(owner: str, repo: str) -> List[Dict[str, Any]]:
    """Получение коммитов репозитория"""
    async with aiohttp.ClientSession() as session:
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/commits"
        response = await fetch_data(session, url)
        return response