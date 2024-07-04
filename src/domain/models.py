from datetime import date
from typing import Optional, List
from pydantic import BaseModel


class Repo(BaseModel):
    repo: str
    owner: str
    position_cur: int
    position_prev: Optional[int] = None
    stars: int
    watchers: int
    forks: int
    open_issues: int
    language: Optional[str] = "Undefined"


class RepoActivity(BaseModel):
    date: date
    commits: int
    authors: List[str]
