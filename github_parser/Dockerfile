FROM python:3.10

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /github_parser

# Копируем файл зависимостей в директорию tmp и устанавливаем их
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем все файлы приложения в контейнер
COPY . .

# Указываем переменную окружения PYTHONPATH для корректной работы Python
ENV PYTHONPATH /

CMD [ "python", "main.py" ]