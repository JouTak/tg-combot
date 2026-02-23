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

# --- subscription gate (optional) ---
SUBSCRIPTION_GATE_ENABLED = os.getenv("SUBSCRIPTION_GATE_ENABLED", "0") == "1"
CHANNEL_ID_RAW = os.getenv("CHANNEL_ID")
CHANNEL_URL = os.getenv("CHANNEL_URL")
SUBSCRIPTION_PHOTO_PATH = os.getenv("SUBSCRIPTION_PHOTO_PATH", "")


def _parse_chat_id(value: str | None):
    if value is None:
        return None
    v = value.strip()
    if not v:
        return None
    if v.lstrip("-").isdigit():
        return int(v)
    return v


CHANNEL_ID = _parse_chat_id(CHANNEL_ID_RAW)

if SUBSCRIPTION_GATE_ENABLED:
    missing_gate = [k for k in ("CHANNEL_ID", "CHANNEL_URL") if not os.getenv(k)]
    if missing_gate:
        raise RuntimeError("Missing env: " + ", ".join(missing_gate))

# --- logging / runtime ---
APP_DEBUG = os.getenv("APP_DEBUG", "0")

# polling tuning (optional)
POLLING_TIMEOUT = int(os.getenv("POLLING_TIMEOUT", "20"))
LONG_POLLING_TIMEOUT = int(os.getenv("LONG_POLLING_TIMEOUT", "25"))
SKIP_PENDING = os.getenv("SKIP_PENDING", "1") == "1"
