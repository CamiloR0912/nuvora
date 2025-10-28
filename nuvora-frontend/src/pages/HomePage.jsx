import { useState, useEffect } from 'react';
import { StatCard } from '../components/StatCard';
import { ParkingSpaceGrid } from '../components/ParkingSpaceGrid';
import { VehicleList } from '../components/VehicleList';
import { RecentActivity } from '../components/RecentActivity';
import { VoiceControlPanel } from '../components/VoiceControlPanel';
import { Car, ParkingCircle, Clock } from 'lucide-react';

// Datos simulados de ejemplo
const mockParkingSpaces = [
  { id: 1, floor: 1, zone: 'A', space_number: 'A1', is_occupied: false },
  { id: 2, floor: 1, zone: 'A', space_number: 'A2', is_occupied: true },
  { id: 3, floor: 1, zone: 'B', space_number: 'B1', is_occupied: false },
  { id: 4, floor: 2, zone: 'C', space_number: 'C1', is_occupied: true },
  { id: 5, floor: 2, zone: 'C', space_number: 'C2', is_occupied: false },
];

const mockVehicles = [
  {
    id: 1,
    license_plate: 'ABC123',
    entry_time: new Date(Date.now() - 1000 * 60 * 45), // hace 45 min
    parking_spaces: { space_number: 'A2' },
  },
  {
    id: 2,
    license_plate: 'XYZ987',
    entry_time: new Date(Date.now() - 1000 * 60 * 120), // hace 2h
    parking_spaces: { space_number: 'C1' },
  },
];

const mockEvents = [
  {
    id: 1,
    event_type: 'entry',
    event_data: { description: 'Vehículo ABC123 ingresó al parqueadero' },
    created_at: new Date(Date.now() - 1000 * 60 * 5), // hace 5 min
  },
  {
    id: 2,
    event_type: 'exit',
    event_data: { description: 'Vehículo KLM456 salió del parqueadero' },
    created_at: new Date(Date.now() - 1000 * 60 * 30),
  },
  {
    id: 3,
    event_type: 'voice_command',
    event_data: { description: 'Comando de voz ejecutado: “Mostrar ocupación nivel 2”' },
    created_at: new Date(Date.now() - 1000 * 60 * 60),
  },
];

export default function HomePage() {
  const [parkingSpaces, setParkingSpaces] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simula carga inicial
    const timer = setTimeout(() => {
      setParkingSpaces(mockParkingSpaces);
      setVehicles(mockVehicles);
      setEvents(mockEvents);
      setLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  const stats = {
    totalSpaces: parkingSpaces.length,
    occupiedSpaces: parkingSpaces.filter(s => s.is_occupied).length,
    availableSpaces: parkingSpaces.filter(s => !s.is_occupied).length,
    activeVehicles: vehicles.length,
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Cargando Nuvora...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Tarjetas de estadísticas principales */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard title="Total de Cupos" value={stats.totalSpaces} icon={ParkingCircle} subtitle="Capacidad total" />
        <StatCard title="Cupos Ocupados" value={stats.occupiedSpaces} icon={Car} subtitle={`${Math.round((stats.occupiedSpaces / stats.totalSpaces) * 100)}% ocupación`} />
        <StatCard title="Cupos Disponibles" value={stats.availableSpaces} icon={ParkingCircle} subtitle="Listos para usar" />
        <StatCard title="Vehículos Activos" value={stats.activeVehicles} icon={Clock} subtitle="En el parqueadero" />
      </div>

      {/* Estado de cupos y panel derecho */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2">
          <ParkingSpaceGrid spaces={parkingSpaces} />
        </div>
        <div className="flex flex-col space-y-6">
          <RecentActivity events={events} />
          <VoiceControlPanel lastCommand={events.find(e => e.event_type === 'voice_command')?.event_data?.description ?? ''} />
        </div>
      </div>

      {/* Lista de vehículos activos */}
      <VehicleList vehicles={vehicles} />
    </div>
  );
}
