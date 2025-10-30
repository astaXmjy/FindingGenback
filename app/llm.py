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
    temperature: float = 0.7  # Increased for more comprehensive and creative responses
    max_tokens: int = 8000  # Increased significantly for long professional reports
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
                        "You are a senior penetration tester and security researcher with 10+ years of experience. "
                        "You write comprehensive, professional vulnerability reports following industry standards (OWASP, NIST, SANS). "
                        "You MUST respond with valid JSON matching the exact schema provided. "
                        "CRITICAL INSTRUCTIONS: "
                        "1. Respect character limits (min_length and max_length) - these are HARD requirements "
                        "2. Generate COMPLETE, COMPREHENSIVE reports - this is a professional deliverable "
                        "3. Include ALL required technical details, examples, and references "
                        "4. Use industry-standard terminology and frameworks "
                        "5. Provide actionable, specific guidance with code examples where applicable "
                        "6. Quality AND quantity are both essential - meet minimum character counts with substantial content"
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

        max_retries = 5  # Increased retries for better reliability
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                with httpx.Client(timeout=120.0) as client:  # Increased timeout for longer generations
                    r = client.post(self.api_url, headers=headers, json=payload)
                    r.raise_for_status()
                    data = r.json()

                content = data["choices"][0]["message"]["content"].strip()
                
                # Basic quality check - ensure response has substance
                if len(content) < 100:
                    raise ValueError(f"Response too short ({len(content)} chars) - likely incomplete")
                
                return content
                
            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code == 429:  # Rate limit
                    retry_count += 1
                    if retry_count < max_retries:
                        import time
                        wait_time = min(2 ** retry_count, 30)  # Exponential backoff, max 30s
                        print(f"⚠️  Rate limited. Retrying in {wait_time}s... (attempt {retry_count}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                elif e.response.status_code >= 500:  # Server error
                    retry_count += 1
                    if retry_count < max_retries:
                        import time
                        wait_time = 5
                        print(f"⚠️  Server error. Retrying in {wait_time}s... (attempt {retry_count}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                raise RuntimeError(f"Mistral API error: {e.response.status_code} - {e.response.text}")
            except (httpx.TimeoutException, httpx.ConnectError, httpx.ReadTimeout) as e:
                last_error = e
                retry_count += 1
                if retry_count < max_retries:
                    import time
                    wait_time = 5
                    print(f"⚠️  Network error: {type(e).__name__}. Retrying in {wait_time}s... (attempt {retry_count}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                raise RuntimeError(f"Network error after {max_retries} retries: {str(e)}")
            except json.JSONDecodeError as e:
                last_error = e
                retry_count += 1
                if retry_count < max_retries:
                    print(f"⚠️  Invalid JSON response. Retrying... (attempt {retry_count}/{max_retries})")
                    continue
                raise RuntimeError(f"Failed to parse API response as JSON: {str(e)}")
            except Exception as e:
                last_error = e
                retry_count += 1
                if retry_count >= max_retries:
                    raise RuntimeError(f"Failed after {max_retries} retries: {str(e)}")
                print(f"⚠️  Unexpected error: {type(e).__name__}. Retrying... (attempt {retry_count}/{max_retries})")
                import time
                time.sleep(2)
        
        raise RuntimeError(f"Failed to generate report after {max_retries} retries. Last error: {str(last_error)}")

    def generate_structured(
        self, 
        prompt: str, 
        schema: Type[BaseModel],
        max_attempts: int = 3
    ) -> BaseModel:
        """
        Generate structured output matching a Pydantic schema with validation retry.
        
        Args:
            prompt: The prompt to send to the LLM
            schema: Pydantic model class defining the expected structure
            max_attempts: Maximum validation retry attempts (default: 3)
            
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
- Output ONLY valid JSON, no markdown code blocks, no explanations
- Include ALL required fields defined in the schema
- Follow field descriptions carefully for content guidelines and requirements
- For string fields: Meet BOTH min_length and max_length character requirements (characters, not words)
- For list fields: Provide between min_items and max_items number of items
- Each list item must be substantial (minimum 30-50 characters with real content)
- Character limits are HARD REQUIREMENTS - you MUST stay within bounds
- Generate comprehensive, professional content that meets minimum lengths
- Quality AND quantity are both essential - be thorough and detailed
- Use proper formatting, paragraphs, and structure in long text fields
- All references must be in format: [Title](URL) with real, functional URLs
"""
        
        last_error = None
        last_response = None
        
        # Try to generate and validate with retries
        for attempt in range(max_attempts):
            try:
                # Generate response
                raw_response = self._call(enhanced_prompt)
                last_response = raw_response
                
                # Parse and validate
                try:
                    # Handle markdown code blocks if present
                    cleaned_response = raw_response
                    if "```json" in cleaned_response:
                        cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
                    elif "```" in cleaned_response:
                        cleaned_response = cleaned_response.split("```")[1].split("```")[0].strip()
                    
                    # Parse JSON
                    data = json.loads(cleaned_response)
                    
                    # Validate against schema
                    validated = schema(**data)
                    
                    print(f"✅ Successfully generated and validated report (attempt {attempt + 1}/{max_attempts})")
                    return validated
                    
                except json.JSONDecodeError as e:
                    last_error = e
                    print(f"❌ JSON parsing failed (attempt {attempt + 1}/{max_attempts}): {str(e)[:100]}")
                    if attempt < max_attempts - 1:
                        enhanced_prompt += f"\n\nPREVIOUS ATTEMPT FAILED: Invalid JSON format. {str(e)[:200]}. Please generate VALID JSON only."
                        continue
                    raise ValueError(f"Failed to parse JSON response after {max_attempts} attempts: {e}\n\nLast response: {raw_response[:500]}")
                
                except ValueError as e:
                    last_error = e
                    error_msg = str(e)
                    print(f"❌ Schema validation failed (attempt {attempt + 1}/{max_attempts}): {error_msg[:150]}")
                    
                    # Check for specific validation errors and provide feedback
                    if "min_length" in error_msg or "max_length" in error_msg:
                        enhanced_prompt += f"\n\nPREVIOUS ATTEMPT FAILED: Character length validation error. {error_msg[:300]}. Please adjust content length to meet requirements."
                    elif "min_items" in error_msg or "max_items" in error_msg:
                        enhanced_prompt += f"\n\nPREVIOUS ATTEMPT FAILED: List size validation error. {error_msg[:300]}. Please provide the correct number of items."
                    else:
                        enhanced_prompt += f"\n\nPREVIOUS ATTEMPT FAILED: {error_msg[:300]}. Please fix and regenerate."
                    
                    if attempt < max_attempts - 1:
                        continue
                    raise ValueError(f"Failed to validate response against schema after {max_attempts} attempts: {e}\n\nLast parsed data: {str(data)[:500]}")
                
            except Exception as e:
                last_error = e
                if "Failed to parse JSON response" in str(e) or "Failed to validate response" in str(e):
                    raise  # Re-raise our formatted errors
                print(f"❌ Generation error (attempt {attempt + 1}/{max_attempts}): {str(e)[:100]}")
                if attempt >= max_attempts - 1:
                    raise RuntimeError(f"Failed to generate structured output after {max_attempts} attempts: {str(e)}")
                import time
                time.sleep(2)  # Brief pause before retry
        
        # Should not reach here, but just in case
        raise RuntimeError(f"Failed to generate valid structured output after {max_attempts} attempts. Last error: {str(last_error)}")
