"""
Test GEMINI_API_KEY and GEMINI_BASE_URL from .env with a minimal LLM call.
Run from project root: py scripts/test_api_key.py
"""

import sys
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

from src.llm import get_api_key, get_base_url, call_llm


def main():
    print("Testing Gemini API key and base URL from .env ...")
    key = get_api_key()
    base_url = get_base_url()
    if not key:
        print("FAIL: GEMINI_API_KEY not set in .env or environment.")
        return 1
    print(f"  GEMINI_API_KEY: {key[:8]}...{key[-4:] if len(key) > 12 else '***'}")
    print(f"  GEMINI_BASE_URL: {base_url or '(not set, using direct Gemini)'}")
    print("  Sending minimal test request...")
    # Uses .env GEMINI_MODEL or default gemini-2.0-flash (gateway-allowed)
    try:
        response = call_llm("You are a test. Reply with exactly: OK", "Say OK")
        print(f"  Response: {response.strip()[:200]}")
        print("SUCCESS: API key and base URL are working.")
        return 0
    except Exception as e:
        print(f"FAIL: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
