# app/main.py
import os
from datetime import datetime
from typing import Optional, Literal, List
from .output_schemas import TemplateOneOutput, TemplateCoreOutput
from .prompt_templates import get_prompt_structured
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .import models
from .auth import verify_firebase_token
from .db import get_db,engine
from .llm import MistralLLM
from .schemas import GenerateRequest, GenerationOut, ReportCreate, ReportOut, FindingTypeSummary,ApproveUserRequest,ApprovedUserOut
from .crud import create_report, list_reports, types_summary, delete_report
from langchain_core.output_parsers import StrOutputParser

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pentest Report Generator")

# ========================================
# CORS Configuration - ALLOW ALL ORIGINS
# ========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins. For production, specify allowed origins.
    allow_credentials=True,
    allow_methods=[
        "*"
    ],  # Allow all methods. Specify methods if needed (e.g., ["GET", "POST"]).
    allow_headers=["*"],  # Allow all headers. Specify headers if needed.
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

# Add a health check endpoint for debugging
@app.get("/health")
def health_check(user=Depends(verify_firebase_token)):
    """Health check endpoint that also verifies user approval"""
    return {
        "status": "ok",
        "user": user.get("email"),
        "message": "User is approved and authenticated"
    }


def _section(text: str, heading: str) -> str:
    """Extract a section from generated text."""
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
    """Get list of all available finding types."""
    return FINDINGS_CATALOG

