// src/api/vehiculosApi.js
import { http } from "./http";

// 1️⃣ Obtener todos los vehículos activos (tickets abiertos)
export const getVehiculosActivos = () => http.get("/tickets/abiertos");

// 2️⃣ Obtener historial de tickets (todos los tickets del turno actual)
export const getVehiculosHistorial = () => http.get("/tickets/");

// 3️⃣ Registrar entrada
export const registrarEntrada = (data) => http.post("/tickets/entrada", data);

// 4️⃣ Registrar salida (con logging interno)
export const registrarSalida = (data) => {
  // Log para depuración (se ejecuta en tiempo de llamada)
  console.log("📤 [vehiculosApi] registrarSalida -> payload:", data);
  return http.post("/tickets/salida", data);
};

// 5️⃣ Buscar por placa
export const buscarPorPlaca = (placa) =>
  http.get(`/tickets/buscar-placa/${encodeURIComponent(placa)}`);
