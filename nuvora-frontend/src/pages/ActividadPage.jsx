import React, { useEffect, useState } from "react";
import { Activity, ArrowUpCircle, ArrowDownCircle } from "lucide-react";
import { http } from "../api/http";

export default function ActividadPage() {
  const [eventos, setEventos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Usar endpoint de tickets en lugar de vehiculos
    http.get('/tickets')
      .then((response) => {
        const todosLosTickets = response.data;

        // Crear eventos de entrada (todos los tickets)
        const entradas = todosLosTickets
          .map((ticket) => ({
            id: `entrada-${ticket.id}`,
            event_type: 'entry',
            event_data: {
              description: `Vehículo ${ticket.placa} ingresó al parqueadero`
            },
            created_at: ticket.hora_entrada
          }));

        // Crear eventos de salida (solo tickets cerrados con hora_salida)
        const salidas = todosLosTickets
          .filter(ticket => ticket.estado === 'cerrado' && ticket.hora_salida)
          .map((ticket) => ({
            id: `salida-${ticket.id}`,
            event_type: 'exit',
            event_data: {
              description: `Vehículo ${ticket.placa} salió del parqueadero`
            },
            created_at: ticket.hora_salida
          }));

        // Combinar y ordenar por fecha más reciente
        const ambos = [...entradas, ...salidas]
          .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

        setEventos(ambos);
      })
      .catch((error) => {
        console.error('Error al cargar tickets:', error);
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
