import os
import httpx
from typing import Any, List, Mapping, Optional
from langchain_core.language_models import LLM
from pydantic import Field
from dotenv import load_dotenv
 
load_dotenv()

class MistralLLM(LLM):
    """LangChain-compatible wrapper for Mistral Chat API."""

    api_url: str = Field(default="https://api.mistral.ai/v1/chat/completions")
    api_key: str = Field(default_factory=lambda: os.getenv("MISTRAL_API_KEY", ""))
    model: str = Field(default_factory=lambda: os.getenv("MISTRAL_MODEL", "mistral-large-latest"))
    temperature: float = 0.7

    @property
    def _llm_type(self) -> str:
        return "mistral"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model": self.model, "temperature": self.temperature}

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        if not self.api_key:
            raise RuntimeError("Missing MISTRAL_API_KEY")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a senior penetration tester who writes professional vulnerability reports."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.temperature,
            "max_tokens": 1500
        }

        with httpx.Client(timeout=60.0) as client:
            r = client.post(self.api_url, headers=headers, json=payload)
            # Raise for 4xx/5xx errors
            r.raise_for_status()
            data = r.json()

        try:
            return data["choices"][0]["message"]["content"].strip()
        except Exception:
            # Defensive: if API shape changes
            return str(data)
