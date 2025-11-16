from langchain_core.prompts import PromptTemplate

# Template One Prompt - Detailed pentest format
TEMPLATE_ONE_PROMPT = """You are a senior penetration tester writing a professional security finding report.

Finding Name: {finding_name}
Additional Context: {additional_context}

Generate a COMPLETE, PROFESSIONAL security finding report following this structure:

# [Finding Title]
Use the exact finding name provided.

## Summary
- Concise summary for the finding (2-3 sentences)
- Clearly explain what was discovered, where it was found, and the potential security impact
- Make it understandable for both technical teams and management stakeholders

## Vulnerability Overview
- General description of this vulnerability type (explain the class of issue, how it works, and how an attacker could exploit it)
- This paragraph must describe the vulnerability type in general terms, not the specific instance
- Include technical explanation of attack mechanics and why this vulnerability is dangerous
- Reference industry standards (OWASP, CWE) where relevant

## Finding Details
- Brief overview of the specific issue: what was found, where it was found, and the potential risk in context
- Write in a professional, explanatory tone
- Root cause and observed evidence (concise bullet points describing the root cause, affected components/endpoints, and what was observed)
- Integrate the additional context provided and explain how it relates to this finding
- Be specific about exact locations and technical details

## Impacts
- One paragraph describing the security impact: how an attacker might exploit the issue, what access or damage it could lead to, and any broader implications (data leakage, supply chain risk, business impact)
- Cover CIA Triad (Confidentiality, Integrity, Availability)
- Include compliance implications if relevant (GDPR, PCI-DSS, HIPAA, SOC 2)
- Keep to a single comprehensive paragraph

## Recommendations
- Detailed, actionable remediation steps
- Use imperative language (Implement, Configure, Validate, Deploy, Enable, Enforce, Replace, Upgrade)
- Provide concrete technical guidance where appropriate (configuration changes, code-level guidance, controls to implement)
- Use bullets and be as specific as possible
- Include code snippets or configuration examples where applicable
- Prioritize by: 1) Immediate mitigations, 2) Permanent fixes, 3) Defense-in-depth controls

## Proof of concept
1. Clear, step-by-step instructions to reproduce the issue or observe the vulnerable behavior
2. Keep steps brief but sufficient to validate the finding (include sample curl requests, HTTP requests/responses, or Burp/console snippets where relevant)
3. List any prerequisites or required setup
4. Include exact commands, requests, or procedures with all parameters
5. Describe how to validate successful reproduction
6. IMPORTANT: Keep steps ethical and non-destructive

## References
- Link to authoritative resources (OWASP, PortSwigger, CWE, vendor docs, CVEs, etc.)
- Format: [Descriptive Title](https://actual-complete-url.com)
- Ensure URLs are real, functional, and directly relevant
- Provide 6-8 high-quality references from diverse sources

CRITICAL REQUIREMENTS:
- Write in professional, third-person technical language
- Be technically accurate and specific
- Use industry-standard terminology
- Focus on actionable information that helps teams fix the issue
- Maintain ethical hacking principles throughout"""

