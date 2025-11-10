# app/models.py
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, func, Boolean

Base = declarative_base()

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), index=True, nullable=False)  # owner

    template = Column(String(16), nullable=False)              # "one" | "core"
    finding_name = Column(String(255), index=True, nullable=False)
    input_summary = Column(Text)
    title = Column(String(512), nullable=False)

    # template1 (one)
    vulnerability_overview = Column(Text)
    finding_details = Column(Text)
    impacts = Column(Text)
    recommendations = Column(Text)

    # template2 (core)
    description = Column(Text)
    severity = Column(Text)
    suggested_fix = Column(Text)

    # common
    summary = Column(Text)
    references = Column(Text)

    approved = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class ApprovedUser(Base):
    __tablename__ = "approved_users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    firebase_uid = Column(String(255), unique=True, nullable=True, index=True)  # Store UID after first login
    is_active = Column(Boolean, default=False, nullable=False)  # Default False - needs approval
    role = Column(String(50), default="user", nullable=False)  # user, reviewer, admin
    approved_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_by = Column(String(255))  # Admin who approved
    notes = Column(Text)  # Optional notes about the user