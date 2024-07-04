FROM python:3.10-slim

# Копируем файл зависимостей в директорию tmp и устанавливаем их
COPY requirements.txt .
RUN pip install -r requirements.txt

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /src

# Копируем все файлы приложения в контейнер
COPY src/ src/

# Указываем переменную окружения PYTHONPATH для корректной работы Python
ENV PYTHONPATH /

CMD [ "uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000" ]