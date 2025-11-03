from werkzeug.security import generate_password_hash
from sqlalchemy.orm import Session
from config.db import SessionLocal
from model.users import User

def run():
    db: Session = SessionLocal()
    try:
        if not db.query(User).filter(User.usuario == "admin").first():
            u = User(
                nombre="Admin Test",
                rol="admin",
                usuario="admin",
                password_hash=generate_password_hash("123456"),
                activo=True,
            )
            db.add(u)
            db.commit()
            print("Usuario 'admin' creado con password 123456")
        else:
            print("Usuario 'admin' ya existe")
    finally:
        db.close()

if __name__ == "__main__":
    run()