"""
Simple test script to demonstrate the efficient structured output implementation.
This follows the pattern from your example code.
"""

from app.llm import get_structured_llm
from app.output_schemas import TemplateOneOutput, TemplateCoreOutput
from app.prompt_templates import get_prompt_template
import os
from dotenv import load_dotenv

load_dotenv()

def test_template_one():
    """Test Template One (detailed pentest format)"""
    print("\n" + "="*80)
    print("Testing Template One - Detailed Pentest Format")
    print("="*80 + "\n")
    
    # Get structured LLM with schema
    structured_llm = get_structured_llm(TemplateOneOutput)
    
    # Get and format prompt
    prompt_template = get_prompt_template("one")
    prompt = prompt_template.format(
        finding_name="SQL Injection",
        additional_context="Found in login form, user input not sanitized"
    )
    
    # Invoke - returns validated Pydantic object
    print("🤖 Generating report...")
    result = structured_llm.invoke(prompt)
    
    # Access attributes directly
    print(f"\n✅ Generated report:")
    print(f"Title: {result.title}")
    print(f"Summary: {result.summary[:100]}...")
    print(f"Recommendations count: {len(result.recommendations)}")
    print(f"Proof of Concept steps: {len(result.proof_of_concept)}")
    print(f"References count: {len(result.references)}")
    
    # Type check
    print(f"\nType: {type(result)}")  # <class 'TemplateOneOutput'>
    
    return result


def test_template_core():
    """Test Template Core (comprehensive format)"""
    print("\n" + "="*80)
    print("Testing Template Core - Comprehensive Format")
    print("="*80 + "\n")
    
    # Get structured LLM with schema
    structured_llm = get_structured_llm(TemplateCoreOutput)
    
    # Get and format prompt
    prompt_template = get_prompt_template("core")
    prompt = prompt_template.format(
        finding_name="Cross-Site Scripting (XSS)",
        additional_context="Reflected XSS in search parameter"
    )
    
    # Invoke - returns validated Pydantic object
    print("🤖 Generating report...")
    result = structured_llm.invoke(prompt)
    
    # Access attributes directly
    print(f"\n✅ Generated report:")
    print(f"Title: {result.title}")
    print(f"Summary: {result.summary[:100]}...")
    print(f"Description: {result.description[:100]}...")
    print(f"Severity: {result.severity[:100]}...")
    print(f"Proof of Concept steps: {len(result.proof_of_concept)}")
    print(f"References count: {len(result.references)}")
    
    # Type check
    print(f"\nType: {type(result)}")  # <class 'TemplateCoreOutput'>
    
    # Convert to dict if needed
    result_dict = result.model_dump()
    print(f"\nCan convert to dict: {isinstance(result_dict, dict)}")
    
    return result


if __name__ == "__main__":
    print("\n🚀 Testing Efficient Structured Output Implementation")
    print("This implementation uses OpenAI's json_schema method for 100% schema compliance")
    
    try:
        # Test both templates
        result_one = test_template_one()
        result_core = test_template_core()
        
        print("\n" + "="*80)
        print("✅ All tests passed!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
