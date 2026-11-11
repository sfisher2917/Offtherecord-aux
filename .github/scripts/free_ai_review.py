"""One bounded, explicitly approved request; no retries or paid fallback."""

import json
import os
import re
import sys
import urllib.error
import urllib.request


PROVIDERS = {
    "groq": ("GROQ_API_KEY", "https://api.groq.com/openai/v1/chat/completions", "openai/gpt-oss-20b"),
    "openrouter": ("OPENROUTER_API_KEY", "https://openrouter.ai/api/v1/chat/completions", "openrouter/free"),
    "gemini": ("GEMINI_API_KEY", "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent", "gemini-3.8-flash"),
}
REQUEST_TIMEOUT_SECONDS = 100


def safe_log(value, key):
    """Keep secrets and workflow commands out of provider-supplied log text."""
    value = str(value).replace(key, "[REDACTED]")
    value = re.sub(r"(?:gsk_|sk-or-v1-|AIza|AQ\.)[A-Za-z0-9_.-]+", "[REDACTED]", value)
    for line in value[:5000].splitlines():
        print("Provider output:", line)


def main():
    provider = os.environ.get("PROVIDER", "")
    prompt = os.environ.get("PROMPT", "").strip()
    if provider not in PROVIDERS:
        sys.exit("Provider not allowed")
    if not prompt or len(prompt) > 1000:
        sys.exit("Prompt must be 1-1000 characters")
    secret, url, model = PROVIDERS[provider]
    key = os.environ.get(secret, "").strip()
    if not key:
        sys.exit("Missing secret: " + secret)
    if len(key) < 20 or re.search(r"[\s*\u2022\u2026]", key):
        sys.exit("Incomplete or masked API key; replace the encrypted repository secret")
    if provider == "gemini":
        body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"maxOutputTokens": 512}}
        headers = {"x-goog-api-key": key}
    else:
        body = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 512}
        headers = {"Authorization": "Bearer " + key}
    headers.update({"Content-Type": "application/json", "User-Agent": "Fisher-Free-AI-Review/1.0"})
    request = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            data = json.load(response)
    except urllib.error.HTTPError as error:
        print("Provider request failed with HTTP", error.code, "(no paid fallback)")
        try:
            detail = json.loads(error.read(16384)).get("error", {})
            if isinstance(detail, dict):
                safe_log(json.dumps({field: detail[field] for field in ("code", "type", "status", "message") if field in detail}), key)
        except (ValueError, OSError):
            print("Provider returned a non-JSON error response")
        return 1
    except (TimeoutError, urllib.error.URLError, OSError):
        print("Provider connection failed or timed out; stopped without retry or paid fallback")
        return 1
    except ValueError:
        print("Provider returned an invalid JSON response")
        return 1
    if provider == "gemini":
        result = "\n".join(part.get("text", "") for candidate in data.get("candidates", []) for part in candidate.get("content", {}).get("parts", []))
    else:
        choices = data.get("choices") or []
        result = choices[0].get("message", {}).get("content", "") if choices else ""
    if not isinstance(result, str) or not result.strip():
        print("Provider returned no answer text; this is not a successful connection test")
        return 1
    print("Provider:", provider, "Model:", model)
    safe_log(result, key)
    return 0


if __name__ == "__main__":
    sys.exit(main())
