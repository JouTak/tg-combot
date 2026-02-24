# tg-combot (community bot)

Telegram-бот для **внешней аудитории** на **pyTelegramBotAPI**.

Базовая логика сейчас такая:
- конфигурация через **переменные окружения** + `.env` (`python-dotenv`)
- polling (снятие webhook, backoff при сетевых ошибках)
- опциональный gate «подписка на канал» (проверка через `getChatMember`)
- после успешной подписки бот **отправляет материалы** (задаётся в коде)
- бот **запоминает пользователей** (для будущих рассылок/метрик)

## Быстрый старт (локально)

1) Создай `.env` вручную:

```env
BOT_TOKEN=123456:xxxx
SUBSCRIPTION_GATE_ENABLED=1
CHANNEL_ID=-1001234567890
CHANNEL_URL=https://t.me/your_channel
```

2) Установи зависимости и запусти:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r source/requirements.txt
python -m source
```

## Запуск в Docker

```bash
docker build -t tg-combot --build-arg GIT_COMMIT=$(git rev-parse --short HEAD) .
docker run --rm --env-file .env tg-combot
```

Чтобы метрики/список пользователей не пропадали при пересоздании контейнера, примонтируй data-директорию:

```bash
docker run --rm --env-file .env -v ./data:/app/data tg-combot
```

## Подписка на канал

Переменные окружения (включи gate):

- `SUBSCRIPTION_GATE_ENABLED=1`
- `CHANNEL_ID=-100...`
- `CHANNEL_URL=https://t.me/...`
- `SUBSCRIPTION_PHOTO_PATH=...` (опционально)

Текст материалов задаётся в коде:

- `source/subscription.py` → `COMMUNITY_LINK`

## Хранение пользователей

По умолчанию бот пишет SQLite в `data/users.sqlite3`.

Опционально можно переопределить путь:

- `USERS_DB_PATH=/app/data/users.sqlite3`
