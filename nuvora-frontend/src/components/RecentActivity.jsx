import { Activity, ArrowDownCircle, ArrowUpCircle, Mic } from 'lucide-react';

export function RecentActivity({ events }) {
  const getEventIcon = (eventType) => {
    switch (eventType) {
      case 'entry':
        return <ArrowDownCircle className="w-5 h-5 text-green-600" />;
      case 'exit':
        return <ArrowUpCircle className="w-5 h-5 text-blue-600" />;
      case 'voice_command':
        return <Mic className="w-5 h-5 text-purple-600" />;
      default:
        return <Activity className="w-5 h-5 text-gray-600" />;
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
      <h2 className="text-xl font-bold text-gray-900 mb-6">Actividad Reciente</h2>

      <div className="space-y-4">
        {events.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No hay actividad reciente</p>
        ) : (
          events.map((event) => (
            <div
              key={event.id}
              className="flex items-start space-x-3 pb-4 border-b border-gray-100 last:border-0"
            >
              <div className="mt-1">
                {getEventIcon(event.event_type)}
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">
                  {event.event_data.description || event.event_type}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {formatTime(event.created_at)}
                </p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
