import { useEffect, useRef, useState } from 'react';

/**
 * Hook personalizado para conectarse a eventos Server-Sent Events (SSE)
 * Nota: EventSource no soporta headers personalizados, así que no podemos enviar el token JWT directamente.
 * Como alternativa, el backend debería permitir conexiones SSE sin autenticación o usar query params.
 * 
 * @param {string} url - URL del endpoint SSE
 * @param {function} onMessage - Callback cuando se recibe un mensaje
 * @param {string} token - Token JWT para autenticación (opcional, por ahora no se usa)
 */
export const useSSE = (url, onMessage, token) => {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const eventSourceRef = useRef(null);

  useEffect(() => {
    if (!url) {
      console.warn('⚠️ URL de SSE no proporcionada');
      return;
    }

    try {
      console.log('🔌 Conectando a SSE:', url);
      
      // Crear conexión EventSource
      // NOTA: EventSource no soporta headers, así que no podemos enviar el token JWT
      // El backend debe permitir acceso público a este endpoint o usar otra estrategia
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      // Manejar conexión exitosa
      eventSource.onopen = () => {
        console.log('✅ Conectado a eventos en tiempo real');
        setIsConnected(true);
        setError(null);
      };

      // Manejar mensajes entrantes
      eventSource.onmessage = (event) => {
        try {
          console.log('📨 Mensaje SSE recibido:', event.data);
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch (err) {
          console.error('❌ Error al parsear mensaje SSE:', err, 'Data:', event.data);
        }
      };

      // Manejar errores
      eventSource.onerror = (err) => {
        console.error('❌ Error en conexión SSE:', err);
        setIsConnected(false);
        setError('Error de conexión con eventos en tiempo real');
        
        // EventSource intenta reconectar automáticamente
        // pero si falla repetidamente, podemos cerrar
        if (eventSource.readyState === EventSource.CLOSED) {
          console.warn('🔌 Conexión SSE cerrada');
        }
      };

      // Cleanup al desmontar
      return () => {
        console.log('🔌 Cerrando conexión SSE');
        eventSource.close();
      };
    } catch (err) {
      console.error('❌ Error al crear EventSource:', err);
      setError(err.message);
    }
  }, [url, onMessage]);

  return { isConnected, error };
};
