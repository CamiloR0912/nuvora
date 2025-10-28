import React, { useEffect, useState } from "react";
import { Activity, ArrowUpCircle, ArrowDownCircle } from "lucide-react";
import axios from "axios";

export default function ActividadPage() {
  const [eventos, setEventos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      axios.get('/api/vehiculos/activos'),
      axios.get('/api/vehiculos/historial')
    ])
      .then(([activosRes, historialRes]) => {
        const entradas = activosRes.data
          .map((vehiculo) => ({
            id: `entrada-${vehiculo.id}`,
            event_type: 'entry',
            event_data: {
              description: `Vehículo ${vehiculo.placa} ingresó al parqueadero`
            },
            created_at: vehiculo.fecha_entrada
          }));

        const salidas = historialRes.data
          .map((vehiculo) => ({
            id: `salida-${vehiculo.id}`,
            event_type: 'exit',
            event_data: {
              description: `Vehículo ${vehiculo.placa} salió del parqueadero`
            },
            created_at: vehiculo.fecha_salida
          }));

        const ambos = [...entradas, ...salidas]
          .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

        setEventos(ambos);
      })
      .catch(() => {
        setEventos([]);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-2xl mx-auto py-8">
      <div className="flex items-center mb-7">
        <Activity className="w-7 h-7 text-purple-600 mr-3" />
        <h2 className="text-2xl font-bold text-gray-900">Actividad completa</h2>
      </div>
      {loading ? (
        <div className="bg-white rounded-xl shadow p-8 text-center text-gray-500 text-lg">
          Cargando actividad...
        </div>
      ) : eventos.length === 0 ? (
        <div className="bg-white rounded-xl shadow p-8 text-center text-gray-500 text-lg">
          No hay actividad registrada.
        </div>
      ) : (
        <ul className="divide-y divide-gray-100">
          {eventos.map(evt => (
            <li key={evt.id} className="flex items-center gap-4 py-6">
              {evt.event_type === "entry"
                ? <ArrowDownCircle className="w-6 h-6 text-green-600" />
                : <ArrowUpCircle className="w-6 h-6 text-blue-600" />}
              <div>
                <p className="text-lg font-medium text-gray-900">
                  {evt.event_data.description}
                </p>
                <span className="text-xs text-gray-500 block">
                  {evt.event_type === "entry"
                    ? `Entrada: ${new Date(evt.created_at).toLocaleString()}`
                    : `Salida: ${new Date(evt.created_at).toLocaleString()}`}
                </span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
