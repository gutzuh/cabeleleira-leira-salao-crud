from datetime import datetime
from typing import List, Optional
from sqlalchemy import ForeignKey, String, Float, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.enums import AppointmentStatus, AppointmentServiceStatus

class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)

    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment", back_populates="client", cascade="all, delete-orphan"
    )

class BeautyService(Base):
    __tablename__ = "beauty_services"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)  # duração estimada em minutos
    price: Mapped[float] = mapped_column(Float, nullable=False)

    appointments: Mapped[List["AppointmentService"]] = relationship(
        "AppointmentService", back_populates="service", cascade="all, delete-orphan"
    )

class AppointmentService(Base):
    __tablename__ = "appointment_services"

    appointment_id: Mapped[int] = mapped_column(
        ForeignKey("appointments.id", ondelete="CASCADE"), primary_key=True
    )
    service_id: Mapped[int] = mapped_column(
        ForeignKey("beauty_services.id", ondelete="CASCADE"), primary_key=True
    )
    status: Mapped[AppointmentServiceStatus] = mapped_column(
        SQLEnum(AppointmentServiceStatus), default=AppointmentServiceStatus.PENDENTE, nullable=False
    )
    price_at_booking: Mapped[float] = mapped_column(Float, nullable=False)
    duration_at_booking: Mapped[int] = mapped_column(Integer, nullable=False)

    appointment: Mapped["Appointment"] = relationship("Appointment", back_populates="services")
    service: Mapped["BeautyService"] = relationship("BeautyService", back_populates="appointments")

class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        SQLEnum(AppointmentStatus), default=AppointmentStatus.SOLICITADO, nullable=False
    )
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    client: Mapped["Client"] = relationship("Client", back_populates="appointments")
    services: Mapped[List["AppointmentService"]] = relationship(
        "AppointmentService", back_populates="appointment", cascade="all, delete-orphan"
    )
