import os
from dotenv import load_dotenv

load_dotenv()

# --- required ---
missing = [k for k in ("BOT_TOKEN",) if not os.getenv(k)]
if missing:
    raise RuntimeError("Missing env: " + ", ".join(missing))

# --- build info ---
COMMIT_HASH = os.getenv("GIT_COMMIT", "unknown")

# --- bot ---
BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- logging / runtime ---
APP_DEBUG = os.getenv("APP_DEBUG", "0")

# polling tuning (optional)
POLLING_TIMEOUT = int(os.getenv("POLLING_TIMEOUT", "20"))
LONG_POLLING_TIMEOUT = int(os.getenv("LONG_POLLING_TIMEOUT", "25"))
SKIP_PENDING = os.getenv("SKIP_PENDING", "1") == "1"
