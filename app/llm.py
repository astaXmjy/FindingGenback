import os
from typing import Type
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


def get_structured_llm(schema: Type[BaseModel]) -> ChatOpenAI:

    api_key = os.getenv("OPENAI_API_KEY", "")
  
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini-2024-07-18")
    
    llm = ChatOpenAI(
            model=model,
            api_key=api_key
        )
    
    structured_llm = llm.with_structured_output(
        schema,
        method="json_schema"
    )
    
    return structured_llm
