# app/main.py
from datetime import datetime
from typing import Optional, Literal, List
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .import models
from .auth import verify_firebase_token
from .db import get_db,engine
from .llm import get_structured_llm
from .schemas import GenerateRequest, GenerationOut, ReportCreate, ReportOut, ReportUpdate, FindingTypeSummary,ApproveUserRequest,ApprovedUserOut
from .output_schemas import TemplateOneOutput, TemplateCoreOutput
from .prompt_templates import get_prompt_template
from .crud import create_report, list_reports, types_summary, update_report, delete_report

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pentest Report Generator")

# ========================================
# CORS Configuration - ALLOW ALL ORIGINS
# ========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins. For production, specify allowed origins.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        "role": user.get("role", "user"),
        "message": "User is approved and authenticated"
    }

# ========================================
# Admin Endpoints
# ========================================

@app.get("/admin/users", response_model=List[ApprovedUserOut])
async def admin_list_users(
    user: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """List all users (admin only)"""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = db.query(models.ApprovedUser).all()
    return users

@app.put("/admin/users/{user_id}")
async def admin_update_user(
    user_id: int,
    is_active: Optional[bool] = None,
    role: Optional[str] = None,
    notes: Optional[str] = None,
    user: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """Update user (admin only)"""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db_user = db.query(models.ApprovedUser).filter(models.ApprovedUser.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if is_active is not None:
        db_user.is_active = is_active
    if role is not None:
        if role not in ["user", "reviewer", "admin"]:
            raise HTTPException(status_code=400, detail="Invalid role")
        db_user.role = role
    if notes is not None:
        db_user.notes = notes
    
    db_user.approved_by = user.get("email")
    db.commit()
    db.refresh(db_user)
    
    return {"message": "User updated successfully", "user": db_user}

@app.delete("/admin/users/{user_id}")
async def admin_delete_user(
    user_id: int,
    user: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """Delete user (admin only)"""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db_user = db.query(models.ApprovedUser).filter(models.ApprovedUser.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Don't allow deleting self
    if db_user.email == user.get("email"):
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    db.delete(db_user)
    db.commit()
    
    return {"message": "User deleted successfully"}

@app.get("/admin/reports", response_model=List[ReportOut])
async def admin_list_all_reports(
    user: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """List all reports from all users (admin only)"""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    reports = db.query(models.Report).order_by(models.Report.created_at.desc()).all()
    return reports

@app.put("/admin/reports/{report_id}", response_model=ReportOut)
async def admin_update_report(
    report_id: int,
    updates: ReportUpdate,
    user: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """Update any report (admin only)"""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Update only provided fields
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(report, field, value)
    
    db.commit()
    db.refresh(report)
    
    return report

@app.delete("/admin/reports/{report_id}")
async def admin_delete_report(
    report_id: int,
    user: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """Delete any report (admin only)"""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    db.delete(report)
    db.commit()
    
    return {"message": "Report deleted successfully"}

# ========================================
# Reviewer Endpoints
# ========================================

@app.get("/reviewer/reports", response_model=List[ReportOut])
async def reviewer_list_all_reports(
    user: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """List all reports (reviewer only)"""
    if user.get("role") not in ["reviewer", "admin"]:
        raise HTTPException(status_code=403, detail="Reviewer access required")
    
    reports = db.query(models.Report).order_by(models.Report.created_at.desc()).all()
    return reports

@app.put("/reviewer/reports/{report_id}", response_model=ReportOut)
async def reviewer_update_report(
    report_id: int,
    payload: ReportUpdate,
    user: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """Update any report (reviewer only)"""
    if user.get("role") not in ["reviewer", "admin"]:
        raise HTTPException(status_code=403, detail="Reviewer access required")
    
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Update fields
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(report, field, value)
    
    db.commit()
    db.refresh(report)
    
    return report


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
    """Generate a comprehensive security finding report using OpenAI structured output."""
    try:
        print(f"\n{'='*80}")
        print(f"🔍 Starting report generation")
        print(f"Finding: {req.finding_name}")
        print(f"Template: {req.template}")
        print(f"User: {user.get('email', 'unknown')}")
        print(f"Context length: {len(req.additional_context or '')} characters")
        print(f"{'='*80}\n")
        
        # Select schema based on template
        schema = TemplateOneOutput if req.template == "one" else TemplateCoreOutput
        
        # Get structured LLM with 100% schema compliance
        print(f"🤖 Initializing OpenAI with structured output (json_schema method)...")
        structured_llm = get_structured_llm(schema)
        
        # Get prompt template and format it
        prompt_template = get_prompt_template(req.template)
        prompt = prompt_template.format(
            finding_name=req.finding_name,
            additional_context=req.additional_context or "No additional context provided"
        )
        
        print(f"📝 Generating report with strict schema compliance...")
        
        # Invoke and get validated Pydantic object directly
        result = structured_llm.invoke(prompt)
        
        print(f"\n{'='*80}")
        print(f"✅ Successfully generated structured report!")
        print(f"📊 Report validated against Pydantic schema")
        print(f"{'='*80}\n")
        
        # Convert Pydantic model to GenerationOut response
        if req.template == "one":
            # Convert list fields to strings for the API response
            recommendations_text = "\n".join(f"• {rec}" for rec in result.recommendations)
            poc_text = "\n".join(f"{i+1}. {step}" for i, step in enumerate(result.proof_of_concept))
            references_text = "\n".join(result.references)
            
            return GenerationOut(
                template=req.template,
                finding_name=req.finding_name,
                input_summary=req.additional_context,
                title=result.title,
                summary=result.summary,
                vulnerability_overview=result.vulnerability_overview,
                finding_details=result.finding_details,
                impacts=result.impacts,
                recommendations=recommendations_text,
                description=None,
                severity=None,
                suggested_fix=None,
                references=references_text,
                proof_of_concept=poc_text
            )
        else:
            # Convert list fields to strings for the API response
            poc_text = "\n".join(f"{i+1}. {step}" for i, step in enumerate(result.proof_of_concept))
            references_text = "\n".join(result.references)
            
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
                references=references_text,
                proof_of_concept=poc_text
            )
        
    except Exception as e:
        # Catch all errors including LangChain parsing errors
        error_detail = str(e)
        error_type = type(e).__name__
        print(f"\n{'='*80}")
        print(f"❌ ERROR ({error_type})")
        print(f"Full Error: {error_detail}")
        print(f"{'='*80}\n")
        
        # Check for specific error types
        if "parse" in error_detail.lower() or "completion" in error_detail.lower():
            # LangChain parsing error - likely truncated response
            user_msg = "AI response was incomplete or truncated. The model may need more tokens. Please try again."
        elif "min_length" in error_detail.lower():
            user_msg = "Report generation produced content that was too short. Please try again or provide more context."
        elif "max_length" in error_detail.lower():
            user_msg = "Report generation produced content that was too long. Please try again."
        elif "rate limit" in error_detail.lower() or "429" in error_detail:
            user_msg = "API rate limit reached. Please wait a moment and try again."
        elif "timeout" in error_detail.lower():
            user_msg = "Request timed out. The report generation is taking longer than expected. Please try again."
        elif "network" in error_detail.lower() or "connection" in error_detail.lower():
            user_msg = "Network connection error. Please check your connection and try again."
        else:
            user_msg = "Report generation failed. Please try again."
        
        raise HTTPException(
            status_code=500, 
            detail=f"{user_msg}\n\nTechnical details: {error_detail[:300]}"
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

@app.put("/reports/{report_id}", response_model=ReportOut)
def update_report_endpoint(
    report_id: int,
    payload: ReportUpdate,
    user=Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """Update a report if owned by the authenticated user."""
    update_data = {k: v for k, v in payload.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    updated = update_report(db=db, report_id=report_id, data=update_data, user_id=user["uid"])
    if not updated:
        raise HTTPException(status_code=404, detail="Report not found or not owned by user")
    
    return ReportOut(
        id=updated.id, template=updated.template, finding_name=updated.finding_name, 
        input_summary=updated.input_summary, title=updated.title, summary=updated.summary, 
        vulnerability_overview=updated.vulnerability_overview, finding_details=updated.finding_details, 
        impacts=updated.impacts, recommendations=updated.recommendations, description=updated.description, 
        severity=updated.severity, suggested_fix=updated.suggested_fix, references=updated.references, 
        approved=updated.approved, created_at=updated.created_at.isoformat()
    )


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
