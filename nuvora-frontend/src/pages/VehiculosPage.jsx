import { Car, Clock } from 'lucide-react';

// Datos simulados: solo vehículos actualmente en parqueadero
const vehiculosActivos = [
  {
    id: 1,
    license_plate: 'ABC123',
    entry_time: new Date(Date.now() - 1000 * 60 * 25), // hace 25 min
    parking_space: 'A2',
    owner: 'Juan Pérez'
  },
  {
    id: 2,
    license_plate: 'XYZ987',
    entry_time: new Date(Date.now() - 1000 * 60 * 110), // hace 1h 50min
    parking_space: 'C1',
    owner: 'María Gómez'
  },
];

function formatDuration(entryTime) {
  const now = new Date();
  const diffMs = now - new Date(entryTime);
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours > 0) {
    return `${diffHours}h ${diffMins % 60}m`;
  }
  return `${diffMins}m`;
}

export default function VehiculosPage() {
  return (
    <div className="max-w-3xl mx-auto py-8">
      <div className="flex items-center mb-6">
        <Car className="w-7 h-7 text-blue-600 mr-3" />
        <h2 className="text-2xl font-bold text-gray-900">Vehículos en el Parqueadero</h2>
      </div>
      {vehiculosActivos.length === 0 ? (
        <div className="bg-white rounded-xl shadow p-8 text-center text-gray-500 text-lg">
          No hay vehículos actualmente en el parqueadero.
        </div>
      ) : (
        <ul className="space-y-4">
          {vehiculosActivos.map(v => (
            <li
              key={v.id}
              className="flex items-center justify-between bg-white p-5 rounded-xl shadow-sm border border-slate-100 hover:shadow transition"
            >
              <div className="flex items-center gap-4">
                <div className="bg-blue-100 p-3 rounded-lg">
                  <Car className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <div className="text-lg font-semibold text-gray-800">{v.license_plate}</div>
                  <div className="text-xs text-gray-500">Cupo: <span className="font-medium">{v.parking_space}</span></div>
                  <div className="text-xs text-gray-500">Propietario: <span className="font-medium">{v.owner}</span></div>
                </div>
              </div>
              <div className="flex items-center text-gray-600 text-sm">
                <Clock className="w-4 h-4 mr-2" />
                <span className="font-medium">{formatDuration(v.entry_time)}</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
