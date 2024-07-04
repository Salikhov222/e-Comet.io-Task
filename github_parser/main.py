import asyncio
import logging

from db import Database
from parser import save_top_100_repos_tp_db, update_positions_top_100, repo_activity # type: ignore

logging.basicConfig(level=logging.INFO)

async def main() -> None:
    try:
        async with Database.get_connection() as connection:
            logging.info("Получение списка репозиториев")
            repos = await save_top_100_repos_tp_db(connection)
            logging.info("Получение активности репозиториев")
            await repo_activity(repos, connection)
            await update_positions_top_100(connection)
    finally:
        await Database.close()

def handler(event, context):
    # Запуск асинхронной функции main и ожидание ее выполнения
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    # Возврат ответа об успешном выполнении
    return {'statusCode': 200, 'body': 'Successfully parsed data'}

if __name__=="__main__":    # для локального тестирования
    asyncio.run(main())
