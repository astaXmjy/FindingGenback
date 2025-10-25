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
 