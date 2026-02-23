# tg-combot (community bot)

Telegram-бот для **внешней аудитории** на **pyTelegramBotAPI**.

Базовая логика сейчас такая:
- конфигурация через **переменные окружения** + `.env` (`python-dotenv`)
- polling (снятие webhook, backoff при сетевых ошибках)
- опциональный gate «подписка на канал» (проверка через `getChatMember`)
- после успешной подписки бот **отправляет ссылку** (задаётся прямо в коде)

## Быстрый старт (локально)

1) Создай `.env` по примеру:

```bash
cp .env.example .env
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

## Подписка на канал

Переменные окружения (включи gate):

- `SUBSCRIPTION_GATE_ENABLED=1`
- `CHANNEL_ID=-100...`
- `CHANNEL_URL=https://t.me/...`
- `SUBSCRIPTION_PHOTO_PATH=...` (опционально)

Ссылка, которую отправляем после успешной подписки, задаётся в коде:

- `source/subscription.py` → `COMMUNITY_LINK`
