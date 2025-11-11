"""
Script para limpiar todas las tablas de la base de datos
Mantiene la estructura pero elimina todos los datos
"""
from sqlalchemy import text
from config.db import SessionLocal, engine
from model.users import User
from model.clientes import Cliente
from model.vehiculos import Vehiculo
from model.turnos import Turno
from model.tickets import Ticket
from model.cierres import CierreCaja

def reset_database():
    """Limpia todas las tablas de la base de datos"""
    db = SessionLocal()
    
    try:
        print("🗑️  Iniciando limpieza de base de datos...")
        
        # Deshabilitar checks de foreign keys temporalmente
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        
        # Eliminar datos en orden (respetando dependencias)
        print("   Eliminando cierres de caja...")
        db.query(CierreCaja).delete()
        
        print("   Eliminando tickets...")
        db.query(Ticket).delete()
        
        print("   Eliminando turnos...")
        db.query(Turno).delete()
        
        print("   Eliminando vehículos...")
        db.query(Vehiculo).delete()
        
        print("   Eliminando clientes...")
        db.query(Cliente).delete()
        
        print("   Eliminando usuarios...")
        db.query(User).delete()
        
        # Re-habilitar checks de foreign keys
        db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        
        # Resetear auto_increment de todas las tablas
        print("   Reseteando IDs de auto-incremento...")
        db.execute(text("ALTER TABLE cierres_caja AUTO_INCREMENT = 1"))
        db.execute(text("ALTER TABLE tickets AUTO_INCREMENT = 1"))
        db.execute(text("ALTER TABLE turnos AUTO_INCREMENT = 1"))
        db.execute(text("ALTER TABLE vehiculos AUTO_INCREMENT = 1"))
        db.execute(text("ALTER TABLE clientes AUTO_INCREMENT = 1"))
        db.execute(text("ALTER TABLE usuarios AUTO_INCREMENT = 1"))
        
        db.commit()
        print("✅ Base de datos limpiada exitosamente")
        print("📊 Todas las tablas están vacías y los IDs reseteados")
        
    except Exception as e:
        print(f"❌ Error al limpiar la base de datos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    print("⚠️  ADVERTENCIA: Esta acción eliminará TODOS los datos de la base de datos")
    print("   - Usuarios")
    print("   - Clientes")
    print("   - Vehículos")
    print("   - Turnos")
    print("   - Tickets")
    print("   - Cierres de caja")
    print()
    
    # Pedir confirmación
    respuesta = input("¿Estás seguro de que deseas continuar? (escribe 'SI' para confirmar): ")
    
    if respuesta.strip().upper() == "SI":
        reset_database()
    else:
        print("❌ Operación cancelada")
        sys.exit(0)
