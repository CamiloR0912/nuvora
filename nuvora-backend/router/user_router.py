from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from werkzeug.security import check_password_hash, generate_password_hash
from config.auth import create_access_token, get_current_user, require_admin
from config.db import SessionLocal
from model.users import User
from schema.user_schema import UserCreate, UserResponse

user = APIRouter(prefix="/users", tags=["Usuarios"])

# 🔹 Dependencia de sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 1️⃣ Obtener todos los usuarios (solo admins)
@user.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.query(User).all()


# 2️⃣ Obtener usuario actual autenticado (debe ir ANTES de /{user_id})
@user.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "nombre": current_user.nombre,
        "usuario": current_user.usuario,
        "rol": current_user.rol.name if hasattr(current_user.rol, "name") else current_user.rol,
        "activo": current_user.activo,
    }


# 3️⃣ Obtener un usuario por ID (solo admins)
@user.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    usuario = db.query(User).filter(User.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


# 4️⃣ Crear usuario nuevo (solo admins)
@user.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    # Verificar si ya existe el username
    existing_user = db.query(User).filter(User.usuario == data.usuario).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")

    hashed_password = generate_password_hash(data.password, method="pbkdf2:sha256", salt_length=30)
    new_user = User(
        nombre=data.nombre,
        rol=data.rol,
        usuario=data.usuario,
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# 5️⃣ Login - devuelve JWT token
@user.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario_db = db.query(User).filter(User.usuario == form_data.username).first()
    if not usuario_db or not check_password_hash(usuario_db.password_hash, form_data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    
    # Buscar turno activo del usuario
    from model.turnos import Turno
    turno_activo = db.query(Turno).filter(
        Turno.usuario_id == usuario_db.id,
        Turno.estado == 'abierto'
    ).first()
    
    # Crear token con user_id y turno_id (si existe)
    token_data = {"sub": str(usuario_db.id)}
    if turno_activo:
        token_data["turno_id"] = turno_activo.id
    
    token = create_access_token(token_data)
    return {
        "access_token": token, 
        "token_type": "bearer",
        "turno_id": turno_activo.id if turno_activo else None
    }
