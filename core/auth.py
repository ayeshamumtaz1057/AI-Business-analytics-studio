"""Lightweight username/password auth with PBKDF2 hashing."""
from __future__ import annotations
import hashlib
import os
from datetime import datetime

import streamlit as st

from . import db


def _hash(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 120_000).hex()


def create_user(username: str, password: str, email: str = "", role: str = "user") -> tuple[bool, str]:
    username = (username or "").strip().lower()
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password or "") < 6:
        return False, "Password must be at least 6 characters."
    existing = db.query_df("SELECT id FROM users WHERE username=:u", {"u": username})
    if not existing.empty:
        return False, "That username is already taken."
    salt = os.urandom(16).hex()
    db.execute(
        "INSERT INTO users (username,email,pwd_hash,salt,role,created_at) "
        "VALUES (:u,:e,:p,:s,:r,:t)",
        {"u": username, "e": email, "p": _hash(password, salt), "s": salt,
         "r": role, "t": datetime.utcnow().isoformat(timespec="seconds")},
    )
    return True, "Account created."


def verify(username: str, password: str) -> bool:
    row = db.query_df("SELECT * FROM users WHERE username=:u", {"u": (username or "").strip().lower()})
    if row.empty:
        return False
    r = row.iloc[0]
    return _hash(password, r["salt"]) == r["pwd_hash"]


def set_password(username: str, password: str):
    salt = os.urandom(16).hex()
    db.execute("UPDATE users SET pwd_hash=:p, salt=:s WHERE username=:u",
               {"p": _hash(password, salt), "s": salt, "u": username})


def ensure_demo_user():
    if db.query_df("SELECT id FROM users WHERE username='demo'").empty:
        create_user("demo", "demo123", "demo@example.com", role="admin")


def current_user() -> str:
    return st.session_state.get("user", "")


def is_admin() -> bool:
    u = current_user()
    if not u:
        return False
    row = db.query_df("SELECT role FROM users WHERE username=:u", {"u": u})
    return (not row.empty) and row.iloc[0]["role"] == "admin"


def login(username: str):
    st.session_state["user"] = username
    db.log(username, "login")


def logout():
    u = current_user()
    if u:
        db.log(u, "logout")
    for k in ("user",):
        st.session_state.pop(k, None)
