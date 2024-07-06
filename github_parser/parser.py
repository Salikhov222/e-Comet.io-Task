import asyncpg
import logging

from asyncpg import Record
from typing import Dict, List, Any
from datetime import datetime
from github_api import top_100_repos, repo_commits
from db import fetch_existing_repos, insert_new_repos, update_existing_repos


async def save_top_100_repos_tp_db(connection: asyncpg.Connection) -> List[Dict[str, Any]]:
    """Запись данных в БД"""
    repos: List[Dict[str, Any]] = await top_100_repos()
    repo_id = await fetch_existing_repos(connection)
    insert_list = []    # список для вставки новых репозиториев из запроса
    update_list = []    # список для обновления существующих в БД репозиториев

    for item in repos:
        repo = item["full_name"]

        if repo not in repo_id:
            insert_list.append((repo,
                                item["owner"]["login"],
                                item["stargazers_count"],
                                item["watchers_count"],
                                item["forks_count"],
                                item["open_issues_count"],
                                item["language"]))
            
        else:
            update_list.append((repo_id[repo][0],    # id текущего репозитория,
                                item["owner"]["login"],
                                item["stargazers_count"],
                                item["watchers_count"],
                                item["forks_count"],
                                item["open_issues_count"],
                                item["language"]))

    try:
        async with connection.transaction():
            if update_list:
                await update_existing_repos(connection, update_list)
            if insert_list:
                await insert_new_repos(connection, insert_list)
        logging.info("Репозитории успешно сохранены в БД")

    except asyncpg.PostgresError as e:
        logging.error(f'Ошибка при выполнении транзакции для записи или обновления данных в БД: {e}')
        raise

    return repos 

async def update_positions_top_100(connection: asyncpg.Connection) -> None:
    """Обновление текущей и предыдущей позиции репозитория"""
    repo_id = await fetch_existing_repos(connection)
    for i, key in enumerate(repo_id, start=1):
        position_cur = repo_id[key][1]
        if i != position_cur:   # в случае несовпадения текущего места репозитория по индексу производим обновление позиций
            try:
                async with connection.transaction():
                    await connection.execute("""UPDATE top_repos
                                                SET
                                                    position_cur = $1,
                                                    position_prev = $2
                                                WHERE repo = $3""",
                                            i, position_cur, key)
            except asyncpg.PostgresError as e:
                logging.error(f'Ошибка при выполнении транзакции для обновления позиций репозиториев: {e}')
                raise
    logging.info("Позиции репозиториев успешно обновлены")

async def repo_activity(repos: List[Dict[str, Any]], connection: asyncpg.Connection) -> List:
    """Получение активности репозиториев и сохранением этих данных в БД"""
    existing_repos = await fetch_existing_repos(connection)
    for repo in repos:
        repo_data = existing_repos.get(repo['full_name'])
        if not repo_data:
            continue
        repo_id = repo_data[0]
        owner, repo = repo['full_name'].split('/')
        commits = await repo_commits(owner, repo)
        # словарь для хранения коммитов в по дням в качестве ключей, а
        # значением будет еще один словарь с количеством коммитов и
        # множеством авторов
        activity: Dict[str, Dict[str, Any]] = {}
        for item in commits:
            commit_date_str = item["commit"]["author"]["date"][:10]
            commit_date = datetime.strptime(commit_date_str, "%Y-%m-%d").date()     # преобразование строки в формат date
            if commit_date not in activity:
                activity[commit_date] = {"commits_count": 0, "authors": set()}
            activity[commit_date]["commits_count"] += 1
            activity[commit_date]["authors"].add(item["commit"]["author"]["name"])

        insert_data = []
        for date, data in activity.items():
            commit_count = data['commits_count']
            authors = list(data['authors'])
            insert_data.append((repo_id, date, commit_count, authors))  
        

        try:
            async with connection.transaction():
                await connection.executemany("""INSERT INTO repo_activity 
                                             VALUES (DEFAULT, $1, $2, $3, $4)
                                             ON CONFLICT (repo_id, date)
                                             DO UPDATE SET commits = EXCLUDED.commits, authors = EXCLUDED.authors""",
                                             insert_data)    
        except asyncpg.PostgresError as e:
            logging.error(f'Ошибка при выполнении транзакции для записи активности репозитория: {e}')
            raise
    logging.info("Коммиты по дням успешно сохранены в БД")
