from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class TemplateOneOutput(BaseModel):
    """Structured output for Template 1 - Detailed pentest format"""
    
    title: str = Field(description="Finding title/name")
    
    summary: str = Field(
        description="Professional 2-3 sentence summary clearly explaining what vulnerability was found, where, and its potential impact. Should be understandable by both technical and non-technical stakeholders.",
        min_length=80,
        max_length=500
    )
    
    vulnerability_overview: str = Field(
        description="Comprehensive general description of this vulnerability class. Explain: What this vulnerability type is, How it works technically, Common attack vectors and exploitation methods, Why it's dangerous, Industry context (OWASP/CWE references).",
        min_length=300,
        max_length=1500
    )
    
    finding_details: str = Field(
        description="MUST BE A STRING (not a dict/object). Detailed technical analysis in paragraph form of the specific vulnerability discovered. Include: Precise location (endpoints, parameters, components), Root cause analysis (why it exists), Technical details of the weakness, Observable evidence and artifacts, How additional context relates to the finding.",
        min_length=300,
        max_length=2000
    )
    
    impacts: str = Field(
        description="Comprehensive impact analysis covering: Attack scenarios and exploitation possibilities, CIA triad impact (Confidentiality, Integrity, Availability), Business consequences (financial, operational, reputational), Compliance and legal implications (GDPR, PCI-DSS, etc.), Data or systems at risk.",
        min_length=300,
        max_length=1500
    )
    
    recommendations: List[str] = Field(
        description="List of 5-8 detailed, actionable remediation steps prioritized by effectiveness. Each recommendation MUST: Start with a strong action verb (Implement, Configure, Validate, Deploy, Enable, Enforce), Provide specific technical details and configuration examples, Be immediately actionable by development/security teams.",
        min_items=5,
        max_items=8
    )
    
    proof_of_concept: List[str] = Field(
        description="MUST BE A LIST OF STRINGS (not objects/dicts). 5-8 detailed, reproducible steps demonstrating the vulnerability. Each step should be a single string. Include: Prerequisites and initial setup, Exact commands/requests with parameters, Expected vs actual behavior, Validation of successful exploitation. Must be ethical and non-destructive. Example: ['Step 1: Navigate to...', 'Step 2: Enter payload...', etc.]",
        min_items=5,
        max_items=8
    )
    
    references: List[str] = Field(
        description="List of 5-8 authoritative reference links from diverse sources. Include: OWASP resources, PortSwigger articles, CWE/CVE entries, NIST guidelines. Format: [Descriptive Title](https://actual-url.com). Ensure URLs are real and functional.",
        min_items=5,
        max_items=8
    )

    @field_validator('recommendations', 'proof_of_concept', 'references')
    def validate_list_quality(cls, v, info):
        """Ensure list items have substance"""
        field_name = info.field_name
        for item in v:
            if len(item.strip()) < 20:
                raise ValueError(f"{field_name} items must be substantial (minimum 20 characters each)")
        return v


class TemplateCoreOutput(BaseModel):
    """Structured output for Template 2 - Core comprehensive format"""
    
    title: str = Field(description="Finding title/name")
    
    summary: str = Field(
        description="Executive summary in 3-4 sentences covering: What was found, Where it was found, Why it matters, Overall risk level. Should clearly communicate severity to stakeholders.",
        min_length=150,
        max_length=600
    )
    
    description: str = Field(
        description="MUST BE A STRING (not an object). Comprehensive technical description in paragraph form organized in multiple paragraphs: PARAGRAPH 1 (Specific Finding): Detailed technical explanation of what was discovered, exact location, affected components, root cause analysis. PARAGRAPH 2 (Vulnerability Context): General explanation of this vulnerability class, how it works, common attack patterns. PARAGRAPH 3 (Application Context): Risk specific to this application/environment, data at risk, attack surface analysis. PARAGRAPH 4 (Technical Details): Additional technical depth, edge cases, related weaknesses. Target: 2000-3000 characters for thorough professional documentation.",
        min_length=2000,
        max_length=3500
    )
    
    severity: str = Field(
        description="MUST BE A STRING. Detailed severity and impact analysis in paragraph form with multiple paragraphs: PARAGRAPH 1 (Technical Impact): Direct security consequences, CIA triad analysis, exploitability assessment. PARAGRAPH 2 (Business Impact): Operational disruption, financial losses, reputational damage, compliance violations. PARAGRAPH 3 (Risk Rating): Clear severity rating (Critical/High/Medium/Low) with CVSS-style justification explaining each factor. Target: 1200-1800 characters for comprehensive risk assessment.",
        min_length=1200,
        max_length=2000
    )
    
    suggested_fix: str = Field(
        description="MUST BE A STRING. Comprehensive remediation guidance in paragraph form organized in clear sections with detailed implementation guidance: IMMEDIATE ACTIONS (Short-term mitigations): 3-4 urgent mitigation steps with exact configurations. PERMANENT FIXES (Long-term solutions): 4-5 comprehensive remediation steps with code examples and architecture changes. VALIDATION: Testing procedures to verify fixes. PREVENTION: Security controls to prevent recurrence. Format as structured text with clear section headers. Target: 2000-3000 characters for actionable professional guidance.",
        min_length=2000,
        max_length=3500
    )
    
    proof_of_concept: List[str] = Field(
        description="MUST BE A LIST OF STRINGS (not objects). 5-8 detailed, reproducible steps with technical precision. Each step should be a single string. Include: Environment setup and prerequisites, Exact HTTP requests/commands with full parameters, Expected vs actual responses, Validation criteria, Impact demonstration. Example: ['Step 1: Set up environment...', 'Step 2: Send request...', etc.]. Each step should be 150-300 characters with technical accuracy. Must remain ethical and non-destructive.",
        min_items=5,
        max_items=8
    )
    
    references: List[str] = Field(
        description="MUST BE A LIST OF STRINGS. 7-10 authoritative references organized by category. Include: OWASP resources (Top 10, Testing Guide, ASVS), Industry standards (CWE, NIST, ISO 27001), Technical documentation (RFCs, vendor guides), Academic research and whitepapers, Security tools and resources. Format: [Descriptive Title](https://actual-url.com). Prioritize official and authoritative sources.",
        min_items=7,
        max_items=10
    )

    @field_validator('proof_of_concept', 'references')
    def validate_list_quality(cls, v, info):
        """Ensure list items have substance"""
        field_name = info.field_name
        for item in v:
            if len(item.strip()) < 30:
                raise ValueError(f"{field_name} items must be substantial (minimum 30 characters each)")
        return v