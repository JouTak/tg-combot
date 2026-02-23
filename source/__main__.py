from source.app_logging import setup_logging, logger
from source.app import run
from source.config import COMMIT_HASH


if __name__ == "__main__":
    setup_logging()
    logger.info(
        """
--- Бот запускается ---
Шаблон: tg-bot-template
Коммит: %s
""".strip()
        % COMMIT_HASH
    )
    run()
