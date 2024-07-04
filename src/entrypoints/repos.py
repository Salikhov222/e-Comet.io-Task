import logging
from datetime import date
from typing import List, Annotated

from fastapi import APIRouter, HTTPException, status, Query

from src.domain.models import Repo, RepoActivity
from src.database.db import Database


repos_router = APIRouter()


@repos_router.get("/repos/top100", response_model=List[Repo])
async def get_top_100_repos(sort_by: Annotated[str, Query(enum=["repo", "owner", "position_cur", "position_prev", "stars",
                            "watchers", "forks", "open_issues", "language"])] = "stars"):
    """
    Конечная точка для отображения топ 100 публичных репозиториев
    """
    try:
        repos_data = await Database.fetch_top_100_repos(sort_by)
        repos = [Repo(**repo_data) for repo_data in repos_data]
        return repos
    except Exception as e:
        logging.error(f'Ошибка при выполнении запроса топ 100 репозиториев к базе данных: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal Server Error"
        )

@repos_router.get("/repos/{owner}/{repo}/activity", response_model=List[RepoActivity])
async def get_repo_activity(owner: str,
                            repo: str,
                            since: Annotated[date, Query(description='Дата начала в формате ГГГГ-ММ-ДД')],
                            until: Annotated[date, Query(description='Дата конца в формате ГГГГ-ММ-ДД')]):
    """
    Конечная точка для отображения топ 100 публичных репозиториев
    """
    try:
        activities_data = await Database.fetch_repo_activity(owner, repo, since, until)
        activities = [RepoActivity(**activity_data) for activity_data in activities_data]
        return activities
    except Exception as e:
        logging.error(f'Ошибка при выполнении запроса активности репозитория к базе данных: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal Server Error"
        )