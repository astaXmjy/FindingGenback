import os
import json
from typing import Type
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from dotenv import load_dotenv
 
load_dotenv()


def get_openai_llm_with_structured_output(schema: Type[BaseModel]) -> ChatOpenAI:
    """
    Create an OpenAI LLM instance configured for structured output using LangChain's native capabilities.
    
    Args:
        schema: Pydantic model class defining the expected output structure
        
    Returns:
        ChatOpenAI instance with structured output binding
    """
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable")
    
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini-2024-07-18")
    
    # Get JSON schema for instructions
    json_schema = schema.model_json_schema()
    schema_str = json.dumps(json_schema, indent=2)
    
    # Check if model is a reasoning/preview model that doesn't support temperature/top_p
    is_reasoning_model = any(x in model.lower() for x in ["search-preview", "o1", "reasoning"])
    
    # Create ChatOpenAI instance with optimized parameters
    # Note: gpt-4o-mini supports up to 128k context
    # Reasoning models don't support temperature and top_p parameters
    if is_reasoning_model:
        llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            max_tokens=None,
            max_retries=5,
            timeout=180,
        )
    else:
        llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=0.7,
            max_tokens=None,  # Let model use default, no artificial limit
            top_p=0.95,
            max_retries=5,
            timeout=180,
        )
    
    # Bind structured output with include_raw=False to get clean Pydantic model
    # OpenAI supports native structured outputs via function calling (json_schema method)
    structured_llm = llm.with_structured_output(
        schema, 
        method="json_schema",  # Use OpenAI's native structured outputs
        include_raw=False
    )
    
    return structured_llm


def create_structured_prompt(base_prompt: str, schema: Type[BaseModel]) -> ChatPromptTemplate:
    """
    Create a chat prompt template with schema instructions.
    
    Args:
        base_prompt: The base prompt template string
        schema: Pydantic model class for structured output
        
    Returns:
        ChatPromptTemplate configured for structured output
    """
    json_schema = schema.model_json_schema()
    
    # Extract field names and descriptions
    properties = json_schema.get("properties", {})
    field_info = []
    for field_name, field_spec in properties.items():
        desc = field_spec.get("description", "")
        field_type = field_spec.get("type", "")
        field_info.append(f"- {field_name}: {desc}")
    
    fields_text = "\n".join(field_info)
    
    system_message = f"""You are a senior penetration tester and security researcher writing professional vulnerability reports.

Generate a comprehensive, professional security finding report with the following fields:

{fields_text}

IMPORTANT GUIDELINES:
1. Follow all field descriptions precisely for content requirements
2. Meet minimum and maximum character length requirements
3. For list fields, provide the required number of items (min_items to max_items)
4. Each list item must be substantial and detailed (minimum 50 characters)
5. String fields (like finding_details, description, severity, suggested_fix) must be comprehensive paragraph text, NOT nested objects or dictionaries
6. List fields (like proof_of_concept, recommendations, references) must be arrays of strings, NOT arrays of objects
7. For proof_of_concept: provide step-by-step instructions as simple strings like ["Step 1: Navigate to...", "Step 2: Enter payload...", ...]
8. For recommendations: start each with an action verb (Implement, Configure, Validate, Deploy, etc.)
9. For references: format as markdown links [Title](URL) with real, authoritative sources
10. Maintain professional tone throughout and ensure all content is ethical and non-destructive"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", base_prompt)
    ])
    
    return prompt
