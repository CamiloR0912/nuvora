from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from config.db import SessionLocal
from model.vehicles import VehiculoActivo, VehiculoHistorial
from schema.vehicle_schema import VehiculoEntrada, VehiculoSalida, VehiculoActivoResponse, VehiculoHistorialResponse

vehiculo = APIRouter(prefix="/vehiculos", tags=["Vehículos"])

# Dependencia de sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para calcular el total facturado (ejemplo: 5000 pesos por hora)
def calcular_total_facturado(fecha_entrada: datetime, fecha_salida: datetime) -> float:
    # Asegurar que ambas fechas sean naive (sin timezone)
    if fecha_entrada.tzinfo is not None:
        fecha_entrada = fecha_entrada.replace(tzinfo=None)
    if fecha_salida.tzinfo is not None:
        fecha_salida = fecha_salida.replace(tzinfo=None)
    
    tiempo_estacionado = fecha_salida - fecha_entrada
    horas = tiempo_estacionado.total_seconds() / 3600
    tarifa_por_hora = 5000  # Puedes ajustar esta tarifa
    return round(horas * tarifa_por_hora, 2)

@vehiculo.post("/entrada", response_model=VehiculoActivoResponse)
def registrar_entrada(data: VehiculoEntrada, db: Session = Depends(get_db)):
    existente = db.query(VehiculoActivo).filter(VehiculoActivo.placa == data.placa).first()
    if existente:
        raise HTTPException(status_code=400, detail="El vehículo ya está registrado como activo")

    fecha = data.fecha_entrada or datetime.now()
    # Asegurar que sea naive
    if fecha.tzinfo is not None:
        fecha = fecha.replace(tzinfo=None)

    nuevo = VehiculoActivo(
        placa=data.placa,
        fecha_entrada=fecha
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@vehiculo.post("/salida", response_model=VehiculoHistorialResponse)
def registrar_salida(data: VehiculoSalida, db: Session = Depends(get_db)):
    vehiculo_activo = db.query(VehiculoActivo).filter(VehiculoActivo.placa == data.placa).first()
    if not vehiculo_activo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado en activos")

    # Calcular el total facturado
    total = calcular_total_facturado(vehiculo_activo.fecha_entrada, data.fecha_salida)

    # Asegurar que fecha_salida sea naive
    fecha_salida = data.fecha_salida
    if fecha_salida.tzinfo is not None:
        fecha_salida = fecha_salida.replace(tzinfo=None)

    historial = VehiculoHistorial(
        placa=vehiculo_activo.placa,
        fecha_entrada=vehiculo_activo.fecha_entrada,
        fecha_salida=fecha_salida,
        total_facturado=total
    )

    db.add(historial)
    db.delete(vehiculo_activo)
    db.commit()
    db.refresh(historial)
    return historial

@vehiculo.get("/activos", response_model=list[VehiculoActivoResponse])
def listar_activos(db: Session = Depends(get_db)):
    return db.query(VehiculoActivo).all()

@vehiculo.get("/historial", response_model=list[VehiculoHistorialResponse])
def listar_historial(db: Session = Depends(get_db)):
    return db.query(VehiculoHistorial).all()

@vehiculo.get("/buscar/{placa}")
def buscar_por_placa(placa: str, db: Session = Depends(get_db)):
    activo = db.query(VehiculoActivo).filter(VehiculoActivo.placa == placa).first()
    if activo:
        return {"estado": "activo", "vehiculo": VehiculoActivoResponse.from_orm(activo)}

    historial = db.query(VehiculoHistorial).filter(VehiculoHistorial.placa == placa).order_by(VehiculoHistorial.id.desc()).first()
    if historial:
        return {"estado": "historial", "vehiculo": VehiculoHistorialResponse.from_orm(historial)}

    raise HTTPException(status_code=404, detail="Vehículo no encontrado")