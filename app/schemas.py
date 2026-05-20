from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict, Field
from app.enums import AppointmentStatus, AppointmentServiceStatus

# Client Schemas
class ClientBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, examples=["João Silva"])
    email: str = Field(..., examples=["joao@example.com"])
    phone: str = Field(..., min_length=8, max_length=20, examples=["(11) 99999-9999"])

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = None
    phone: Optional[str] = Field(None, min_length=8, max_length=20)

class ClientResponse(ClientBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Service Schemas
class BeautyServiceBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, examples=["Corte de Cabelo Feminino"])
    description: Optional[str] = Field(None, max_length=255, examples=["Lavagem + Corte + Secagem"])
    duration: int = Field(..., gt=0, description="Duração estimada em minutos", examples=[45])
    price: float = Field(..., ge=0.0, description="Preço do serviço", examples=[80.00])

class BeautyServiceCreate(BeautyServiceBase):
    pass

class BeautyServiceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    duration: Optional[int] = Field(None, gt=0)
    price: Optional[float] = Field(None, ge=0.0)

class BeautyServiceResponse(BeautyServiceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Appointment-Service intermediate schemas
class AppointmentServiceResponse(BaseModel):
    service_id: int
    name: str
    status: AppointmentServiceStatus
    price_at_booking: float
    duration_at_booking: int

    model_config = ConfigDict(from_attributes=True)


# Appointment Schemas
class AppointmentCreate(BaseModel):
    client_id: int = Field(..., description="ID do cliente")
    service_ids: List[int] = Field(..., min_length=1, description="Lista de IDs dos serviços solicitados")
    start_time: datetime = Field(..., description="Data e hora de início")
    notes: Optional[str] = Field(None, max_length=500, description="Observações do agendamento")

class AppointmentUpdate(BaseModel):
    start_time: Optional[datetime] = None
    service_ids: Optional[List[int]] = None
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = Field(None, max_length=500)

class AppointmentResponse(BaseModel):
    id: int
    client_id: int
    client_name: str
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus
    notes: Optional[str]
    services: List[AppointmentServiceResponse]
    suggestion: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AppointmentServiceStatusUpdate(BaseModel):
    status: AppointmentServiceStatus


# Report Schemas
class ServicePopularity(BaseModel):
    name: str
    count: int

class WeeklyReportResponse(BaseModel):
    total_appointments: int
    confirmed_appointments: int
    cancelled_appointments: int
    completed_services: int
    estimated_revenue: float
    appointments_by_status: Dict[str, int]
    most_requested_services: List[ServicePopularity]
