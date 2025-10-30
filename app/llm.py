import os
import json
import httpx
from typing import Any, List, Mapping, Optional, Type, Union
from langchain_core.language_models import LLM
from pydantic import BaseModel, Field
from dotenv import load_dotenv
 
load_dotenv()

class MistralLLM(LLM):
    """LangChain-compatible wrapper for Mistral Chat API with JSON mode support."""

    api_url: str = Field(default="https://api.mistral.ai/v1/chat/completions")
    api_key: str = Field(default_factory=lambda: os.getenv("MISTRAL_API_KEY", ""))
    model: str = Field(default_factory=lambda: os.getenv("MISTRAL_MODEL", "mistral-large-2411"))
    temperature: float = 0.3
    max_tokens: int = 2500
    top_p: float = 0.95
    response_format: Optional[dict] = None  # For JSON mode

    @property
    def _llm_type(self) -> str:
        return "mistral"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {
            "model": self.model, 
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p
        }

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
                    "content": (
                        "You are a senior penetration tester and security researcher. "
                        "You write professional, compact vulnerability reports following industry standards. "
                        "You MUST respond with valid JSON matching the exact schema provided. "
                        "CRITICAL: Strictly respect all character limits (max_length) - violating them will cause errors. "
                        "Be concise and precise - prioritize quality over quantity."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "safe_prompt": False
        }
        
        # Add JSON mode if schema provided
        if self.response_format:
            payload["response_format"] = self.response_format

        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                with httpx.Client(timeout=90.0) as client:
                    r = client.post(self.api_url, headers=headers, json=payload)
                    r.raise_for_status()
                    data = r.json()

                content = data["choices"][0]["message"]["content"].strip()
                return content
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    retry_count += 1
                    if retry_count < max_retries:
                        import time
                        time.sleep(2 ** retry_count)
                        continue
                raise RuntimeError(f"Mistral API error: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise RuntimeError(f"Failed after {max_retries} retries: {str(e)}")
        
        raise RuntimeError("Failed to generate report after maximum retries")

    def generate_structured(
        self, 
        prompt: str, 
        schema: Type[BaseModel]
    ) -> BaseModel:
        """
        Generate structured output matching a Pydantic schema.
        
        Args:
            prompt: The prompt to send to the LLM
            schema: Pydantic model class defining the expected structure
            
        Returns:
            Parsed and validated instance of the schema
        """
        # Enable JSON mode
        self.response_format = {"type": "json_object"}
        
        # Get JSON schema from Pydantic model
        json_schema = schema.model_json_schema()
        
        # Enhance prompt with schema
        enhanced_prompt = f"""{prompt}

You MUST respond with valid JSON matching this exact schema:

{json.dumps(json_schema, indent=2)}

CRITICAL RULES:
- Output ONLY valid JSON, no markdown, no explanations
- Include ALL required fields
- Follow field descriptions for content guidelines
- Keep responses compact and professional - quality over quantity
- For list fields, provide exactly the number of items specified in min_items/max_items
- For string fields, STRICTLY stay within max_length CHARACTER LIMITS (not words) - this is mandatory
- Character limits are HARD LIMITS - exceeding them will cause validation failures
"""
        
        # Generate response
        raw_response = self._call(enhanced_prompt)
        
        # Parse and validate
        try:
            # Handle markdown code blocks if present
            if "```json" in raw_response:
                raw_response = raw_response.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_response:
                raw_response = raw_response.split("```")[1].split("```")[0].strip()
            
            data = json.loads(raw_response)
            return schema(**data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\n\nRaw response: {raw_response}")
        except Exception as e:
            raise ValueError(f"Failed to validate response against schema: {e}\n\nParsed data: {data}")