@app.get("/reports/types", response_model=List[FindingTypeSummary])
def get_types(
    approved_only: bool = True,
    user=Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """Get summary of finding types with counts."""
    return types_summary(db=db, user_id=user["uid"], approved_only=approved_only)


@app.post("/generate", response_model=GenerationOut)
async def generate(req: GenerateRequest, user=Depends(verify_firebase_token)):
    """Generate a comprehensive security finding report preview (not saved to database)."""
    try:
        print(f"\n{'='*80}")
        print(f"🔍 Starting report generation")
        print(f"Finding: {req.finding_name}")
        print(f"Template: {req.template}")
        print(f"User: {user.get('email', 'unknown')}")
        print(f"Context length: {len(req.additional_context or '')} characters")
        print(f"{'='*80}\n")
        
        # Get structured prompt
        prompt = get_prompt_structured(req.template)
        
        # Prepare context
        context = {
            "finding_name": req.finding_name,
            "additional_context": req.additional_context or "No additional context provided"
        }
        
        # Format prompt
        formatted_prompt = prompt.format(**context)
        print(f"📝 Prompt length: {len(formatted_prompt)} characters")
        
        # Select appropriate schema
        schema = TemplateOneOutput if req.template == "one" else TemplateCoreOutput
        print(f"📋 Using schema: {schema.__name__}")
        
        # Generate structured output with retry logic
        print(f"🤖 Generating report with Mistral AI...")
        result = llm.generate_structured(formatted_prompt, schema, max_attempts=3)
        
        # Log success and stats
        print(f"\n{'='*80}")
        print(f"✅ Successfully generated comprehensive report!")
        print(f"📊 Report Statistics:")
        if req.template == "one":
            print(f"  - Summary: {len(result.summary)} chars")
            print(f"  - Vulnerability Overview: {len(result.vulnerability_overview)} chars")
            print(f"  - Finding Details: {len(result.finding_details)} chars")
            print(f"  - Impacts: {len(result.impacts)} chars")
            print(f"  - Recommendations: {len(result.recommendations)} items")
            print(f"  - Proof of Concept: {len(result.proof_of_concept)} steps")
            print(f"  - References: {len(result.references)} links")
        else:
            print(f"  - Summary: {len(result.summary)} chars")
            print(f"  - Description: {len(result.description)} chars")
            print(f"  - Severity: {len(result.severity)} chars")
            print(f"  - Suggested Fix: {len(result.suggested_fix)} chars")
            print(f"  - Proof of Concept: {len(result.proof_of_concept)} steps")
            print(f"  - References: {len(result.references)} links")
        print(f"{'='*80}\n")
        
        # Convert to response format
        if req.template == "one":
            return GenerationOut(
                template=req.template,
                finding_name=req.finding_name,
                input_summary=req.additional_context,
                title=result.title,
                summary=result.summary,
                vulnerability_overview=result.vulnerability_overview,
                finding_details=result.finding_details,
                impacts=result.impacts,
                recommendations="\n".join(f"{i+1}. {rec}" for i, rec in enumerate(result.recommendations)),
                description=None,
                severity=None,
                suggested_fix=None,
                references="\n".join(result.references),
                proof_of_concept="\n".join(f"{i+1}. {step}" for i, step in enumerate(result.proof_of_concept))
            )
        else:
            return GenerationOut(
                template=req.template,
                finding_name=req.finding_name,
                input_summary=req.additional_context,
                title=result.title,
                summary=result.summary,
                vulnerability_overview=None,
                finding_details=None,
                impacts=None,
                recommendations=None,
                description=result.description,
                severity=result.severity,
                suggested_fix=result.suggested_fix,
                references="\n".join(result.references),
                proof_of_concept="\n".join(f"{i+1}. {step}" for i, step in enumerate(result.proof_of_concept))
            )
        
    except ValueError as e:
        # Schema validation or JSON parsing error
        error_detail = str(e)
        print(f"\n{'='*80}")
        print(f"❌ VALIDATION ERROR")
        print(f"Error: {error_detail[:500]}")
        print(f"{'='*80}\n")
        
        # Provide user-friendly error message
        if "min_length" in error_detail.lower():
            user_msg = "Report generation produced content that was too short. Please try again or provide more context."
        elif "max_length" in error_detail.lower():
            user_msg = "Report generation produced content that was too long. Please try again."
        elif "json" in error_detail.lower():
            user_msg = "Failed to parse AI response. This is usually temporary - please try again."
        else:
            user_msg = "Report validation failed. Please try again."
        
        raise HTTPException(
            status_code=500, 
            detail=f"{user_msg} (Technical details: {error_detail[:200]})"
        )
    
    except RuntimeError as e:
        # API or network errors
        error_detail = str(e)
        print(f"\n{'='*80}")
        print(f"❌ RUNTIME ERROR")
        print(f"Error: {error_detail}")
        print(f"{'='*80}\n")
        
        if "rate limit" in error_detail.lower() or "429" in error_detail:
            user_msg = "API rate limit reached. Please wait a moment and try again."
        elif "timeout" in error_detail.lower():
            user_msg = "Request timed out. The report generation is taking longer than expected. Please try again."
        elif "network" in error_detail.lower() or "connection" in error_detail.lower():
            user_msg = "Network connection error. Please check your connection and try again."
        else:
            user_msg = "Report generation failed. Please try again."
        
        raise HTTPException(
            status_code=503,
            detail=f"{user_msg} (Technical details: {error_detail[:200]})"
        )
    
    except Exception as e:
        # Unexpected errors
        error_detail = str(e)
        print(f"\n{'='*80}")
        print(f"❌ UNEXPECTED ERROR")
        print(f"Type: {type(e).__name__}")
        print(f"Error: {error_detail}")
        print(f"{'='*80}\n")
        
        raise HTTPException(
            status_code=500, 
            detail=f"An unexpected error occurred during report generation. Please try again. (Error: {error_detail[:200]})"
        )
    

# ---------- SAVE ONLY WHEN APPROVED (no PoC stored) ----------
@app.post("/reports", response_model=ReportOut)
def save_report(
    payload: ReportCreate,
    user=Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """Save an approved report to the database."""
    data = dict(
        template=payload.template, finding_name=payload.finding_name, input_summary=payload.input_summary,
        title=payload.title, summary=payload.summary, vulnerability_overview=payload.vulnerability_overview,
        finding_details=payload.finding_details, impacts=payload.impacts, recommendations=payload.recommendations,
        description=payload.description, severity=payload.severity, suggested_fix=payload.suggested_fix,
        references=payload.references, approved=payload.approved, created_at=datetime.utcnow()
    )
    saved = create_report(db=db, data=data, user_id=user["uid"])
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
    db: Session = Depends(get_db)
):
    """Get list of reports with optional filtering."""
    items = list_reports(db=db, user_id=user["uid"], approved_only=approved_only, finding_name=finding_name, template=template)
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

@app.delete("/reports/{report_id}")
def delete_report_endpoint(
    report_id: int,
    user=Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """Delete a report if owned by the authenticated user."""
    success = delete_report(db=db, report_id=report_id, user_id=user["uid"])
    if not success:
        raise HTTPException(status_code=404, detail="Report not found or not owned by user")
    return {"message": "Report deleted successfully"}

@app.get("/admin/pending-users", response_model=List[ApprovedUserOut])
def list_pending_users(
    user=Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """List all pending (inactive) users awaiting approval"""
    # TODO: Add admin role check here
    
    users = db.query(models.ApprovedUser).filter(models.ApprovedUser.is_active == False).all()
    return [
        ApprovedUserOut(
            id=u.id,
            email=u.email,
            firebase_uid=u.firebase_uid,
            is_active=u.is_active,
            approved_at=u.approved_at.isoformat() if u.approved_at else "",
            approved_by=u.approved_by,
            notes=u.notes
        )
        for u in users
    ]

@app.get("/admin/approved-users", response_model=List[ApprovedUserOut])
def list_approved_users(
    user=Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """List all approved (active) users"""
    # TODO: Add admin role check here
    
    users = db.query(models.ApprovedUser).filter(models.ApprovedUser.is_active == True).all()
    return [
        ApprovedUserOut(
            id=u.id,
            email=u.email,
            firebase_uid=u.firebase_uid,
            is_active=u.is_active,
            approved_at=u.approved_at.isoformat() if u.approved_at else "",
            approved_by=u.approved_by,
            notes=u.notes
        )
        for u in users
    ]

@app.post("/admin/approve-user")
def approve_user(
    req: ApproveUserRequest,
    user=Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """Approve a pending user"""
    # TODO: Add admin role check here
    admin_email = user.get("email", "admin")
    
    approved_user = db.query(models.ApprovedUser).filter(models.ApprovedUser.email == req.email).first()
    
    if not approved_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if approved_user.is_active:
        return {"message": f"User {req.email} is already approved"}
    
    approved_user.is_active = True
    approved_user.approved_by = admin_email
    approved_user.approved_at = datetime.utcnow()
    if req.notes:
        approved_user.notes = req.notes
    
    db.commit()
    return {"message": f"User {req.email} approved successfully"}

@app.post("/admin/revoke-user")
def revoke_user(
    req: ApproveUserRequest,
    user=Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """Revoke access for an approved user"""
    # TODO: Add admin role check here
    
    approved_user = db.query(models.ApprovedUser).filter(models.ApprovedUser.email == req.email).first()
    
    if not approved_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not approved_user.is_active:
        return {"message": f"User {req.email} is already inactive"}
    
    approved_user.is_active = False
    if req.notes:
        approved_user.notes = req.notes
    
    db.commit()
    return {"message": f"User {req.email} access revoked successfully"}

@app.delete("/admin/delete-user/{email}")
def delete_user(
    email: str,
    user=Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """Permanently delete a user from approved list"""
    # TODO: Add admin role check here
    
    approved_user = db.query(models.ApprovedUser).filter(models.ApprovedUser.email == email).first()
    
    if not approved_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(approved_user)
    db.commit()
    return {"message": f"User {email} deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
