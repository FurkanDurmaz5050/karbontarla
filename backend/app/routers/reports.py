from __future__ import annotations
from typing import List

"""MRV rapor router — PDF üretimi ve indirme."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.field import Field
from app.models.carbon_credit import CarbonCredit
from app.models.report import MRVReport
from app.routers.auth import get_current_user
from app.schemas.report import ReportOut, ReportGenerateRequest
from app.services.pdf_generator import PDFGenerator

router = APIRouter()
pdf_generator = PDFGenerator()


@router.post("/generate", response_model=ReportOut, status_code=201)
async def generate_report(
    data: ReportGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    field_result = await db.execute(select(Field).where(Field.id == data.field_id))
    field = field_result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="Tarla bulunamadı")

    credit = None
    if data.credit_id:
        credit_result = await db.execute(
            select(CarbonCredit).where(CarbonCredit.id == data.credit_id)
        )
        credit = credit_result.scalar_one_or_none()

    pdf_path = pdf_generator.generate_mrv_pdf(
        field=field,
        credit=credit,
        user=current_user,
        report_type=data.report_type,
        period_start=data.period_start,
        period_end=data.period_end,
    )

    report = MRVReport(
        field_id=data.field_id,
        credit_id=data.credit_id,
        report_type=data.report_type,
        period_start=data.period_start,
        period_end=data.period_end,
        pdf_path=pdf_path,
        generated_by=current_user.id,
    )
    db.add(report)
    await db.flush()
    return report


@router.get("/{report_id}", response_model=ReportOut)
async def get_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(MRVReport).where(MRVReport.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Rapor bulunamadı")
    return report


@router.get("/{report_id}/download")
async def download_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(MRVReport).where(MRVReport.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Rapor bulunamadı")

    if not report.pdf_path:
        raise HTTPException(status_code=404, detail="PDF dosyası bulunamadı")

    try:
        with open(report.pdf_path, "rb") as f:
            pdf_bytes = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="PDF dosyası sunucuda bulunamadı")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="MRV_Report_{report_id}.pdf"'
        },
    )


@router.get("/field/{field_id}", response_model=List[ReportOut])
async def list_field_reports(
    field_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MRVReport)
        .where(MRVReport.field_id == field_id)
        .order_by(MRVReport.generated_at.desc())
    )
    return result.scalars().all()
