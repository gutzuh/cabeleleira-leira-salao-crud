from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Appointment, AppointmentService, BeautyService
from app.enums import AppointmentStatus, AppointmentServiceStatus
from app.schemas import WeeklyReportResponse, ServicePopularity

def generate_weekly_report(db: Session, reference_date: datetime) -> WeeklyReportResponse:
    # calcula o começo (segunda) e o fim (domingo) da semana da data escolhida
    weekday = reference_date.weekday()
    start_of_week = reference_date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=weekday)
    end_of_week = start_of_week + timedelta(days=7)
    
    # busca todos os agendamentos feitos nessa semana
    appointments = db.query(Appointment).filter(
        Appointment.start_time >= start_of_week,
        Appointment.start_time < end_of_week
    ).all()
    
    total_appointments = len(appointments)
    
    # conta quantos agendamentos tem em cada status (confirmado, cancelado, etc)
    appointments_by_status = {status_val.value: 0 for status_val in AppointmentStatus}
    confirmed_appointments = 0
    cancelled_appointments = 0
    
    for app in appointments:
        appointments_by_status[app.status.value] += 1
        if app.status == AppointmentStatus.CONFIRMADO:
            confirmed_appointments += 1
        elif app.status == AppointmentStatus.CANCELADO:
            cancelled_appointments += 1
            
    # calcula quantos serviços foram concluídos e a soma do faturamento
    completed_services_list = db.query(AppointmentService).join(Appointment).filter(
        Appointment.start_time >= start_of_week,
        Appointment.start_time < end_of_week,
        AppointmentService.status == AppointmentServiceStatus.CONCLUIDO
    ).all()
    
    completed_services = len(completed_services_list)
    estimated_revenue = sum(item.price_at_booking for item in completed_services_list)
    
    # busca a lista dos serviços mais pedidos na semana, ordenados do maior pro menor
    most_requested = db.query(
        BeautyService.name,
        func.count(AppointmentService.service_id).label("count")
    ).join(
        AppointmentService, BeautyService.id == AppointmentService.service_id
    ).join(
        Appointment, Appointment.id == AppointmentService.appointment_id
    ).filter(
        Appointment.start_time >= start_of_week,
        Appointment.start_time < end_of_week
    ).group_by(
        BeautyService.name
    ).order_by(
        func.count(AppointmentService.service_id).desc()
    ).all()
    
    most_requested_services = [
        ServicePopularity(name=name, count=count) for name, count in most_requested
    ]
    
    return WeeklyReportResponse(
        total_appointments=total_appointments,
        confirmed_appointments=confirmed_appointments,
        cancelled_appointments=cancelled_appointments,
        completed_services=completed_services,
        estimated_revenue=estimated_revenue,
        appointments_by_status=appointments_by_status,
        most_requested_services=most_requested_services
    )
