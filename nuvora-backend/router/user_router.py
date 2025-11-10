from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from config.db import get_db
from model.users import User
from model.turnos import Turno
from config.auth import create_access_token

user = APIRouter(prefix="/api/users", tags=["users"])


# ---------------------- MODELOS DE ENTRADA ----------------------

class UserCreate(BaseModel):
    nombre: str
    rol: str
    usuario: str
    password: str


class LoginRequest(BaseModel):
    username: str = Field(..., example="admin")
    password: str = Field(..., example="000")
    monto_inicial: Optional[float] = Field(0.0, ge=0, example=20000)


# ---------------------- RUTAS ----------------------

@user.post("/register")
def register_user(data: UserCreate, db: Session = Depends(get_db)):
    """Crear un nuevo usuario"""
    existing_user = db.query(User).filter(User.usuario == data.usuario).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    hashed_password = generate_password_hash(data.password, method='pbkdf2:sha256', salt_length=30)
    new_user = User(
        nombre=data.nombre,
        rol=data.rol,
        usuario=data.usuario,
        password_hash=hashed_password,
        activo=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Usuario creado correctamente", "usuario": new_user.usuario}


@user.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Login via JSON: { username, password, monto_inicial }
    - Valida credenciales
    - Retorna JWT
    - Crea un turno ABIERTO para el usuario si no tiene uno abierto (usa monto_inicial)
    """
    usuario_db = db.query(User).filter(User.usuario == payload.username).first()
    if not usuario_db or not check_password_hash(usuario_db.password_hash, payload.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    # Crear token JWT
    token = create_access_token({"sub": str(usuario_db.id)})

    # Buscar turno abierto del usuario
    turno = db.query(Turno).filter(Turno.usuario_id == usuario_db.id, Turno.estado == 'abierto').first()

    # Si no existe, crear uno usando monto_inicial
    if not turno:
        turno = Turno(
            usuario_id=usuario_db.id,
            fecha_inicio=datetime.now(),
            monto_inicial=payload.monto_inicial or 0.0,
            estado='abierto'
        )
        try:
            db.add(turno)
            db.commit()
            db.refresh(turno)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al crear turno: {str(e)}")

    # Respuesta: token y datos del turno
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario_db.id,
            "nombre": usuario_db.nombre,
            "rol": usuario_db.rol,
            "usuario": usuario_db.usuario,
        },
        "turno": {
            "id": turno.id,
            "usuario_id": turno.usuario_id,
            "fecha_inicio": turno.fecha_inicio,
            "estado": turno.estado,
            "monto_inicial": float(turno.monto_inicial or 0.0)
        }
    }


@user.get("/")
def get_users(db: Session = Depends(get_db)):
    """Listar todos los usuarios"""
    users = db.query(User).all()
    return users


@user.get("/{id}")
def get_user(id: int, db: Session = Depends(get_db)):
    """Obtener un usuario por ID"""
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user
