from pydantic import BaseModel, Field
from typing import List, Optional

class TemplateOneOutput(BaseModel):
    """Structured output for Template 1 - Detailed pentest format"""
    
    title: str = Field(description="Finding title/name")
    
    summary: str = Field(
        description="String. 2-3 sentence summary: what vulnerability was found, where, potential impact."
    )
    
    vulnerability_overview: str = Field(
        description="String. General description of vulnerability class: what it is, how it works, attack vectors, why dangerous."
    )
    
    finding_details: str = Field(
        description="String. Technical analysis: precise location, root cause, technical details, evidence."
    )
    
    impacts: str = Field(
        description="String. Impact analysis: attack scenarios, CIA triad, business consequences, compliance."
    )
    
    recommendations: List[str] = Field(
        description="List of 6-8 strings. Each starts with action verb and provides actionable guidance."
    )
    
    proof_of_concept: List[str] = Field(
        description="List of 6-8 strings. Each string is one step. Format: 'Step 1: ...', 'Step 2: ...'."
    )
    
    references: List[str] = Field(
        description="List of 6-8 strings. Each is markdown link [Title](URL). Include OWASP, CWE, NIST, docs."
    )




class TemplateCoreOutput(BaseModel):
    """Structured output for Template 2 - Core comprehensive format"""
    
    title: str = Field(description="Finding title/name")
    
    summary: str = Field(
        description="String. Executive summary in 3-4 sentences: what was found, where, why it matters, risk level."
    )
    
    description: str = Field(
        description="String. Comprehensive technical description covering: specific finding, vulnerability context, application risk, technical details. Write in paragraphs."
    )
    
    severity: str = Field(
        description="String. Severity analysis covering: technical impact, business impact, risk rating with justification."
    )
    
    suggested_fix: str = Field(
        description="String. Remediation guidance with sections: IMMEDIATE ACTIONS, PERMANENT FIXES, VALIDATION, PREVENTION."
    )
    
    proof_of_concept: List[str] = Field(
        description="List of 6-8 strings. Each string is one step. Format: 'Step 1: ...', 'Step 2: ...'. Keep concise."
    )
    
    references: List[str] = Field(
        description="List of 7-8 strings. Each is markdown link [Title](URL). Include OWASP, CWE, NIST, technical docs."
    )

