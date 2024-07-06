### Настройка
# Данные для подключения к PostgreSQL
DB_USER=""
DB_PASSWORD=""
DB_HOST=""
DB_PORT=""
DB_NAME=""

# Yandex Cloud
FOLDER_NAME=""          # Имя каталога облака (по умолчанию default)
FOLDER_ID=""            # ID каталога
SERVICE_ACCOUNT_ID=""	# ID сервисного аккаунта

# Создание сервисного аккаунта и присвоение ему роли для создания триггера

# Получение списка каталогов и выбор первого из них (или другого по необходимости)
if [ -z "$FOLDER_NAME" ]; then
        FOLDER_NAME=$(yc resource-manager folder list --format json | jq -r '.[0].name')
fi

# Если SERVICE_ACCOUNT_ID не указан (пустой) - то создает новый аккаунт и присваивает SERVICE_ACCOUNT_ID
if [ -z "$SERVICE_ACCOUNT_ID" ]; then
        echo "Создание нового сервисного аккаунта..."
        yc iam service-account create --name service-acc
        SERVICE_ACCOUNT_ID=$(yc iam service-account get --name service-acc --format json | jq -r .id) 

        # Получение ID текущего каталога по его имени
        FOLDER_ID=$(yc resource-manager folder get --name $FOLDER_NAME --format json | jq -r .id)

        echo "Назначение роли functions.functionInvoker новому сервисному аккаунту..."
        yc resource-manager folder add-access-binding --id $FOLDER_ID \
        --role functions.functionInvoker \
        --subject serviceAccount:$SERVICE_ACCOUNT_ID      
fi

echo "Сервисный аккаунт с ID: $SERVICE_ACCOUNT_ID готов к использованию."

# Создание YC функции
echo "Создание YC функции..."
yc serverless function create --name=parser-function

# Создание версии функции
yc serverless function version create \
        --function-name=parser-function \
        --runtime python312 \
        --entrypoint main.handler \
        --execution-timeout 5m \
        --memory 128m \
        --environment POSTGRES_USER=$POSTGRES_USER \
        --environment POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
        --environment POSTGRES_HOST=$POSTGRES_HOST \
        --environment POSTGRES_PORT=$POSTGRES_PORT \
        --source-path ./github_parser

echo "Функция parser-function готова к использованию."

# Создание триггера функции для запуска раз в час
echo "Создание триггера функции..."
yc serverless trigger create timer \
        --name parser-trigger \
        --cron-expression '0 * ? * * *' \
        --invoke-function-name parser-function \
        --invoke-function-service-account-id $SERVICE_ACCOUNT_ID
echo "Триггер создан"