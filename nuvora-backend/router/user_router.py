from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from werkzeug.security import generate_password_hash, check_password_hash

from config.db import SessionLocal
from model.users import User
from schema.user_schema import UserBase, UserResponse

user = APIRouter(prefix="/users", tags=["Usuarios"])

# 🔹 Dependencia de sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 1️⃣ Obtener todos los usuarios
@user.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


# 2️⃣ Obtener un usuario por ID
@user.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    usuario = db.query(User).filter(User.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


# 3️⃣ Crear usuario nuevo
@user.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(data: UserBase, db: Session = Depends(get_db)):
    # Verificar si ya existe el username
    existing_user = db.query(User).filter(User.username == data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")

    hashed_password = generate_password_hash(data.user_passw, method="pbkdf2:sha256", salt_length=30)
    new_user = User(
        name=data.name,
        username=data.username,
        user_passw=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# 4️⃣ Verificar contraseña (opcional)
@user.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.username == username).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not check_password_hash(user_db.user_passw, password):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    return {"message": "Inicio de sesión exitoso", "user_id": user_db.id}
