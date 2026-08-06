"""Gemini client wrapper with graceful offline fallback."""
from __future__ import annotations
import os

import streamlit as st

from .config import GEMINI_API_KEY, GEMINI_MODELS


def get_key() -> str:
    key = st.session_state.get("gemini_key") or GEMINI_API_KEY
    if not key:
        try:
            key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            key = ""
    return key or ""


def available() -> bool:
    if not get_key():
        return False
    try:
        import google.generativeai  # noqa: F401
        return True
    except Exception:
        return False


def generate(prompt: str, system: str = "", model: str | None = None,
             temperature: float = 0.4, max_tokens: int = 2048) -> str | None:
    """Return model text, or None when the AI backend is unavailable."""
    if not available():
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=get_key())
        model = model or st.session_state.get("ai_model", GEMINI_MODELS[0])
        m = genai.GenerativeModel(model, system_instruction=system or None)
        resp = m.generate_content(
            prompt,
            generation_config={"temperature": temperature, "max_output_tokens": max_tokens},
        )
        return (resp.text or "").strip()
    except Exception as e:  # network / quota / bad key
        st.session_state["ai_error"] = str(e)
        return None


ANALYST_SYSTEM = (
    "You are a senior business intelligence analyst. You are given aggregated statistics "
    "from a company's sales dataset. Write clear, specific, decision-oriented commentary "
    "for a business owner who is not technical. Always reference the actual numbers you are "
    "given, never invent figures, and keep every point under two sentences."
)
