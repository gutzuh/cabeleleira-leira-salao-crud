from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Client
from app.schemas import ClientCreate, ClientUpdate, ClientResponse

router = APIRouter(prefix="/clients", tags=["Clients"])

@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(client_data: ClientCreate, db: Session = Depends(get_db)):
    existing = db.query(Client).filter(Client.email == client_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um cliente cadastrado com este e-mail."
        )
    db_client = Client(
        name=client_data.name,
        email=client_data.email,
        phone=client_data.phone
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@router.get("", response_model=List[ClientResponse])
def list_clients(db: Session = Depends(get_db)):
    return db.query(Client).all()

@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente com ID {client_id} não encontrado."
        )
    return client

@router.put("/{client_id}", response_model=ClientResponse)
def update_client(client_id: int, client_data: ClientUpdate, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente com ID {client_id} não encontrado."
        )
    
    if client_data.email is not None and client_data.email != client.email:
        existing = db.query(Client).filter(Client.email == client_data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um cliente cadastrado com este e-mail."
            )
        client.email = client_data.email
        
    if client_data.name is not None:
        client.name = client_data.name
        
    if client_data.phone is not None:
        client.phone = client_data.phone
        
    db.commit()
    db.refresh(client)
    return client

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente com ID {client_id} não encontrado."
        )
    db.delete(client)
    db.commit()
