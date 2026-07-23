"""Provider-agnostic LLM client with automatic fallback."""
from __future__ import annotations

from typing import Protocol

from app.config import settings


class LLMError(RuntimeError):
    pass


class LLMClient(Protocol):
    name: str

    def generate(self, prompt: str) -> str: ...


class GeminiClient:
    name = "gemini"

    def __init__(self) -> None:
        from google import genai
        if not settings.gemini_api_key:
            raise LLMError("GEMINI_API_KEY not set")
        self._client = genai.Client(api_key=settings.gemini_api_key)

    def generate(self, prompt: str) -> str:
        resp = self._client.models.generate_content(
            model=settings.generation_model,
            contents=prompt,
        )
        return (resp.text or "").strip()


class GroqClient:
    name = "groq"

    def __init__(self) -> None:
        from groq import Groq
        if not settings.groq_api_key:
            raise LLMError("GROQ_API_KEY not set")
        self._client = Groq(api_key=settings.groq_api_key)

    def generate(self, prompt: str) -> str:
        resp = self._client.chat.completions.create(
            model=settings.groq_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        return (resp.choices[0].message.content or "").strip()


_REGISTRY = {"gemini": GeminiClient, "groq": GroqClient}
_cache: dict[str, LLMClient] = {}


def generate(prompt: str) -> tuple[str, str]:
    """Try each provider in order. Returns (answer, provider_name)."""
    errors = []
    for name in [p.strip() for p in settings.provider_chain.split(",") if p.strip()]:
        cls = _REGISTRY.get(name)
        if cls is None:
            continue
        try:
            if name not in _cache:
                _cache[name] = cls()
            return _cache[name].generate(prompt), name
        except Exception as exc:
            errors.append(f"{name}: {type(exc).__name__}: {exc}")
            continue
    raise LLMError("All providers failed:\n" + "\n".join(errors))
