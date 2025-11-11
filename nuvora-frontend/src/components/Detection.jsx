import { Camera } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function Detection({ lastDetection, recentDetections = [] }) {
  const streamUrl = "http://localhost:8001/cameras/entrada/stream";
  const [currentTime, setCurrentTime] = useState('');

  useEffect(() => {
    // Actualizar el tiempo actual cada segundo
    const interval = setInterval(() => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString('es-CO', { hour12: false }));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // Formatear hora de detección
  const formatDetectionTime = (timestamp) => {
    if (!timestamp) return '--:--:--';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('es-CO', { hour12: false });
  };
  
  return (
    <div className="bg-white rounded-xl shadow p-8 border border-gray-100 w-full h-full flex flex-col">
      {/* Cabecera */}
      <div className="flex items-center mb-6">
        <div className="bg-emerald-100 rounded-full p-2 mr-3">
          <Camera className="w-6 h-6 text-emerald-600" />
        </div>
        <h2 className="text-xl font-bold text-gray-900">Detección en Vivo</h2>
        {lastDetection && (
          <div className="ml-auto">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
              Activo
            </span>
          </div>
        )}
      </div>
      {/* Contenido mayor video, menor info */}
      <div className="flex flex-col md:flex-row gap-8">
        {/* Video más grande - Stream en vivo */}
        <div className="flex-[2] min-w-[240px] flex items-center justify-center">
          <img 
            src={streamUrl} 
            alt="Stream de cámara en vivo"
            className="rounded-lg w-full h-[330px] md:h-[360px] object-cover bg-slate-200"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
          {/* Fallback si el stream no está disponible */}
          <div 
            className="hidden items-center justify-center bg-slate-200 rounded-lg w-full aspect-video h-[330px] md:h-[360px]"
          >
            <div className="text-center">
              <Camera className="w-12 h-12 text-gray-400 mx-auto mb-2" />
              <span className="text-lg font-semibold text-gray-400">Cámara no disponible</span>
              <p className="text-sm text-gray-400 mt-1">Verifica que el stream esté activo</p>
            </div>
          </div>
        </div>
        {/* Detalle, info más pequeña */}
        <div className="flex-[1] max-w-xs flex flex-col justify-center">
          <h3 className="text-base font-semibold mb-2 text-gray-900">Última placa detectada</h3>
          <div className="px-4 py-3 rounded-lg bg-gradient-to-br from-blue-50 to-blue-100 flex flex-col items-start mb-4 border border-blue-200">
            {lastDetection ? (
              <>
                <span className="font-mono text-2xl tracking-widest text-blue-700 font-bold">
                  {lastDetection.placa}
                </span>
                <span className="text-xs text-blue-600 mt-1">
                  Detectada a las {formatDetectionTime(lastDetection.timestamp)}
                </span>
              </>
            ) : (
              <>
                <span className="font-mono text-xl tracking-widest text-gray-400">
                  ---
                </span>
                <span className="text-xs text-gray-500 mt-1">
                  Esperando detección...
                </span>
              </>
            )}
          </div>
          
          <h4 className="text-sm font-semibold mb-2 text-gray-800">Placas recientes</h4>
          <ul className="text-xs text-gray-700 space-y-2">
            {recentDetections.length > 0 ? (
              recentDetections.slice(0, 3).map((detection, index) => (
                <li key={index} className="flex justify-between items-center bg-gray-50 px-3 py-2 rounded-md">
                  <span className="font-mono font-semibold">{detection.placa}</span>
                  <span className="text-gray-500">{formatDetectionTime(detection.timestamp)}</span>
                </li>
              ))
            ) : (
              <li className="text-gray-400 italic">No hay detecciones recientes</li>
            )}
          </ul>
          
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="text-xs text-gray-500">
              <p>Hora actual: <span className="font-mono font-semibold text-gray-700">{currentTime}</span></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
