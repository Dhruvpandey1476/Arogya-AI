import httpx
import json
import logging
from typing import AsyncGenerator

import config

logger = logging.getLogger(__name__)


class OllamaClient:
    """LLM client. Uses Groq (OpenAI-compatible API) when configured,
    otherwise falls back to a local Ollama server. Name kept for compatibility."""

    def __init__(self):
        self.provider = config.LLM_PROVIDER
        if self.provider == "groq":
            self.base_url = config.GROQ_BASE_URL
            self.model = config.GROQ_MODEL
            self.api_key = config.GROQ_API_KEY
        else:
            self.base_url = config.OLLAMA_BASE_URL
            self.model = config.OLLAMA_MODEL
            self.api_key = None

    # ---------------- Groq (OpenAI-compatible) ----------------
    def _groq_headers(self):
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def _groq_body(self, prompt: str, max_tokens: int, temperature: float, stream: bool):
        return {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.9,
            "stream": stream,
        }

    # ---------------- Sync generation (assessment) ----------------
    def generate(self, prompt: str, max_tokens: int = 800) -> str:
        if self.provider == "groq":
            return self._generate_groq(prompt, max_tokens)
        return self._generate_ollama(prompt, max_tokens)

    def _generate_groq(self, prompt: str, max_tokens: int) -> str:
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._groq_headers(),
                    json=self._groq_body(prompt, max_tokens, 0.3, False),
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Groq generate error: {e}")
            raise

    def _generate_ollama(self, prompt: str, max_tokens: int) -> str:
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"num_predict": max_tokens, "temperature": 0.3, "top_p": 0.9},
                    },
                )
                response.raise_for_status()
                return response.json().get("response", "")
        except httpx.ConnectError:
            raise RuntimeError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running: ollama serve"
            )
        except Exception as e:
            logger.error(f"Ollama generate error: {e}")
            raise

    # ---------------- Async streaming (WebSocket chat) ----------------
    async def stream(self, prompt: str, max_tokens: int = 600) -> AsyncGenerator[str, None]:
        if self.provider == "groq":
            async for tok in self._stream_groq(prompt, max_tokens):
                yield tok
        else:
            async for tok in self._stream_ollama(prompt, max_tokens):
                yield tok

    async def _stream_groq(self, prompt: str, max_tokens: int) -> AsyncGenerator[str, None]:
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=self._groq_headers(),
                    json=self._groq_body(prompt, max_tokens, 0.4, True),
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        line = line.strip()
                        if not line or not line.startswith("data:"):
                            continue
                        data = line[len("data:"):].strip()
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            token = chunk["choices"][0]["delta"].get("content", "")
                            if token:
                                yield token
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue
        except Exception as e:
            logger.error(f"Groq stream error: {e}")
            yield f"Error generating response: {str(e)}"

    async def _stream_ollama(self, prompt: str, max_tokens: int) -> AsyncGenerator[str, None]:
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": True,
                        "options": {"num_predict": max_tokens, "temperature": 0.4, "top_p": 0.9},
                    },
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                chunk = json.loads(line)
                                token = chunk.get("response", "")
                                if token:
                                    yield token
                                if chunk.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue
        except httpx.ConnectError:
            yield "⚠️ AI model unavailable. Please ensure Ollama is running with: ollama serve"
        except Exception as e:
            logger.error(f"Ollama stream error: {e}")
            yield f"Error generating response: {str(e)}"
