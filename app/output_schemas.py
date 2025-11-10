from pydantic import BaseModel, Field
from typing import List, Optional

class TemplateOneOutput(BaseModel):
    """Structured output for Template 1 - Detailed pentest format"""
    
    title: str = Field(description="Finding title/name")
    
    summary: str = Field(
        description="Professional 2-3 sentence summary (150-300 characters) clearly explaining what vulnerability was found, where, and its potential impact. Understandable by both technical and non-technical stakeholders."
    )
    
    vulnerability_overview: str = Field(
        description="Comprehensive general description of this vulnerability class (500-1000 characters). Explain: What this vulnerability type is, how it works technically, common attack vectors, why it's dangerous, industry context (OWASP/CWE references). Single focused paragraph."
    )
    
    finding_details: str = Field(
        description="MUST BE A STRING (not a dict/object). Detailed technical analysis (800-1500 characters) in paragraph form. Include: Precise location (endpoints, parameters, components), root cause analysis, technical details of the weakness, observable evidence, how additional context relates to the finding. Be specific and concise."
    )
    
    impacts: str = Field(
        description="Comprehensive impact analysis (500-1000 characters). Cover: Attack scenarios, CIA triad impact (Confidentiality, Integrity, Availability), business consequences (financial, operational, reputational), compliance implications (GDPR, PCI-DSS, etc.), data/systems at risk. Single focused paragraph."
    )
    
    recommendations: List[str] = Field(
        description="MUST BE A LIST OF 6-8 STRINGS. Each recommendation (80-150 characters) starts with an action verb (Implement, Configure, Validate, Deploy, Enable, Enforce) and provides specific, actionable guidance. Prioritized by effectiveness."
    )
    
    proof_of_concept: List[str] = Field(
        description="MUST BE A LIST OF 6-8 STRINGS (not objects/dicts). Each string is one reproducible step (100-200 characters). Include: prerequisites, exact commands/requests with parameters, expected vs actual behavior, validation. Format: 'Step 1: Action...', 'Step 2: Action...'. Keep ethical and non-destructive."
    )
    
    references: List[str] = Field(
        description="MUST BE A LIST OF 6-8 STRINGS. Each is a markdown link: [Title](URL). Include: 2 OWASP links, 2 CWE/CVE/NIST links, 2 technical documentation links, 2 additional sources. Use real, functional URLs only."
    )




class TemplateCoreOutput(BaseModel):
    """Structured output for Template 2 - Core comprehensive format"""
    
    title: str = Field(description="Finding title/name")
    
    summary: str = Field(
        description="Executive summary (200-400 characters) in 3-4 sentences covering: What was found, where it was found, why it matters, overall risk level. Clearly communicate severity to stakeholders."
    )
    
    description: str = Field(
        description="MUST BE A STRING (not an object). Comprehensive technical description (1500-2500 characters). Write in paragraph form with multiple paragraphs covering: 1) Specific finding with precise location and root cause, 2) Vulnerability context explaining this class of vulnerability, 3) Application-specific risk analysis, 4) Technical details and related weaknesses. Be concise yet thorough."
    )
    
    severity: str = Field(
        description="MUST BE A STRING. Detailed severity and impact analysis (800-1500 characters). Write in paragraph form covering: 1) Technical impact (CIA triad, exploitability), 2) Business impact (operational, financial, reputational), 3) Risk rating with CVSS-style justification. Be focused and actionable."
    )
    
    suggested_fix: str = Field(
        description="MUST BE A STRING. Comprehensive remediation guidance (1500-2500 characters). Structure with clear sections: IMMEDIATE ACTIONS (3-4 urgent mitigations), PERMANENT FIXES (4-5 comprehensive solutions with examples), VALIDATION (testing procedures), PREVENTION (controls to prevent recurrence). Be specific and actionable."
    )
    
    proof_of_concept: List[str] = Field(
        description="MUST BE A LIST OF 6-8 STRINGS (not objects). Each string is one reproducible step (100-200 characters). Include: prerequisites, exact commands/requests with parameters, expected vs actual behavior, validation. Format: 'Step 1: Action...', 'Step 2: Action...'. Keep concise and ethical."
    )
    
    references: List[str] = Field(
        description="MUST BE A LIST OF 7-8 STRINGS. Each is a markdown link: [Title](URL). Include: 2 OWASP links, 2 CWE/NIST links, 2 technical documentation links, 2 additional authoritative sources. Use real, functional URLs only."
    )

