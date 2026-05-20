from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from app.models import Appointment, Client, BeautyService, AppointmentService
from app.enums import AppointmentStatus, AppointmentServiceStatus
from app.schemas import AppointmentCreate, AppointmentUpdate, AppointmentResponse, AppointmentServiceResponse

def get_week_range(date_val: datetime):
    # weekday retorna 0 para segunda-feira e 6 para domingo
    weekday = date_val.weekday()
    start_of_week = date_val.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=weekday)
    end_of_week = start_of_week + timedelta(days=7)
    return start_of_week, end_of_week

def check_weekly_suggestion(db: Session, client_id: int, start_time: datetime) -> Optional[str]:
    # acha o primeiro e o último dia da semana
    start_of_week, end_of_week = get_week_range(start_time)
    
    # procura se o cliente já tem outro agendamento nessa mesma semana
    existing = db.query(Appointment).filter(
        Appointment.client_id == client_id,
        Appointment.start_time >= start_of_week,
        Appointment.start_time < end_of_week
    ).first()
    
    if existing:
        formatted_date = existing.start_time.strftime("%d/%m/%Y")
        formatted_time = existing.start_time.strftime("%H:%M")
        return (
            f"O cliente já possui um agendamento nesta semana no dia {formatted_date} às {formatted_time}. "
            f"Sugerimos agendar seus novos serviços na mesma data para sua maior conveniência."
        )
    return None

def build_appointment_response(appointment: Appointment, suggestion: Optional[str] = None) -> AppointmentResponse:
    services_list = []
    for app_svc in appointment.services:
        services_list.append(
            AppointmentServiceResponse(
                service_id=app_svc.service_id,
                name=app_svc.service.name,
                status=app_svc.status,
                price_at_booking=app_svc.price_at_booking,
                duration_at_booking=app_svc.duration_at_booking
            )
        )
    
    return AppointmentResponse(
        id=appointment.id,
        client_id=appointment.client_id,
        client_name=appointment.client.name,
        start_time=appointment.start_time,
        end_time=appointment.end_time,
        status=appointment.status,
        notes=appointment.notes,
        services=services_list,
        suggestion=suggestion
    )

def create_appointment(db: Session, appointment_data: AppointmentCreate) -> AppointmentResponse:
    # verifica se o cliente existe no banco
    client = db.query(Client).filter(Client.id == appointment_data.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente com ID {appointment_data.client_id} não encontrado."
        )
    
    # verifica se todos os serviços solicitados existem no banco
    services = db.query(BeautyService).filter(BeautyService.id.in_(appointment_data.service_ids)).all()
    if len(services) != len(appointment_data.service_ids):
        found_ids = {s.id for s in services}
        missing_ids = set(appointment_data.service_ids) - found_ids
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Serviço(s) com ID(s) {list(missing_ids)} não encontrado(s)."
        )
    
    # cria o aviso caso o cliente já tenha outro agendamento na semana
    suggestion = check_weekly_suggestion(db, appointment_data.client_id, appointment_data.start_time)
    
    # calcula o tempo total dos serviços e a hora que vai terminar
    total_duration = sum(s.duration for s in services)
    end_time = appointment_data.start_time + timedelta(minutes=total_duration)
    
    # salva as informações principais do agendamento
    db_appointment = Appointment(
        client_id=appointment_data.client_id,
        start_time=appointment_data.start_time,
        end_time=end_time,
        status=AppointmentStatus.SOLICITADO,
        notes=appointment_data.notes
    )
    db.add(db_appointment)
    db.flush()  # gera o ID do agendamento
    
    # salva cada serviço escolhido dentro desse agendamento
    for s in services:
        app_svc = AppointmentService(
            appointment_id=db_appointment.id,
            service_id=s.id,
            status=AppointmentServiceStatus.PENDENTE,
            price_at_booking=s.price,
            duration_at_booking=s.duration
        )
        db.add(app_svc)
        
    db.commit()
    db.refresh(db_appointment)
    
    return build_appointment_response(db_appointment, suggestion=suggestion)

