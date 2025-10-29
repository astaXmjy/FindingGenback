from pydantic import BaseModel, Field
from typing import List, Optional

class TemplateOneOutput(BaseModel):
    """Structured output for Template 1 - Detailed pentest format"""
    
    title: str = Field(description="Finding title/name")
    
    summary: str = Field(
        description="Concise 1-2 sentence summary of the finding",
        min_length=50,
        max_length=300
    )
    
    vulnerability_overview: str = Field(
        description="General description of vulnerability class (OWASP-style), 150-250 words",
        min_length=200,
        max_length=600
    )
    
    finding_details: str = Field(
        description="Specific issue details with root cause and evidence, 150-300 words",
        min_length=200,
        max_length=800
    )
    
    impacts: str = Field(
        description="Security and business impact in one paragraph, 100-200 words",
        min_length=150,
        max_length=500
    )
    
    recommendations: List[str] = Field(
        description="5-7 detailed, actionable remediation steps",
        min_items=5,
        max_items=7
    )
    
    proof_of_concept: List[str] = Field(
        description="4-6 clear reproduction steps",
        min_items=4,
        max_items=6
    )
    
    references: List[str] = Field(
        description="4-7 authoritative links in format: [Title](URL)",
        min_items=4,
        max_items=7
    )


class TemplateCoreOutput(BaseModel):
    """Structured output for Template 2 - Core format"""
    
    title: str = Field(description="Finding title/name")
    
    summary: str = Field(
        description="Concise 2-3 sentence summary",
        min_length=50,
        max_length=300
    )
    
    description: str = Field(
        description="Comprehensive technical description in 2-3 paragraphs, 300-500 words",
        min_length=400,
        max_length=1200
    )
    
    severity: str = Field(
        description="Detailed impact analysis in 1-2 paragraphs with severity rating, 150-300 words",
        min_length=200,
        max_length=700
    )
    
    suggested_fix: str = Field(
        description="Comprehensive remediation guidance organized in sections (Immediate Actions, Permanent Fixes, Additional Measures), 300-500 words",
        min_length=400,
        max_length=1200
    )
    
    proof_of_concept: List[str] = Field(
        description="4-6 detailed reproduction steps with commands",
        min_items=4,
        max_items=6
    )
    
    references: List[str] = Field(
        description="5-8 authoritative links in format: [Title](URL)",
        min_items=5,
        max_items=8
    )