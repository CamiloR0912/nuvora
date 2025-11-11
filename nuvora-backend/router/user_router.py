from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash

from config.auth import create_access_token, get_current_user, require_admin
from config.db import SessionLocal
from model.users import User
from model.turnos import Turno
from schema.user_schema import UserCreate, UserResponse

user = APIRouter(prefix="/users", tags=["Usuarios"])

# Dependencia de sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 📥 Modelo de login con monto inicial incluido
class LoginRequest(BaseModel):
    username: str
    password: str


# 1️⃣ Obtener todos los usuarios (solo admins)
@user.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.query(User).all()


# 2️⃣ Obtener usuario actual autenticado
@user.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "nombre": current_user.nombre,
        "usuario": current_user.usuario,
        "rol": current_user.rol,
        "activo": current_user.activo,
    }


# 3️⃣ Obtener usuario por ID (solo admins)
@user.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    usuario = db.query(User).filter(User.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


# 4️⃣ Crear usuario nuevo (solo admins)
@user.post("/", status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    existing_user = db.query(User).filter(User.usuario == data.usuario).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    hashed_password = generate_password_hash(data.password, method="pbkdf2:sha256", salt_length=30)
    new_user = User(
        nombre=data.nombre,
        rol=data.rol,
        usuario=data.usuario,
        password_hash=hashed_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Usuario creado correctamente", "usuario": new_user.usuario}


# 5️⃣ Login con creación automática de turno
@user.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    usuario_db = db.query(User).filter(User.usuario == data.username).first()

    if not usuario_db or not check_password_hash(usuario_db.password_hash, data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    # Buscar turno activo
    turno_activo = db.query(Turno).filter(
        Turno.usuario_id == usuario_db.id,
        Turno.estado == "abierto"
    ).first()

    # Si no hay turno activo, crear uno nuevo
    if not turno_activo:
        nuevo_turno = Turno(
            usuario_id=usuario_db.id,
            fecha_inicio=datetime.now(),
            estado="abierto",
            observaciones="Inicio automático al iniciar sesión"
        )
        db.add(nuevo_turno)
        db.commit()
        db.refresh(nuevo_turno)
        turno_activo = nuevo_turno

    # Crear JWT con info del usuario y turno
    token_data = {"sub": str(usuario_db.id), "turno_id": turno_activo.id}
    access_token = create_access_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario_db.id,
            "nombre": usuario_db.nombre,
            "rol": usuario_db.rol,
        },
        "turno": {
            "id": turno_activo.id,
            "fecha_inicio": turno_activo.fecha_inicio,
            "estado": turno_activo.estado,
        }
    }
