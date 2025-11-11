// src/api/vehiculosApi.js
import { http } from "./http";

// 1️⃣ Obtener todos los vehículos activos
export const getVehiculosActivos = () => http.get("/vehiculos/activos");

// 2️⃣ Obtener historial de vehículos
export const getVehiculosHistorial = () => http.get("/vehiculos/historial");

// 3️⃣ Registrar entrada
export const registrarEntrada = (data) => http.post("/vehiculos/entrada", data);

// 4️⃣ Registrar salida (con logging interno)
export const registrarSalida = (data) => {
  // Log para depuración (se ejecuta en tiempo de llamada)
  console.log("📤 [vehiculosApi] registrarSalida -> payload:", data);
  return http.post("/vehiculos/salida", data);
};

// 5️⃣ Buscar por placa
export const buscarPorPlaca = (placa) =>
  http.get(`/vehiculos/buscar/${encodeURIComponent(placa)}`);
