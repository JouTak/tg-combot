from __future__ import annotations

import os
import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


_LOCK = threading.Lock()
_INITED = False


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _db_path() -> str:
    return os.getenv("USERS_DB_PATH", "data/users.sqlite3")


def _connect() -> sqlite3.Connection:
    path = _db_path()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    conn = sqlite3.connect(path, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def _init():
    global _INITED
    if _INITED:
        return
    with _LOCK:
        if _INITED:
            return
        with _connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    chat_id INTEGER,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    language_code TEXT,
                    is_bot INTEGER,
                    first_seen_at TEXT,
                    last_seen_at TEXT,
                    gate_shown_count INTEGER NOT NULL DEFAULT 0,
                    gate_shown_last_at TEXT,
                    subscription_verified_at TEXT,
                    materials_sent_count INTEGER NOT NULL DEFAULT 0,
                    materials_sent_last_at TEXT
                )
                """
            )
        _INITED = True


def touch_user(user: Any, chat_id: int | None = None):
    _init()
    user_id = getattr(user, "id", None)
    if user_id is None:
        return
    now = _now_iso()
    username = getattr(user, "username", None)
    first_name = getattr(user, "first_name", None)
    last_name = getattr(user, "last_name", None)
    language_code = getattr(user, "language_code", None)
    is_bot = 1 if getattr(user, "is_bot", False) else 0

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO users (
                user_id, chat_id, username, first_name, last_name, language_code, is_bot,
                first_seen_at, last_seen_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                chat_id=COALESCE(excluded.chat_id, users.chat_id),
                username=excluded.username,
                first_name=excluded.first_name,
                last_name=excluded.last_name,
                language_code=excluded.language_code,
                is_bot=excluded.is_bot,
                last_seen_at=excluded.last_seen_at
            """,
            (int(user_id), int(chat_id) if chat_id is not None else None, username, first_name, last_name, language_code, is_bot, now, now),
        )


def mark_gate_shown(user_id: int):
    _init()
    now = _now_iso()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO users (user_id, first_seen_at, last_seen_at, gate_shown_count, gate_shown_last_at)
            VALUES (?, ?, ?, 1, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                gate_shown_count = users.gate_shown_count + 1,
                gate_shown_last_at = ?,
                last_seen_at = ?
            """,
            (int(user_id), now, now, now, now, now),
        )


def mark_subscription_verified(user_id: int):
    _init()
    now = _now_iso()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO users (user_id, first_seen_at, last_seen_at, subscription_verified_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                subscription_verified_at = COALESCE(users.subscription_verified_at, ?),
                last_seen_at = ?
            """,
            (int(user_id), now, now, now, now, now),
        )


def mark_materials_sent(user_id: int):
    _init()
    now = _now_iso()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO users (
                user_id, first_seen_at, last_seen_at,
                subscription_verified_at, materials_sent_count, materials_sent_last_at
            ) VALUES (?, ?, ?, ?, 1, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                subscription_verified_at = COALESCE(users.subscription_verified_at, excluded.subscription_verified_at),
                materials_sent_count = users.materials_sent_count + 1,
                materials_sent_last_at = excluded.materials_sent_last_at,
                last_seen_at = excluded.last_seen_at
            """,
            (int(user_id), now, now, now, now),
        )
