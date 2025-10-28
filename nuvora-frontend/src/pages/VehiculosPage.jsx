import React, { useEffect, useState } from "react";
import { Car, Clock } from "lucide-react";
import { getVehiculosActivos } from "../api/vehiculosApi";

function formatDuration(fecha_entrada) {
  const entryTime = new Date(fecha_entrada);
  const now = new Date();
  const diffMs = now - entryTime;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours > 0) {
    return `${diffHours}h ${diffMins % 60}m`;
  }
  return `${diffMins}m`;
}

export default function VehiculosPage() {
  const [vehiculos, setVehiculos] = useState([]); // Siempre array
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getVehiculosActivos()
      .then((res) => {
        // Asegura que res.data sea siempre un array
        if (Array.isArray(res.data)) {
          setVehiculos(res.data);
        } else {
          setVehiculos([]);
        }
        setError("");
      })
      .catch(() => {
        setVehiculos([]);
        setError("No se pudieron obtener los vehículos.");
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-3xl mx-auto py-8">
      <div className="flex items-center mb-6">
        <Car className="w-7 h-7 text-blue-600 mr-3" />
        <h2 className="text-2xl font-bold text-gray-900">Vehículos en el Parqueadero</h2>
      </div>

      {loading ? (
        <div className="text-center py-8">Cargando...</div>
      ) : error ? (
        <div className="bg-red-100 text-red-800 rounded-xl shadow p-8 text-center text-lg">
          {error}
        </div>
      ) : vehiculos.length === 0 ? (
        <div className="bg-white rounded-xl shadow p-8 text-center text-gray-500 text-lg">
          No hay vehículos actualmente en el parqueadero.
        </div>
      ) : (
        <ul className="space-y-4">
          {vehiculos.map((v) => (
            <li
              key={v.id}
              className="flex items-center justify-between bg-white p-5 rounded-xl shadow-sm border border-slate-100 hover:shadow transition"
            >
              <div className="flex items-center gap-4">
                <div className="bg-blue-100 p-3 rounded-lg">
                  <Car className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <div className="text-lg font-semibold text-gray-800">{v.placa}</div>
                  <div className="text-xs text-gray-500">
                    Ingreso:{" "}
                    <span className="font-medium">
                      {new Date(v.fecha_entrada).toLocaleString()}
                    </span>
                  </div>
                  <div className="text-xs text-gray-500">
                    Cupo: <span className="font-medium">{v.espacio ?? "-"}</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center text-gray-600 text-sm">
                <Clock className="w-4 h-4 mr-2" />
                <span className="font-medium">{formatDuration(v.fecha_entrada)}</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
