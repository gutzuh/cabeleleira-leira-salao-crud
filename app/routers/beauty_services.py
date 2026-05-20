from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import BeautyService
from app.schemas import BeautyServiceCreate, BeautyServiceUpdate, BeautyServiceResponse

router = APIRouter(prefix="/services", tags=["Services"])

@router.post("", response_model=BeautyServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(service_data: BeautyServiceCreate, db: Session = Depends(get_db)):
    existing = db.query(BeautyService).filter(BeautyService.name == service_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um serviço cadastrado com este nome."
        )
    db_service = BeautyService(
        name=service_data.name,
        description=service_data.description,
        duration=service_data.duration,
        price=service_data.price
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

@router.get("", response_model=List[BeautyServiceResponse])
def list_services(db: Session = Depends(get_db)):
    return db.query(BeautyService).all()

@router.get("/{service_id}", response_model=BeautyServiceResponse)
def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(BeautyService).filter(BeautyService.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Serviço com ID {service_id} não encontrado."
        )
    return service

@router.put("/{service_id}", response_model=BeautyServiceResponse)
def update_service(service_id: int, service_data: BeautyServiceUpdate, db: Session = Depends(get_db)):
    service = db.query(BeautyService).filter(BeautyService.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Serviço com ID {service_id} não encontrado."
        )
    
    if service_data.name is not None and service_data.name != service.name:
        existing = db.query(BeautyService).filter(BeautyService.name == service_data.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um serviço cadastrado com este nome."
            )
        service.name = service_data.name
        
    if service_data.description is not None:
        service.description = service_data.description
        
    if service_data.duration is not None:
        service.duration = service_data.duration
        
    if service_data.price is not None:
        service.price = service_data.price
        
    db.commit()
    db.refresh(service)
    return service

@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(BeautyService).filter(BeautyService.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Serviço com ID {service_id} não encontrado."
        )
    db.delete(service)
    db.commit()