def update_appointment(db: Session, appointment_id: int, update_data: AppointmentUpdate) -> AppointmentResponse:
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agendamento com ID {appointment_id} não encontrado."
        )
    
    # regra de segurança: só deixa mudar se faltar pelo menos 2 dias para o agendamento
    time_difference = db_appointment.start_time - datetime.now()
    if time_difference < timedelta(days=2):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Não é possível alterar este agendamento pois faltam menos de 2 dias para a data marcada. "
                "Alterações com prazo inferior a 2 dias devem ser solicitadas exclusivamente por telefone."
            )
        )
    
    # atualiza as observações e o status se foram passados
    if update_data.notes is not None:
        db_appointment.notes = update_data.notes
        
    if update_data.status is not None:
        db_appointment.status = update_data.status
        
    # recalcula o horário de término se mudar a hora de início ou os serviços
    new_start_time = update_data.start_time if update_data.start_time is not None else db_appointment.start_time
    
    if update_data.service_ids is not None:
        # confere se os novos serviços existem no banco
        services = db.query(BeautyService).filter(BeautyService.id.in_(update_data.service_ids)).all()
        if len(services) != len(update_data.service_ids):
            found_ids = {s.id for s in services}
            missing_ids = set(update_data.service_ids) - found_ids
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Serviço(s) com ID(s) {list(missing_ids)} não encontrado(s)."
            )
        
        # apaga os serviços antigos do agendamento
        db.query(AppointmentService).filter(AppointmentService.appointment_id == appointment_id).delete()
        
        # adiciona a lista de novos serviços no agendamento
        for s in services:
            app_svc = AppointmentService(
                appointment_id=appointment_id,
                service_id=s.id,
                status=AppointmentServiceStatus.PENDENTE,
                price_at_booking=s.price,
                duration_at_booking=s.duration
            )
            db.add(app_svc)
            
        total_duration = sum(s.duration for s in services)
        db_appointment.end_time = new_start_time + timedelta(minutes=total_duration)
    elif update_data.start_time is not None:
        # se mudou só o horário de início, calcula a nova hora final baseada na duração salva no banco
        total_duration = sum(app_svc.duration_at_booking for app_svc in db_appointment.services)
        db_appointment.end_time = new_start_time + timedelta(minutes=total_duration)
        
    if update_data.start_time is not None:
        db_appointment.start_time = update_data.start_time
        
    db.commit()
    db.refresh(db_appointment)
    
    return build_appointment_response(db_appointment)

def get_appointment(db: Session, appointment_id: int) -> AppointmentResponse:
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agendamento com ID {appointment_id} não encontrado."
        )
    return build_appointment_response(db_appointment)

def delete_appointment(db: Session, appointment_id: int):
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agendamento com ID {appointment_id} não encontrado."
        )
        
    db.delete(db_appointment)
    db.commit()


def list_appointments(
    db: Session,
    client_id: Optional[int] = None,
    status_filter: Optional[AppointmentStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[AppointmentResponse]:
    query = db.query(Appointment)
    
    if client_id is not None:
        query = query.filter(Appointment.client_id == client_id)
        
    if status_filter is not None:
        query = query.filter(Appointment.status == status_filter)
        
    if start_date is not None:
        query = query.filter(Appointment.start_time >= start_date)
        
    if end_date is not None:
        # Use exclusive end bound to match report_service (start_time < end_of_week)
        query = query.filter(Appointment.start_time < end_date)
        
    appointments = query.order_by(Appointment.start_time.asc()).all()
    return [build_appointment_response(app) for app in appointments]

def confirm_appointment(db: Session, appointment_id: int) -> AppointmentResponse:
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agendamento com ID {appointment_id} não encontrado."
        )

    if db_appointment.status != AppointmentStatus.SOLICITADO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Só é possível confirmar agendamentos com status 'solicitado'. "
                f"Status atual: '{db_appointment.status.value}'."
            )
        )
    
    db_appointment.status = AppointmentStatus.CONFIRMADO
    db.commit()
    db.refresh(db_appointment)
    
    return build_appointment_response(db_appointment)

def cancel_appointment(db: Session, appointment_id: int, bypass_limit: bool = False) -> AppointmentResponse:
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agendamento com ID {appointment_id} não encontrado."
        )

    if db_appointment.status == AppointmentStatus.CANCELADO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este agendamento já está cancelado."
        )

    if db_appointment.status == AppointmentStatus.CONCLUIDO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível cancelar um agendamento concluído."
        )
    
    if not bypass_limit:
        # regra de segurança: só deixa cancelar se faltar pelo menos 2 dias para o agendamento
        time_difference = db_appointment.start_time - datetime.now()
        if time_difference < timedelta(days=2):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Não é possível cancelar este agendamento pois faltam menos de 2 dias para a data marcada. "
                    "Cancelamentos com prazo inferior a 2 dias devem ser solicitados exclusivamente por telefone."
                )
            )
    
    db_appointment.status = AppointmentStatus.CANCELADO
    
    # Também definimos todos os serviços vinculados a este agendamento como CANCELADO
    for app_svc in db_appointment.services:
        app_svc.status = AppointmentServiceStatus.CANCELADO
        
    db.commit()
    db.refresh(db_appointment)
    
    return build_appointment_response(db_appointment)


def update_service_status(
    db: Session, appointment_id: int, service_id: int, new_status: AppointmentServiceStatus
) -> AppointmentResponse:
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agendamento com ID {appointment_id} não encontrado."
        )
    
    # busca a relação entre o agendamento e o serviço específico
    app_svc = db.query(AppointmentService).filter(
        and_(
            AppointmentService.appointment_id == appointment_id,
            AppointmentService.service_id == service_id
        )
    ).first()
    
    if not app_svc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Serviço com ID {service_id} não associado ao agendamento {appointment_id}."
        )
        
    app_svc.status = new_status
    db.commit()
    db.refresh(db_appointment)
    
    return build_appointment_response(db_appointment)
