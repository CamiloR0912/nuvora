import { Car } from 'lucide-react';

export function ParkingSpaceGrid({ spaces }) {
  const groupedSpaces = spaces.reduce((acc, space) => {
    const key = `${space.floor} - Zona ${space.zone}`;
    if (!acc[key]) {
      acc[key] = [];
    }
    acc[key].push(space);
    return acc;
  }, {});

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
      <h2 className="text-xl font-bold text-gray-900 mb-6">Estado de Cupos</h2>

      <div className="space-y-6">
        {Object.entries(groupedSpaces).map(([group, groupSpaces]) => (
          <div key={group}>
            <h3 className="text-sm font-semibold text-gray-700 mb-3">{group}</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
              {groupSpaces.map((space) => (
                <div
                  key={space.id}
                  className={`relative p-4 rounded-lg border-2 transition-all ${
                    space.is_occupied
                      ? 'bg-red-50 border-red-300'
                      : 'bg-green-50 border-green-300'
                  }`}
                >
                  <div className="flex flex-col items-center justify-center">
                    <Car
                      className={`w-6 h-6 mb-2 ${
                        space.is_occupied ? 'text-red-600' : 'text-green-600'
                      }`}
                    />
                    <span className="text-sm font-bold text-gray-900">
                      {space.space_number}
                    </span>
                    <span
                      className={`text-xs mt-1 ${
                        space.is_occupied ? 'text-red-600' : 'text-green-600'
                      }`}
                    >
                      {space.is_occupied ? 'Ocupado' : 'Libre'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