# Template Core Prompt - Core comprehensive format
TEMPLATE_CORE_PROMPT = """You are a senior penetration tester writing a comprehensive security finding report for an enterprise client.

Finding Name: {finding_name}
Additional Context: {additional_context}

Generate a COMPLETE, PROFESSIONAL, COMPREHENSIVE security finding report following this structure:

# [Finding Title]
Use the exact finding name provided.

## Summary
Concise summary for the finding (3-4 sentences).
Cover what vulnerability was discovered, where it was found in the application, why it matters (security risk and potential impact), and overall risk level assessment.
Make this accessible to both technical and non-technical audiences while clearly communicating urgency.

## Description
Brief overview of the issue, what was found, where it was found, and the potential risk in context. This is written in a professional, explanatory tone.

Add comprehensive information about the vulnerability:
- Precise location: specific endpoints, parameters, components, or functions affected
- Root cause: why this vulnerability exists (misconfiguration, design flaw, missing validation, outdated component)
- Technical mechanics: what security control is missing or improperly implemented
- Observable artifacts: error messages, unexpected responses, data leakage, or abnormal behavior witnessed
- Vulnerability context: explain this vulnerability class in general terms (definition, classification, how it works, common attack patterns)
- Application-specific risk: analyze the risk in the context of THIS specific application
- Technical deep dive: edge cases, related weaknesses, dependencies, or configurations that contribute

## Severity
Explanation of the security impact, detailing how an attacker might exploit the issue, what kind of access or damage it could lead to, and any broader implications (e.g., data leaks, supply chain risks). Keep this to a single paragraph.

Provide comprehensive severity and impact analysis covering:
- Technical Impact: analyze direct technical security consequences (Confidentiality, Integrity, Availability impacts, exploitability assessment)
- Business Impact: examine organizational and business consequences (financial losses, operational disruption, reputational damage, legal liabilities)
- Risk Rating: provide clear severity rating with detailed justification (CVSS-style breakdown, compliance context)
- Recommendation for remediation timeline (immediate, urgent, planned)

## Suggested fix
Recommended actions to remediate the issue. Provide very detailed, actionable remediation steps (configuration changes, code-level guidance, compensating controls, testing/validation steps).

Structure your fix recommendations as follows:

**IMMEDIATE ACTIONS (Short-term Mitigations):**
List 3-4 urgent mitigation steps that can be implemented quickly to reduce immediate risk with specific configuration changes, WAF rules, or temporary controls.

**PERMANENT FIXES (Long-term Solutions):**
List 4-5 comprehensive remediation steps for permanent resolution with detailed implementation guidance and code examples.

**VALIDATION AND TESTING:**
Describe procedures to verify the fix (unit tests, integration tests, security testing procedures, verification criteria).

**PREVENTION AND DEFENSE IN DEPTH:**
List 2-3 additional security controls to prevent recurrence (monitoring, detection mechanisms, CI/CD security scanning, developer training).

## Proof of concept
1. Clear, step-by-step instructions to reproduce the issue or observe the vulnerable behavior.  
2. Keep steps brief but sufficient to validate the finding (include sample curl commands, HTTP requests/responses, or Burp snippets where relevant). Do not include destructive commands.
3. Provide 5-8 detailed, reproducible steps
4. Include prerequisites, exact commands/requests with all parameters
5. Show expected vs actual behavior at each step
6. Describe how to validate successful exploitation
7. IMPORTANT: Maintain ethical hacking principles - no destructive or malicious actions

## References
- Links to authoritative resources such as OWASP, PortSwigger, CWE, CVEs, vendor documentation, or other reputable sources.
- Format: [Descriptive Title](https://actual-complete-url.com)
- Provide 7-10 high-quality reference links organized by category:
  * OWASP Resources (2-3 links)
  * Industry Standards (2-3 links): CWE, NIST, SANS, ISO 27001, CVE
  * Technical Documentation (2-3 links): vendor security advisories, framework guides, RFC specifications
  * Additional Resources (1-2 links): academic research, security tools, reputable blog articles
- Ensure ALL URLs are real, functional, and directly relevant

CRITICAL REQUIREMENTS:
- Write in professional, technical language appropriate for enterprise security reports
- Use industry-standard terminology and frameworks (OWASP, CWE, CVSS, CIA Triad)
- Provide specific, actionable guidance that development teams can immediately implement
- Include concrete examples, code snippets, and configuration details
- Structure content with clear paragraphs and sections for readability
- Maintain ethical hacking principles and responsible disclosure throughout
- Focus on helping the client understand risk and implement effective remediations"""


def get_prompt_template(template_key: str) -> str:
    """
    Get the prompt template string for the specified template.
    
    Args:
        template_key: Either "one" or "core"
        
    Returns:
        Prompt template string with {finding_name} and {additional_context} placeholders
    """
    if template_key == "one":
        return TEMPLATE_ONE_PROMPT
    elif template_key == "core":
        return TEMPLATE_CORE_PROMPT
    else:
        raise ValueError(f"Invalid template key: {template_key}. Must be 'one' or 'core'")
