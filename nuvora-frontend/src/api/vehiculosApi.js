import axios from "axios";

const api = axios.create({
  baseURL: "/api/vehiculos",
});

// 1️⃣ Obtener todos los vehículos activos
export const getVehiculosActivos = () => api.get("/activos");

// 2️⃣ Obtener historial de vehículos
export const getVehiculosHistorial = () => api.get("/historial");

// 3️⃣ Registrar entrada
export const registrarEntrada = (data) =>
  api.post("/entrada", data); // { placa, fecha_entrada (ISO opcional) }

// 4️⃣ Registrar salida
export const registrarSalida = (data) =>
  api.post("/salida", data); // { placa, fecha_salida (ISO obligatorio) }

// 5️⃣ Buscar por placa
export const buscarPorPlaca = (placa) =>
  api.get(`/buscar/${encodeURIComponent(placa)}`);
