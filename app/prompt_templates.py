from langchain_core.prompts import PromptTemplate

TEMPLATE_ONE = """
You are a senior security engineer and technical writer. Produce a pentest finding using the "template1 (one)" format below.

Input:
- finding_name: {finding_name}
- additional_context: {additional_context}

Output format (use these headings and sections exactly):

# [Finding Title]

## Summary
- Concise summary for the finding.

## Vulnerability Overview
- General description of this vulnerability type (explain the class of issue, how it works, and how an attacker could exploit it). This paragraph must describe the vulnerability type, not the specific instance.

## Finding Details
- Brief overview of the specific issue: what was found, where it was found, and the potential risk in context. Write in a professional, explanatory tone.
- Root cause and observed evidence (concise bullet points describing the root cause, affected components/endpoints, and what was observed).

## Impacts
- One paragraph describing the security impact: how an attacker might exploit the issue, what access or damage it could lead to, and any broader implications (data leakage, supply chain risk, business impact). Keep to a single paragraph.

## Recommendations
- Detailed, actionable remediation steps. Use imperative language and provide concrete technical guidance where appropriate (configuration changes, code-level guidance, controls to implement). Use bullets and be as specific as possible.

## Proof of concept
1. Clear, step-by-step instructions to reproduce the issue or observe the vulnerable behavior.
2. Keep steps brief but sufficient to validate the finding (include sample curl requests, HTTP requests/responses, or Burp/console snippets where relevant).

## References
- Link to authoritative resources (OWASP, PortSwigger, CWE, vendor docs, CVEs, etc.)
"""

TEMPLATE_CORE = """
You are a senior security engineer and technical writer. Produce a pentest finding using the "template2 (core)" format below.

Input:
- finding_name: {finding_name}
- additional_context: {additional_context}

Output format (use these headings and sections exactly):

# [Finding Title]

## Summary
Concise summary for the finding.

## Description
Brief overview of the issue, what was found, where it was found, and the potential risk in context. This is written in a professional, explanatory tone.

Add about the vulnerability

## Severity
Explanation of the security impact, detailing how an attacker might exploit the issue, what kind of access or damage it could lead to, and any broader implications (e.g., data leaks, supply chain risks). Keep this to a single paragraph.

## Suggested fix
Recommended actions to remediate the issue. Provide very detailed, actionable remediation steps (configuration changes, code-level guidance, compensating controls, testing/validation steps).

## Proof of concept
1. Clear, step-by-step instructions to reproduce the issue or observe the vulnerable behavior.
2. Keep steps brief but sufficient to validate the finding (include sample curl commands, HTTP requests/responses, or Burp snippets where relevant). Do not include destructive commands.

## References
- Links to authoritative resources such as OWASP, PortSwigger, CWE, CVEs, vendor documentation, or other reputable sources.
"""

PROMPT_ONE = PromptTemplate.from_template(TEMPLATE_ONE)
PROMPT_CORE = PromptTemplate.from_template(TEMPLATE_CORE)

def get_prompt(template_key: str) -> PromptTemplate:
    if template_key == "one":
        return PROMPT_ONE
    return PROMPT_CORE
