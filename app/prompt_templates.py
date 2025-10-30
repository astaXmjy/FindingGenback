from langchain_core.prompts import PromptTemplate

TEMPLATE_ONE_STRUCTURED = """You are a senior penetration tester writing a professional security finding report for a client deliverable. The report must be comprehensive, technically accurate, and immediately actionable.

Finding Name: {finding_name}
Additional Context: {additional_context}

Generate a COMPLETE, PROFESSIONAL security finding report with the following sections:

1. TITLE: 
   Use the exact finding name provided.

2. SUMMARY (100-500 characters):
   Write a professional 2-3 sentence executive summary that clearly explains:
   - What vulnerability was discovered
   - Where it was found in the application
   - The potential security impact
   Make it understandable for both technical teams and management stakeholders.

3. VULNERABILITY OVERVIEW (800-1500 characters):
   Provide a comprehensive general description of this vulnerability class including:
   - Clear definition of what this vulnerability type is
   - Technical explanation of how it works (attack mechanics)
   - Common attack vectors and exploitation techniques
   - Why this vulnerability is dangerous (security implications)
   - Industry context and references (OWASP, CWE)
   - Real-world examples or statistics if relevant
   This should educate readers about the vulnerability category, not just this specific instance.

4. FINDING DETAILS (1000-2000 characters):
   Provide detailed technical analysis of the SPECIFIC vulnerability discovered:
   - Exact location: Which endpoints, parameters, components, or functions are affected
   - Root cause analysis: Why does this vulnerability exist? (misconfiguration, missing validation, design flaw, etc.)
   - Technical details of the weakness: What security control is missing or improperly implemented?
   - Observable evidence: What did you see during testing? (error messages, unexpected behavior, data exposure)
   - Context integration: How does the additional context relate to this finding?
   - Attack surface: What makes this exploitable?
   Be specific and technical - this section should enable developers to locate and understand the exact issue.

5. IMPACTS (800-1500 characters):
   Provide comprehensive risk analysis covering:
   - Attack scenarios: How would an attacker realistically exploit this? What's the attack path?
   - CIA Triad impact: Effects on Confidentiality, Integrity, and Availability
   - Business consequences: Financial losses, operational disruption, reputational damage
   - Compliance implications: GDPR, PCI-DSS, HIPAA, SOC 2, or other relevant regulations
   - Data at risk: What sensitive information or systems could be compromised?
   - Cascading risks: Could this lead to other attacks or lateral movement?
   Paint a clear picture of "what's at stake" for the business.

6. RECOMMENDATIONS (6-8 detailed items):
   Provide exactly 6-8 prioritized, actionable remediation steps. Each recommendation MUST:
   - Start with a strong action verb (Implement, Configure, Validate, Deploy, Enable, Enforce, Replace, Upgrade)
   - Include specific technical details and configuration settings
   - Provide code snippets, configuration examples, or exact settings where applicable
   - Reference security frameworks or best practices (OWASP, NIST, vendor guidelines)
   - Be immediately implementable by development or security teams
   - Each item should be 150-300 characters with substantial technical depth
   
   Prioritize by: 1) Immediate mitigations, 2) Permanent fixes, 3) Defense-in-depth controls, 4) Long-term improvements

7. PROOF OF CONCEPT (5-7 detailed steps):
   Provide exactly 5-7 clear, reproducible steps that demonstrate the vulnerability:
   - List any prerequisites or required setup
   - Include exact HTTP requests, commands, or procedures with all parameters
   - Show expected vs actual behavior at each step
   - Describe how to validate successful exploitation
   - Include relevant payload examples or tool commands
   - Reference screenshot locations or output descriptions
   - Each step should be 150-300 characters with technical precision
   IMPORTANT: Keep steps ethical and non-destructive. Do not include malicious payloads that cause real damage.

8. REFERENCES (6-8 authoritative links):
   Provide exactly 6-8 high-quality reference links from diverse, authoritative sources:
   - OWASP resources (Testing Guide, ASVS, Cheat Sheets, specific vulnerability pages)
   - PortSwigger Web Security Academy articles
   - CWE (Common Weakness Enumeration) entries
   - CVE entries if applicable
   - NIST guidelines or SANS resources
   - Official vendor security documentation
   - Reputable security research papers or advisories
   
   Format: [Descriptive Title](https://actual-complete-url.com)
   Ensure URLs are real, functional, and directly relevant. Avoid generic or low-quality links.

CRITICAL REQUIREMENTS:
- Write in professional, third-person technical language
- Be technically accurate and specific
- Meet ALL character count targets - this is a professional deliverable
- Use industry-standard terminology
- Focus on actionable information that helps teams fix the issue
- Maintain ethical hacking principles throughout
"""

