"""
LLM client for all agents.
- Default: loads .env from project root. GEMINI_API_KEY and GEMINI_BASE_URL from .env are used first.
- When GEMINI_BASE_URL is set (e.g. AI Gateway): uses openai package (OpenAI-compatible client); model defaults to gemini-2.0-flash if GEMINI_MODEL not in .env.
- When GEMINI_BASE_URL not set: uses google-generativeai (direct Gemini).
"""

import os
from pathlib import Path
from typing import Optional

# Load .env from project root (parent of src/)
_env_loaded = False
def _load_dotenv():
    global _env_loaded
    if _env_loaded:
        return
    try:
        from dotenv import load_dotenv
        root = Path(__file__).resolve().parent.parent
        load_dotenv(root / ".env")
        _env_loaded = True
    except ImportError:
        pass

# Lazy imports so app can run without key until workflow is triggered
_genai = None


def get_api_key() -> Optional[str]:
    """API key: default from .env, then env, then Streamlit secrets."""
    _load_dotenv()
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    try:
        import streamlit as st
        if hasattr(st, "secrets") and st.secrets:
            return st.secrets.get("GEMINI_API_KEY")
    except Exception:
        pass
    return None


def get_base_url() -> Optional[str]:
    """Base URL for AI Gateway: default from .env, then env, then Streamlit secrets."""
    _load_dotenv()
    url = os.environ.get("GEMINI_BASE_URL", "").strip()
    if url:
        return url.rstrip("/")
    try:
        import streamlit as st
        if hasattr(st, "secrets") and st.secrets:
            url = (st.secrets.get("GEMINI_BASE_URL") or "").strip()
            if url:
                return url.rstrip("/")
    except Exception:
        pass
    return None


def _get_client():
    global _genai
    if _genai is None:
        try:
            import google.generativeai as genai
            _genai = genai
        except ImportError:
            raise ImportError("Install google-generativeai: pip install google-generativeai")
    return _genai


def call_llm(system_prompt: str, user_content: str, model: str = "gemini-1.5-flash") -> str:
    """
    Call LLM with system + user content. Returns full text response.
    When GEMINI_BASE_URL is set, uses OpenAI-compatible client (e.g. AI Gateway).
    Otherwise uses Google Generative AI (Gemini) directly.
    Raises if GEMINI_API_KEY is missing or API fails.
    """
    key = get_api_key()
    if not key:
        raise ValueError("GEMINI_API_KEY not set. Set it in environment or Streamlit secrets.")

    base_url = get_base_url()
    if base_url:
        # AI Gateway (OpenAI-compatible): use openai package; model from .env or default gateway-allowed model
        _load_dotenv()
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Install openai: pip install openai")
        client = OpenAI(api_key=key, base_url=base_url)
        # Default gemini-2.0-flash for gateway (key often allows gemini-2.0-flash, gemini-2.5-flash, etc.)
        model_name = os.environ.get("GEMINI_MODEL")
        if not model_name:
            try:
                import streamlit as st
                if hasattr(st, "secrets") and st.secrets:
                    model_name = st.secrets.get("GEMINI_MODEL")
            except Exception:
                pass
        model_name = model_name or "gemini-2.0-flash"
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        )
        if not response.choices or not response.choices[0].message.content:
            raise RuntimeError(f"Empty response from {model_name}: {response}")
        return response.choices[0].message.content.strip()

    # Direct Gemini
    genai = _get_client()
    genai.configure(api_key=key)
    model_obj = genai.GenerativeModel(
        model_name=model,
        system_instruction=system_prompt,
    )
    response = model_obj.generate_content(user_content)
    if not response.text:
        raise RuntimeError(f"Empty response from {model}: {getattr(response, 'prompt_feedback', '')}")
    return response.text
