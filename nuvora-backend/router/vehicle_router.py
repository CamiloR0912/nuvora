from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from config.db import SessionLocal
from model.vehiculos import Vehiculo
from model.tickets import Ticket
from schema.vehicle_schema import VehiculoEntrada, VehiculoSalida, VehiculoActivoResponse, VehiculoHistorialResponse

vehiculo = APIRouter(prefix="/vehiculos", tags=["Vehículos"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def calcular_total_facturado(fecha_entrada: datetime, fecha_salida: datetime) -> float:
    if fecha_entrada.tzinfo is not None:
        fecha_entrada = fecha_entrada.replace(tzinfo=None)
    if fecha_salida.tzinfo is not None:
        fecha_salida = fecha_salida.replace(tzinfo=None)
    tiempo_estacionado = fecha_salida - fecha_entrada
    horas = tiempo_estacionado.total_seconds() / 3600
    tarifa_por_hora = 5000
    return round(horas * tarifa_por_hora, 2)


@vehiculo.post("/entrada", response_model=VehiculoActivoResponse)
def registrar_entrada(data: VehiculoEntrada, db: Session = Depends(get_db)):
    existente = db.query(Vehiculo).filter(Vehiculo.placa == data.placa).first()
    if existente:
        raise HTTPException(status_code=400, detail="El vehículo ya está registrado como activo")

    fecha = data.fecha_entrada or datetime.now()
    if fecha.tzinfo is not None:
        fecha = fecha.replace(tzinfo=None)

    # crear ticket y vehiculo
    veh = db.query(Vehiculo).filter(Vehiculo.placa == data.placa).first()
    if not veh:
        veh = Vehiculo(placa=data.placa)
        db.add(veh)
        db.commit()
        db.refresh(veh)

    nuevo_ticket = Ticket(vehiculo_id=veh.id, hora_entrada=fecha)
    db.add(nuevo_ticket)
    db.commit()
    db.refresh(nuevo_ticket)

    return VehiculoActivoResponse(id=nuevo_ticket.id, placa=veh.placa, fecha_entrada=fecha)


@vehiculo.post("/salida", response_model=VehiculoHistorialResponse)
def registrar_salida(data: VehiculoSalida, db: Session = Depends(get_db)):
    # buscar ticket abierto por placa
    veh = db.query(Vehiculo).filter(Vehiculo.placa == data.placa).first()
    if not veh:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    ticket = db.query(Ticket).filter(Ticket.vehiculo_id == veh.id, Ticket.estado == 'abierto').order_by(Ticket.id.desc()).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket activo no encontrado para la placa")

    fecha_salida = data.fecha_salida
    if fecha_salida.tzinfo is not None:
        fecha_salida = fecha_salida.replace(tzinfo=None)

    total = calcular_total_facturado(ticket.hora_entrada, fecha_salida)
    ticket.hora_salida = fecha_salida
    ticket.monto_total = total
    ticket.estado = 'cerrado'
    db.commit()
    db.refresh(ticket)

    return VehiculoHistorialResponse(id=ticket.id, placa=veh.placa, fecha_entrada=ticket.hora_entrada, fecha_salida=fecha_salida, total_facturado=total)


@vehiculo.get("/activos", response_model=list[VehiculoActivoResponse])
def listar_activos(db: Session = Depends(get_db)):
    abiertos = db.query(Ticket).filter(Ticket.estado == 'abierto').all()
    result = []
    for t in abiertos:
        v = db.query(Vehiculo).filter(Vehiculo.id == t.vehiculo_id).first()
        result.append(VehiculoActivoResponse(id=t.id, placa=v.placa, fecha_entrada=t.hora_entrada))
    return result


@vehiculo.get("/historial", response_model=list[VehiculoHistorialResponse])
def listar_historial(db: Session = Depends(get_db)):
    cerrados = db.query(Ticket).filter(Ticket.estado == 'cerrado').all()
    result = []
    for t in cerrados:
        v = db.query(Vehiculo).filter(Vehiculo.id == t.vehiculo_id).first()
        result.append(VehiculoHistorialResponse(id=t.id, placa=v.placa, fecha_entrada=t.hora_entrada, fecha_salida=t.hora_salida, total_facturado=float(t.monto_total or 0.0)))
    return result
