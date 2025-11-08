from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from config.db import SessionLocal
from config.auth import get_current_user, require_admin
from model.clientes import Cliente
from model.users import User
from schema.cliente_schema import ClienteCreate, ClienteUpdate, ClienteResponse

client_router = APIRouter(prefix="/clientes", tags=["Clientes"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@client_router.post("/", response_model=ClienteResponse, status_code=201)
def crear_cliente(
    data: ClienteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea un nuevo cliente. Requiere autenticación.
    """
    # Validar tipo_cliente
    if data.tipo_cliente not in ['visitante', 'abonado']:
        raise HTTPException(status_code=400, detail="tipo_cliente debe ser 'visitante' o 'abonado'")
    
    # Verificar si ya existe un cliente con ese correo (si se proporciona)
    if data.correo:
        existente = db.query(Cliente).filter(Cliente.correo == data.correo).first()
        if existente:
            raise HTTPException(status_code=400, detail="Ya existe un cliente con ese correo")
    
    nuevo_cliente = Cliente(
        nombre=data.nombre,
        telefono=data.telefono,
        correo=data.correo,
        tipo_cliente=data.tipo_cliente
    )
    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)
    return nuevo_cliente

@client_router.get("/", response_model=List[ClienteResponse])
def listar_clientes(
    tipo: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todos los clientes. Opcionalmente filtra por tipo (visitante/abonado).
    """
    query = db.query(Cliente)
    
    if tipo:
        if tipo not in ['visitante', 'abonado']:
            raise HTTPException(status_code=400, detail="tipo debe ser 'visitante' o 'abonado'")
        query = query.filter(Cliente.tipo_cliente == tipo)
    
    clientes = query.order_by(Cliente.created_at.desc()).all()
    return clientes

@client_router.get("/{cliente_id}", response_model=ClienteResponse)
def obtener_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene un cliente por su ID.
    """
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@client_router.put("/{cliente_id}", response_model=ClienteResponse)
def actualizar_cliente(
    cliente_id: int,
    data: ClienteUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Actualiza un cliente. Solo admins pueden hacerlo.
    """
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Actualizar solo los campos proporcionados
    if data.nombre is not None:
        cliente.nombre = data.nombre
    if data.telefono is not None:
        cliente.telefono = data.telefono
    if data.correo is not None:
        # Verificar que el correo no esté en uso por otro cliente
        existente = db.query(Cliente).filter(
            Cliente.correo == data.correo,
            Cliente.id != cliente_id
        ).first()
        if existente:
            raise HTTPException(status_code=400, detail="Ese correo ya está en uso")
        cliente.correo = data.correo
    if data.tipo_cliente is not None:
        if data.tipo_cliente not in ['visitante', 'abonado']:
            raise HTTPException(status_code=400, detail="tipo_cliente debe ser 'visitante' o 'abonado'")
        cliente.tipo_cliente = data.tipo_cliente
    
    db.commit()
    db.refresh(cliente)
    return cliente

@client_router.delete("/{cliente_id}", status_code=204)
def eliminar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Elimina un cliente. Solo admins pueden hacerlo.
    """
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    db.delete(cliente)
    db.commit()
    return None

@client_router.get("/buscar/correo", response_model=ClienteResponse)
def buscar_por_correo(
    correo: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Busca un cliente por su correo electrónico.
    """
    cliente = db.query(Cliente).filter(Cliente.correo == correo).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado con ese correo")
    return cliente