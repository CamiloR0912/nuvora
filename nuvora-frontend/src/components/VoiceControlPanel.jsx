import { Mic, CheckCircle2 } from 'lucide-react';

export function VoiceControlPanel({ lastCommand }) {
  return (
    <div className="bg-white rounded-xl shadow p-6 border border-gray-100 max-w-sm mx-auto">
      <div className="flex items-center mb-6">
        <div className="bg-emerald-50 p-2 rounded-full mr-3">
          <Mic className="w-5 h-5 text-emerald-600" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Control por Voz</h2>
          <p className="text-sm text-gray-500">Comandos de voz</p>
        </div>
      </div>

      <div className="flex flex-col items-center space-y-2 mb-6">
        <button
          type="button"
          className="bg-blue-600 hover:bg-blue-700 text-white rounded-full w-20 h-20 flex items-center justify-center shadow-lg transition"
        >
          <Mic className="w-8 h-8" />
        </button>
        <span className="text-gray-500 text-sm text-center">Toca para hablar</span>
      </div>

      <div className="bg-gray-50 rounded-lg p-3 mb-5">
        <div className="text-xs text-gray-500 mb-1">Último comando:</div>
        <div className="text-gray-800 font-medium">{lastCommand || '—'}</div>
      </div>

      <div>
        <p className="text-xs text-gray-700 font-medium mb-2">Comandos disponibles:</p>
        <ul className="text-sm text-gray-600 list-disc list-inside space-y-1">
          <li>¿Cuántos carros hay?</li>
          <li>Mostrar cupos disponibles</li>
          <li>Buscar placa ABC-123</li>
          <li>Estadísticas del día</li>
        </ul>
      </div>
    </div>
  );
}
