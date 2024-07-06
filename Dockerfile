FROM python:3.10-slim

# Копируем файл зависимостей в директорию tmp и устанавливаем их
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем bash скрипт для проверки состояния БД
COPY sh_scripts/wait-for-it.sh .
RUN chmod +x wait-for-it.sh

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /src

# Копируем все файлы приложения в контейнер
COPY src/ src/

# Указываем переменную окружения PYTHONPATH для корректной работы Python
ENV PYTHONPATH /

CMD [ "/wait-for-it.sh", "postgres:5432", "--", "uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000" ]