"""SQLite persistence layer (users, datasets, reports, chat, activity history)."""
from __future__ import annotations
import json
from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine, text

from .config import DB_PATH

_ENGINE = None

SCHEMA = [
    """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT,
        pwd_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS datasets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, name TEXT, path TEXT, source TEXT,
        rows INTEGER, cols INTEGER, created_at TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, name TEXT, kind TEXT, path TEXT, created_at TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, dataset TEXT, role TEXT, message TEXT, created_at TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, action TEXT, detail TEXT, created_at TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS queries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, name TEXT, sql TEXT, created_at TEXT
    )""",
]


def engine():
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = create_engine(f"sqlite:///{DB_PATH}", future=True)
        with _ENGINE.begin() as c:
            for stmt in SCHEMA:
                c.execute(text(stmt))
    return _ENGINE


def execute(sql: str, params: dict | None = None):
    with engine().begin() as c:
        return c.execute(text(sql), params or {})


def query_df(sql: str, params: dict | None = None) -> pd.DataFrame:
    with engine().begin() as c:
        return pd.DataFrame(c.execute(text(sql), params or {}).mappings().all())


def _now():
    return datetime.utcnow().isoformat(timespec="seconds")


def log(username: str, action: str, detail=""):
    if isinstance(detail, (dict, list)):
        detail = json.dumps(detail)
    execute(
        "INSERT INTO history (username, action, detail, created_at) "
        "VALUES (:u,:a,:d,:t)",
        {"u": username, "a": action, "d": str(detail)[:800], "t": _now()},
    )


def add_dataset(username, name, path, source, rows, cols):
    execute(
        "INSERT INTO datasets (username,name,path,source,rows,cols,created_at) "
        "VALUES (:u,:n,:p,:s,:r,:c,:t)",
        {"u": username, "n": name, "p": str(path), "s": source,
         "r": int(rows), "c": int(cols), "t": _now()},
    )


def add_report(username, name, kind, path):
    execute(
        "INSERT INTO reports (username,name,kind,path,created_at) VALUES (:u,:n,:k,:p,:t)",
        {"u": username, "n": name, "k": kind, "p": str(path), "t": _now()},
    )


def add_chat(username, dataset, role, message):
    execute(
        "INSERT INTO chat (username,dataset,role,message,created_at) VALUES (:u,:d,:r,:m,:t)",
        {"u": username, "d": dataset, "r": role, "m": message, "t": _now()},
    )


def save_query(username, name, sql):
    execute(
        "INSERT INTO queries (username,name,sql,created_at) VALUES (:u,:n,:s,:t)",
        {"u": username, "n": name, "s": sql, "t": _now()},
    )


def recent(table: str, username: str | None = None, limit: int = 20) -> pd.DataFrame:
    if username:
        return query_df(
            f"SELECT * FROM {table} WHERE username=:u ORDER BY id DESC LIMIT {int(limit)}",
            {"u": username})
    return query_df(f"SELECT * FROM {table} ORDER BY id DESC LIMIT {int(limit)}")
