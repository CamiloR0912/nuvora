import { ArrowDownCircle, ArrowUpCircle, Activity } from 'lucide-react';

const eventos = [
  {
    id: 1,
    tipo: 'entry',
    placa: 'ABC123',
    descripcion: 'Vehículo ABC123 ingresó al parqueadero',
    hora: '19:32:10'
  },
  {
    id: 2,
    tipo: 'exit',
    placa: 'XYZ987',
    descripcion: 'Vehículo XYZ987 salió del parqueadero',
    hora: '18:55:28'
  },
  {
    id: 3,
    tipo: 'entry',
    placa: 'KLJ456',
    descripcion: 'Vehículo KLJ456 ingresó al parqueadero',
    hora: '17:21:04'
  },
];

function iconoEvento(tipo) {
  if (tipo === 'entry') return <ArrowDownCircle className="w-6 h-6 text-emerald-600" />;
  if (tipo === 'exit') return <ArrowUpCircle className="w-6 h-6 text-blue-600" />;
  return <Activity className="w-6 h-6 text-gray-600" />;
}

export default function ActividadPage() {
  return (
    <div className="max-w-2xl mx-auto py-8">
      <div className="flex items-center mb-7">
        <Activity className="w-7 h-7 text-purple-600 mr-3" />
        <h2 className="text-2xl font-bold text-gray-900">Actividad Reciente</h2>
      </div>
      {eventos.length === 0 ? (
        <div className="bg-white rounded-xl shadow p-8 text-center text-gray-500 text-lg">
          No hay actividad registrada.
        </div>
      ) : (
        <ul className="divide-y divide-gray-100">
          {eventos.map(evt => (
            <li key={evt.id} className="flex items-center gap-4 py-6">
              {/* Ícono */}
              <div>
                {iconoEvento(evt.tipo)}
              </div>
              {/* Detalles */}
              <div>
                <p className="text-lg font-medium text-gray-900">{evt.descripcion}</p>
                <span className="text-xs text-gray-500">
                  Placa: <span className="font-semibold">{evt.placa}</span> · Hora: {evt.hora}
                </span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
