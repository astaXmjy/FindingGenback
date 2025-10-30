from langchain_core.prompts import PromptTemplate

TEMPLATE_ONE_STRUCTURED = """Generate a professional penetration testing finding report.

Finding Name: {finding_name}
Additional Context: {additional_context}

Generate a complete security finding report with:

1. TITLE: Use the finding name as-is

2. SUMMARY: 1-2 sentences describing what was found

3. VULNERABILITY OVERVIEW: 
   - Concise general description of this vulnerability class
   - How it works and common attack vectors
   - Why it's dangerous
   (CRITICAL: Maximum 500 characters - be extremely concise)

4. FINDING DETAILS:
   - Specific technical details of what was discovered
   - Where it was found (endpoints, parameters, components)
   - Root cause analysis
   - Observable evidence
   (150-300 words, incorporate additional context if provided)

5. IMPACTS:
   - How attackers could exploit this
   - What access/damage is possible
   - Business and compliance consequences
   (CRITICAL: Maximum 400 characters - be very concise)

6. RECOMMENDATIONS:
   Provide exactly 5-7 actionable remediation steps. Each MUST:
   - Start with action verb (Implement, Configure, Validate, etc.)
   - Be specific with technical details
   - Include configuration examples or code patterns
   - Be immediately actionable

7. PROOF OF CONCEPT:
   Provide exactly 4-6 clear reproduction steps:
   - Include prerequisites if needed
   - Show exact commands/requests
   - Describe expected results
   - Keep ethical and non-destructive

8. REFERENCES:
   Provide exactly 4-7 authoritative links:
   - OWASP resources
   - PortSwigger articles
   - CWE/CVE entries
   - Vendor documentation
   Format: [Link Title](https://actual-url.com)

Be concise, professional, and technically accurate. Focus on quality over length.
"""

TEMPLATE_CORE_STRUCTURED = """Generate a professional security finding report.

Finding Name: {finding_name}
Additional Context: {additional_context}

Generate a complete security finding report with:

1. TITLE: Use the finding name as-is

2. SUMMARY: 2-3 sentences describing what was found and why it matters

3. DESCRIPTION:
   Write 2-3 paragraphs (300-500 words total):
   - Paragraph 1: Specific technical details of what was found
   - Paragraph 2: General explanation of this vulnerability type
   - Paragraph 3: Risk context for this specific application

4. SEVERITY:
   Write 1-2 paragraphs (150-300 words) covering:
   - Direct security impact and exploitation scenarios
   - Business and compliance consequences
   - Severity rating (Critical/High/Medium/Low) with justification

5. SUGGESTED FIX:
   Comprehensive remediation guidance (300-500 words) organized as:
   
   **Immediate Actions (Short-term mitigations):**
   1. [Specific mitigation step]
   2. [Another mitigation]
   
   **Permanent Fixes (Long-term solutions):**
   1. [Detailed fix with technical specifics]
   2. [Architecture changes needed]
   3. [Security controls to implement]
   
   **Additional Security Measures:**
   1. [Defense-in-depth controls]
   2. [Monitoring mechanisms]
   3. [Testing procedures]
   
   (Provide all content as a single formatted string, not as separate lists)

6. PROOF OF CONCEPT:
   Provide exactly 4-6 detailed steps with:
   - Prerequisites listed
   - Exact commands/requests
   - Expected vs actual results
   - Clear validation of the vulnerability

7. REFERENCES:
   Provide exactly 5-8 authoritative links organized by category:
   - OWASP resources
   - Industry standards (CWE, NIST)
   - Technical documentation
   - Additional reading
   Format: [Link Title](https://actual-url.com)

Be technical, concise, and actionable. Quality over quantity.
"""

PROMPT_ONE_STRUCTURED = PromptTemplate.from_template(TEMPLATE_ONE_STRUCTURED)
PROMPT_CORE_STRUCTURED = PromptTemplate.from_template(TEMPLATE_CORE_STRUCTURED)

def get_prompt_structured(template_key: str) -> PromptTemplate:
    """Get structured prompt template"""
    if template_key == "one":
        return PROMPT_ONE_STRUCTURED
    elif template_key == "core":
        return PROMPT_CORE_STRUCTURED
    else:
        raise ValueError(f"Invalid template key: {template_key}")