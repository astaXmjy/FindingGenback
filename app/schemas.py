# app/schemas.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal, Dict
from datetime import datetime

class GenerateRequest(BaseModel):
    finding_name: str
    template: Literal["one", "core"] = "one"
    additional_context: Optional[str] = None

class GenerationOut(BaseModel):  # preview (includes PoC)
    template: Literal["one", "core"]
    finding_name: str
    input_summary: Optional[str]
    title: str
    summary: str
    vulnerability_overview: Optional[str] = None
    finding_details: Optional[str] = None
    impacts: Optional[str] = None
    recommendations: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    suggested_fix: Optional[str] = None
    references: str
    proof_of_concept: Optional[str] = None

class ReportCreate(BaseModel):   # approve & save (NO PoC)
    template: Literal["one", "core"] = "one"
    finding_name: str
    input_summary: Optional[str] = None
    title: str
    summary: str
    vulnerability_overview: Optional[str] = None
    finding_details: Optional[str] = None
    impacts: Optional[str] = None
    recommendations: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    suggested_fix: Optional[str] = None
    references: str
    approved: bool = True

class ReportUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    vulnerability_overview: Optional[str] = None
    finding_details: Optional[str] = None
    impacts: Optional[str] = None
    recommendations: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    suggested_fix: Optional[str] = None
    references: Optional[str] = None
    input_summary: Optional[str] = None


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    template: Literal["one", "core"]
    finding_name: str
    input_summary: Optional[str]
    title: str
    summary: str
    vulnerability_overview: Optional[str] = None
    finding_details: Optional[str] = None
    impacts: Optional[str] = None
    recommendations: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    suggested_fix: Optional[str] = None
    references: str
    approved: bool
    created_at: datetime

class FindingTypeSummary(BaseModel):  # sidebar
    finding_name: str
    total: int
    counts: Dict[str, int]  # {"one": 3, "core": 5}


class ApproveUserRequest(BaseModel):
    email: str
    notes: Optional[str] = None

class ApprovedUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: str
    firebase_uid: Optional[str]
    is_active: bool
    role: str = "user"
    approved_at: datetime
    approved_by: Optional[str]
    notes: Optional[str]