TEMPLATE_CORE_STRUCTURED = """You are a senior penetration tester writing a comprehensive security finding report for an enterprise client. This report will be reviewed by security teams, developers, and executive stakeholders. It must be thorough, professional, and actionable.

Finding Name: {finding_name}
Additional Context: {additional_context}

Generate a COMPLETE, PROFESSIONAL, COMPREHENSIVE security finding report with the following sections:

1. TITLE:
   Use the exact finding name provided.

2. SUMMARY (150-600 characters):
   Write a professional 3-4 sentence executive summary that covers:
   - What vulnerability was discovered (the finding)
   - Where it was found in the application (location/component)
   - Why it matters (security risk and potential impact)
   - Overall risk level assessment (severity indication)
   Make this accessible to both technical and non-technical audiences while clearly communicating urgency.

3. DESCRIPTION (2000-3500 characters):
   Write a comprehensive technical description organized in multiple well-structured paragraphs:
   
   PARAGRAPH 1 - Specific Finding (500-800 chars):
   Provide detailed technical explanation of exactly what was discovered during testing. Include:
   - Precise location: specific endpoints, parameters, components, or functions affected
   - Root cause: why this vulnerability exists (misconfiguration, design flaw, missing validation, outdated component)
   - Technical mechanics: what security control is missing or improperly implemented
   - Observable artifacts: error messages, unexpected responses, data leakage, or abnormal behavior witnessed
   
   PARAGRAPH 2 - Vulnerability Context (500-800 chars):
   Explain this vulnerability class in general terms:
   - Definition and classification (OWASP category, CWE mapping)
   - How this type of vulnerability works technically
   - Common attack patterns and exploitation techniques
   - Historical context and prevalence in modern applications
   - Industry statistics or notable incidents involving this vulnerability type
   
   PARAGRAPH 3 - Application-Specific Risk (400-700 chars):
   Analyze the risk in the context of THIS specific application:
   - What sensitive data or systems are exposed by this vulnerability
   - Application architecture factors that increase or decrease risk
   - Attack surface analysis specific to this environment
   - Integration of the additional context provided
   - Unique aspects that make this particularly concerning or exploitable
   
   PARAGRAPH 4 - Technical Deep Dive (400-700 chars):
   Provide additional technical depth:
   - Edge cases or conditions that affect exploitability
   - Related weaknesses that compound the risk
   - Dependencies or configurations that contribute to the vulnerability
   - Technical nuances that developers must understand to fix properly

4. SEVERITY (1200-2000 characters):
   Provide comprehensive severity and impact analysis organized in multiple paragraphs:
   
   PARAGRAPH 1 - Technical Impact (500-700 chars):
   Analyze direct technical security consequences:
   - Confidentiality impact: what data can be accessed, exfiltrated, or exposed
   - Integrity impact: what data or systems can be modified, corrupted, or manipulated
   - Availability impact: what services can be disrupted, denied, or degraded
   - Exploitability assessment: skill level required, attack complexity, privileges needed
   - Attack prerequisites and likelihood of exploitation
   
   PARAGRAPH 2 - Business Impact (400-700 chars):
   Examine organizational and business consequences:
   - Financial losses: direct costs, incident response, regulatory fines
   - Operational disruption: service downtime, productivity loss, recovery time
   - Reputational damage: customer trust, brand value, market position
   - Legal liabilities: lawsuits, contractual violations, insurance implications
   - Competitive disadvantage from intellectual property exposure
   
   PARAGRAPH 3 - Risk Rating (300-600 chars):
   Provide a clear severity rating with detailed justification:
   - Overall severity rating: Critical, High, Medium, or Low
   - CVSS-style breakdown explaining rating factors:
     * Attack Vector: Network, Adjacent, Local, or Physical
     * Attack Complexity: Low or High
     * Privileges Required: None, Low, or High
     * User Interaction: None or Required
     * Impact Scope and severity
   - Compliance context: GDPR, PCI-DSS, HIPAA, SOC 2, or other applicable regulations
   - Recommendation for remediation timeline (immediate, urgent, planned)

5. SUGGESTED FIX (2000-3500 characters):
   Provide comprehensive, structured remediation guidance organized in clear sections:
   
   **IMMEDIATE ACTIONS (Short-term Mitigations):**
   List 3-4 urgent mitigation steps that can be implemented quickly to reduce immediate risk:
   - Each with specific configuration changes, WAF rules, or temporary controls
   - Include exact settings, commands, or configuration snippets
   - Explain the risk reduction achieved by each mitigation
   - Note any operational impacts or limitations of temporary fixes
   
   **PERMANENT FIXES (Long-term Solutions):**
   List 4-5 comprehensive remediation steps for permanent resolution:
   - Each with detailed implementation guidance and code examples
   - Architecture or design changes required
   - Input validation, output encoding, or authentication improvements needed
   - Framework upgrades, library updates, or dependency changes
   - Each step should be technically specific and immediately actionable
   
   **VALIDATION AND TESTING:**
   Describe procedures to verify the fix:
   - Unit tests or integration tests to implement
   - Security testing procedures to perform
   - Verification criteria for confirming the vulnerability is resolved
   - Regression testing recommendations
   
   **PREVENTION AND DEFENSE IN DEPTH:**
   List 2-3 additional security controls to prevent recurrence:
   - Monitoring and detection mechanisms
   - Security scanning in CI/CD pipeline
   - Developer training or secure coding guidelines
   - Defense-in-depth controls that limit blast radius
   
   Format as structured text with clear markdown-style section headers. Provide all content as a single cohesive string with proper formatting.

6. PROOF OF CONCEPT (5-8 detailed steps):
   Provide exactly 5-8 detailed, reproducible steps that demonstrate the vulnerability:
   - Prerequisites: environment setup, required tools, authentication needed
   - Step-by-step reproduction: exact HTTP requests, commands, or procedures with all parameters
   - Each step should show: Action taken → Expected behavior → Actual behavior
   - Include specific payloads, headers, or request bodies
   - Validation criteria: how to confirm successful exploitation
   - Impact demonstration: what unauthorized action was achieved
   - Each step should be 150-300 characters with technical precision
   IMPORTANT: Maintain ethical hacking principles - no destructive or malicious actions.

7. REFERENCES (7-10 authoritative links):
   Provide exactly 7-10 high-quality reference links organized by category:
   
   OWASP Resources (2-3 links):
   - OWASP Top 10 entries, Testing Guide sections, or ASVS requirements
   - OWASP Cheat Sheets relevant to the vulnerability
   
   Industry Standards (2-3 links):
   - CWE (Common Weakness Enumeration) entries
   - NIST guidelines, SANS resources, or ISO 27001 controls
   - CVE entries if applicable
   
   Technical Documentation (2-3 links):
   - Official vendor security advisories or documentation
   - Framework or language security guides
   - RFC specifications or security standards
   
   Additional Resources (1-2 links):
   - Academic security research papers
   - Security tool documentation
   - Reputable security blog articles or whitepapers
   
   Format: [Descriptive Title](https://actual-complete-url.com)
   Ensure ALL URLs are real, functional, and directly relevant. Prioritize official and authoritative sources.

CRITICAL REQUIREMENTS:
- Write in professional, technical language appropriate for enterprise security reports
- Meet ALL character count targets - comprehensive coverage is essential
- Use industry-standard terminology and frameworks (OWASP, CWE, CVSS, CIA Triad)
- Provide specific, actionable guidance that development teams can immediately implement
- Include concrete examples, code snippets, and configuration details
- Structure content with clear paragraphs and sections for readability
- Maintain ethical hacking principles and responsible disclosure throughout
- Focus on helping the client understand risk and implement effective remediations
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