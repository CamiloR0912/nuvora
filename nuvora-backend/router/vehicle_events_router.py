from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from config.db import SessionLocal
from model.vehicles import Vehicle

vehicle_events_router = APIRouter(prefix="/vehicle-events", tags=["Vehicle Events"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@vehicle_events_router.get("/count")
def get_vehicle_events_count(db: Session = Depends(get_db)):
    """Obtiene el total de eventos de vehículos detectados"""
    count = db.query(func.count(Vehicle.id)).scalar()
    return {"count": count}


@vehicle_events_router.get("/today")
def get_today_detections(db: Session = Depends(get_db)):
    """Obtiene las detecciones del día actual"""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    detections = db.query(Vehicle).filter(Vehicle.timestamp >= today).all()
    
    return {
        "count": len(detections),
        "detections": [
            {
                "id": d.id,
                "vehicle_type": d.vehicle_type,
                "confidence": d.confidence,
                "timestamp": d.timestamp,
                "plate_number": d.plate_number
            }
            for d in detections
        ]
    }


@vehicle_events_router.get("/latest")
def get_latest_detection(db: Session = Depends(get_db)):
    """Obtiene la última detección registrada"""
    latest = db.query(Vehicle).order_by(Vehicle.timestamp.desc()).first()
    
    if not latest:
        raise HTTPException(status_code=404, detail="No hay detecciones registradas")
    
    return {
        "id": latest.id,
        "vehicle_type": latest.vehicle_type,
        "confidence": latest.confidence,
        "timestamp": latest.timestamp,
        "plate_number": latest.plate_number,
        "location": latest.location
    }


@vehicle_events_router.get("/stats")
def get_detection_stats(db: Session = Depends(get_db)):
    """Obtiene estadísticas de detecciones"""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Total de detecciones
    total = db.query(func.count(Vehicle.id)).scalar()
    
    # Detecciones de hoy
    today_count = db.query(func.count(Vehicle.id)).filter(Vehicle.timestamp >= today).scalar()
    
    # Detecciones por tipo
    by_type = db.query(
        Vehicle.vehicle_type,
        func.count(Vehicle.id).label("count")
    ).group_by(Vehicle.vehicle_type).all()
    
    return {
        "total_detections": total,
        "today_detections": today_count,
        "by_type": {vtype: count for vtype, count in by_type}
    }
