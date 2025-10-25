# app/crud.py
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func
from .models import Report
from .db import async_session

async def create_report(data: Dict[str, Any], user_id: str) -> Report:
    async with async_session() as session:
        r = Report(user_id=user_id, **data)
        session.add(r)
        await session.commit()
        await session.refresh(r)
        return r

async def list_reports(
    user_id: str,
    approved_only: bool = True,
    finding_name: Optional[str] = None,
    template: Optional[str] = None,
    limit: int = 200
) -> List[Report]:
    async with async_session() as session:
        stmt = select(Report).where(Report.user_id == user_id).order_by(Report.created_at.desc()).limit(limit)
        if approved_only:
            stmt = stmt.where(Report.approved.is_(True))
        if finding_name:
            stmt = stmt.where(Report.finding_name == finding_name)
        if template:
            stmt = stmt.where(Report.template == template)
        q = await session.execute(stmt)
        return q.scalars().all()

async def types_summary(user_id: str, approved_only: bool = True) -> List[Dict[str, Any]]:
    async with async_session() as session:
        stmt = select(
            Report.finding_name,
            Report.template,
            func.count(Report.id).label("cnt"),
        ).where(Report.user_id == user_id).group_by(Report.finding_name, Report.template)

        if approved_only:
            stmt = stmt.where(Report.approved.is_(True))

        rows = (await session.execute(stmt)).all()
        agg: Dict[str, Dict[str, Any]] = {}
        for name, template, cnt in rows:
            if name not in agg:
                agg[name] = {"finding_name": name, "total": 0, "counts": {"one": 0, "core": 0}}
            agg[name]["counts"][template] = agg[name]["counts"].get(template, 0) + int(cnt)
            agg[name]["total"] += int(cnt)

        return sorted(agg.values(), key=lambda x: x["total"], reverse=True)
