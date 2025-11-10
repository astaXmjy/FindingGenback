# app/crud.py
from typing import Optional, List, Dict, Any
from sqlalchemy import func
from sqlalchemy.orm import Session
from .models import Report


def create_report(db: Session, data: Dict[str, Any], user_id: str) -> Report:
    """Create a new report in the database."""
    r = Report(user_id=user_id, **data)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def list_reports(
    db: Session,
    user_id: str,
    approved_only: bool = True,
    finding_name: Optional[str] = None,
    template: Optional[str] = None,
    limit: int = 200
) -> List[Report]:
    """List reports with optional filtering."""
    # Start with base query
    query = db.query(Report).filter(Report.user_id == user_id)
    
    # Apply all filters BEFORE limit/order_by
    if approved_only:
        query = query.filter(Report.approved.is_(True))
    if finding_name:
        query = query.filter(Report.finding_name == finding_name)
    if template:
        query = query.filter(Report.template == template)
    
    # Apply ordering and limit at the end
    query = query.order_by(Report.created_at.desc()).limit(limit)
    
    return query.all()


def types_summary(db: Session, user_id: str, approved_only: bool = True) -> List[Dict[str, Any]]:
    """Get summary of finding types with counts."""
    query = db.query(
        Report.finding_name,
        Report.template,
        func.count(Report.id).label("cnt"),
    ).filter(Report.user_id == user_id).group_by(Report.finding_name, Report.template)

    if approved_only:
        query = query.filter(Report.approved.is_(True))

    rows = query.all()
    agg: Dict[str, Dict[str, Any]] = {}

    for name, template, cnt in rows:
        if name not in agg:
            agg[name] = {"finding_name": name, "total": 0, "counts": {}}
        agg[name]["counts"][template] = agg[name]["counts"].get(template, 0) + int(cnt)
        agg[name]["total"] += int(cnt)

    return sorted(agg.values(), key=lambda x: x["total"], reverse=True)


def update_report(db: Session, report_id: int, data: Dict[str, Any], user_id: str) -> Optional[Report]:
    """Update a report if owned by the user."""
    report = db.query(Report).filter(Report.id == report_id, Report.user_id == user_id).first()
    if report:
        for key, value in data.items():
            if hasattr(report, key):
                setattr(report, key, value)
        db.commit()
        db.refresh(report)
        return report
    return None


def delete_report(db: Session, report_id: int, user_id: str) -> bool:
    """Delete a report if owned by the user."""
    report = db.query(Report).filter(Report.id == report_id, Report.user_id == user_id).first()
    if report:
        db.delete(report)
        db.commit()
        return True
    return False
