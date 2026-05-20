from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import WeeklyReportResponse
from app.services import report_service

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/weekly", response_model=WeeklyReportResponse)
def get_weekly_report(
    reference_date: Optional[datetime] = Query(
        None,
        description="Data de referência para consultar a semana (formato ISO). Se não fornecida, usa a data atual."
    ),
    db: Session = Depends(get_db)
):
    if reference_date is None:
        reference_date = datetime.now()
    return report_service.generate_weekly_report(db=db, reference_date=reference_date)
