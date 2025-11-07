from werkzeug.security import generate_password_hash
from sqlalchemy.orm import Session
# Usar imports absolutos para poder ejecutar el script desde el directorio raíz del proyecto
from config.db import SessionLocal
from model.users import User

db = SessionLocal()
try:
    # Eliminar admin existente si hay
    existing = db.query(User).filter(User.usuario == 'admin').first()
    if existing:
        db.delete(existing)
        db.commit()
        print('🗑️ Usuario admin anterior eliminado')
    
    # Crear nuevo admin con hash correcto
    u = User(
        nombre='Administrador Principal',
        rol='admin',
        usuario='admin',
        password_hash=generate_password_hash('000', method='pbkdf2:sha256', salt_length=30),
        activo=True,
    )
    db.add(u)
    db.commit()
    print('✅ Usuario admin creado correctamente')
    print('📝 Usuario: admin')
    print('🔑 Password: 000')
except Exception as e:
    print(f'❌ Error: {e}')
    db.rollback()
finally:
    db.close()
