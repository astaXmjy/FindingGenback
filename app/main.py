# app/main.py
import os
from datetime import datetime
from typing import Optional, Literal, List

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware

from .auth import verify_firebase_token
from .db import init_db
from .llm import MistralLLM
from .prompt_templates import get_prompt
from .schemas import GenerateRequest, GenerationOut, ReportCreate, ReportOut, FindingTypeSummary
from .crud import create_report, list_reports, types_summary
from langchain_core.output_parsers import StrOutputParser

app = FastAPI(title="Pentest Report Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # includes Authorization
)

llm = MistralLLM()
parser = StrOutputParser()

FINDINGS_CATALOG = [
    "Account Takeover via Mobile Number",
    "IDOR (Insecure Direct Object Reference)",
    "Broken Access Control",
    "SQL Injection",
    "Cross-Site Scripting (XSS)",
    "Server-Side Request Forgery (SSRF)",
    "Cross-Site Request Forgery (CSRF)",
    "Unrestricted File Upload",
    "Insecure Deserialization",
    "Sensitive Data Exposure",
]

@app.on_event("startup")
def _startup():
    init_db()

def _section(text: str, heading: str) -> str:
    if heading not in text:
        return ""
    start = text.find(heading) + len(heading)
    end = len(text)
    heads = [
        "\n## Summary","\n## Vulnerability Overview","\n## Finding Details","\n## Impacts",
        "\n## Recommendations","\n## Description","\n## Severity","\n## Suggested fix",
        "\n## Proof of concept","\n## References","\n# "
    ]
    for h in heads:
        i = text.find(h, start)
        if i != -1:
            end = min(end, i)
    return text[start:end].strip()

@app.get("/findings", response_model=List[str])
async def list_findings():
    return FINDINGS_CATALOG

@app.get("/reports/types", response_model=List[FindingTypeSummary])
def get_types(approved_only: bool = True, user=Depends(verify_firebase_token)):
    return types_summary(user_id=user["uid"], approved_only=approved_only)

# ---------- PREVIEW ONLY ----------
@app.post("/generate", response_model=GenerationOut)
async def generate(req: GenerateRequest, user=Depends(verify_firebase_token)):
    prompt = get_prompt(req.template)
    chain = prompt | llm | parser
    try:
        raw = chain.invoke({"finding_name": req.finding_name, "additional_context": req.additional_context or ""})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

    title = req.finding_name
    summary = _section(raw, "## Summary")
    references = _section(raw, "## References")
    poc = _section(raw, "## Proof of concept")

    if req.template == "one":
        vo = _section(raw, "## Vulnerability Overview")
        fd = _section(raw, "## Finding Details")
        impacts = _section(raw, "## Impacts")
        recs = _section(raw, "## Recommendations")
        desc = sev = fix = None
    else:
        desc = _section(raw, "## Description")
        sev = _section(raw, "## Severity")
        fix = _section(raw, "## Suggested fix")
        vo = fd = impacts = recs = None

    return GenerationOut(
        template=req.template, finding_name=req.finding_name, input_summary=req.additional_context,
        title=title, summary=summary, vulnerability_overview=vo, finding_details=fd,
        impacts=impacts, recommendations=recs, description=desc, severity=sev, suggested_fix=fix,
        references=references, proof_of_concept=poc,
    )

# ---------- SAVE ONLY WHEN APPROVED (no PoC stored) ----------
@app.post("/reports", response_model=ReportOut)
def save_report(payload: ReportCreate, user=Depends(verify_firebase_token)):
    data = dict(
        template=payload.template, finding_name=payload.finding_name, input_summary=payload.input_summary,
        title=payload.title, summary=payload.summary, vulnerability_overview=payload.vulnerability_overview,
        finding_details=payload.finding_details, impacts=payload.impacts, recommendations=payload.recommendations,
        description=payload.description, severity=payload.severity, suggested_fix=payload.suggested_fix,
        references=payload.references, approved=payload.approved, created_at=datetime.utcnow()
    )
    saved = create_report(data, user_id=user["uid"])
    return ReportOut(
        id=saved.id, template=saved.template, finding_name=saved.finding_name, input_summary=saved.input_summary,
        title=saved.title, summary=saved.summary, vulnerability_overview=saved.vulnerability_overview,
        finding_details=saved.finding_details, impacts=saved.impacts, recommendations=saved.recommendations,
        description=saved.description, severity=saved.severity, suggested_fix=saved.suggested_fix,
        references=saved.references, approved=saved.approved, created_at=saved.created_at.isoformat()
    )

@app.get("/reports", response_model=list[ReportOut])
def get_reports(
    approved_only: bool = True,
    finding_name: Optional[str] = Query(None),
    template: Optional[Literal["one", "core"]] = Query(None),
    user=Depends(verify_firebase_token),
):
    items = list_reports(user_id=user["uid"], approved_only=approved_only, finding_name=finding_name, template=template)
    return [
        ReportOut(
            id=i.id, template=i.template, finding_name=i.finding_name, input_summary=i.input_summary,
            title=i.title, summary=i.summary, vulnerability_overview=i.vulnerability_overview,
            finding_details=i.finding_details, impacts=i.impacts, recommendations=i.recommendations,
            description=i.description, severity=i.severity, suggested_fix=i.suggested_fix,
            references=i.references, approved=i.approved, created_at=i.created_at.isoformat()
        )
        for i in items
    ]
