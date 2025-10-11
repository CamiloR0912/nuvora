import { Clock, Car } from 'lucide-react';

export function VehicleList({ vehicles }) {
  const formatDuration = (entryTime) => {
    const now = new Date();
    const entry = new Date(entryTime);
    const diffMs = now - entry;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);

    if (diffHours > 0) {
      return `${diffHours}h ${diffMins % 60}m`;
    }
    return `${diffMins}m`;
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
      <h2 className="text-xl font-bold text-gray-900 mb-6">Vehículos Activos</h2>

      <div className="space-y-3">
        {vehicles.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No hay vehículos en el parqueadero</p>
        ) : (
          vehicles.map((vehicle) => (
            <div
              key={vehicle.id}
              className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-center space-x-4">
                <div className="bg-blue-100 p-2 rounded-lg">
                  <Car className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <p className="font-bold text-gray-900">{vehicle.license_plate}</p>
                  <p className="text-sm text-gray-600">
                    Cupo: {vehicle.parking_spaces?.space_number || 'N/A'}
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-2 text-gray-600">
                <Clock className="w-4 h-4" />
                <span className="text-sm font-medium">
                  {formatDuration(vehicle.entry_time)}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
