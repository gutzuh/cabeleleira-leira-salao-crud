from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.enums import AppointmentStatus, AppointmentServiceStatus
from app.schemas import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentServiceStatusUpdate
)
from app.services import appointment_service

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(appointment_data: AppointmentCreate, db: Session = Depends(get_db)):
    return appointment_service.create_appointment(db=db, appointment_data=appointment_data)

@router.get("", response_model=List[AppointmentResponse])
def list_appointments(
    client_id: Optional[int] = None,
    status: Optional[AppointmentStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    return appointment_service.list_appointments(
        db=db,
        client_id=client_id,
        status_filter=status,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    return appointment_service.get_appointment(db=db, appointment_id=appointment_id)

@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    update_data: AppointmentUpdate,
    db: Session = Depends(get_db)
):
    return appointment_service.update_appointment(
        db=db, appointment_id=appointment_id, update_data=update_data
    )

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment_service.delete_appointment(db=db, appointment_id=appointment_id)

@router.post("/{appointment_id}/confirm", response_model=AppointmentResponse)
def confirm_appointment(appointment_id: int, db: Session = Depends(get_db)):
    return appointment_service.confirm_appointment(db=db, appointment_id=appointment_id)

@router.post("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db)):
    return appointment_service.cancel_appointment(db=db, appointment_id=appointment_id)


@router.patch("/{appointment_id}/services/{service_id}/status", response_model=AppointmentResponse)
def update_service_status(
    appointment_id: int,
    service_id: int,
    status_update: AppointmentServiceStatusUpdate,
    db: Session = Depends(get_db)
):
    return appointment_service.update_service_status(
        db=db,
        appointment_id=appointment_id,
        service_id=service_id,
        new_status=status_update.status
    )
