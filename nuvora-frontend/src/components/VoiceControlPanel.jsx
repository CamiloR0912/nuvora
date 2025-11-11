import { useState, useRef } from "react";
import { Mic } from "lucide-react";

export function VoiceControlPanel({ onCommandResponse }) {
  const [recording, setRecording] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [response, setResponse] = useState("");
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState("");
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // 🎤 Maneja grabación de audio y envío al backend
  async function toggleMicrophone() {
    try {
      if (!recording) {
        // Limpiar estados previos
        setError("");
        setTranscript("");
        setResponse("");
        audioChunksRef.current = [];

        // Solicitar acceso al micrófono
        const stream = await navigator.mediaDevices.getUserMedia({ 
          audio: true,
          video: false 
        });

        // Configurar MediaRecorder
        const mediaRecorder = new MediaRecorder(stream, {
          mimeType: 'audio/webm;codecs=opus'
        });
        mediaRecorderRef.current = mediaRecorder;

        // Capturar chunks de audio
        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };

        // Cuando se detiene la grabación, enviar al backend
        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          await sendAudioToBackend(audioBlob);
          
          // Detener el stream del micrófono
          stream.getTracks().forEach(track => track.stop());
        };

        // Iniciar grabación
        mediaRecorder.start();
        setRecording(true);
        console.log("🎤 Grabación iniciada");
      } else {
        // Detener grabación
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
          mediaRecorderRef.current.stop();
          setRecording(false);
          setProcessing(true);
          console.log("🛑 Grabación detenida, procesando...");
        }
      }
    } catch (error) {
      console.error("❌ Error:", error);
      setError(error.message || "Error al acceder al micrófono. Verifica los permisos del navegador.");
      setRecording(false);
    }
  }

  // 📤 Envía el audio al backend y procesa la respuesta
  async function sendAudioToBackend(audioBlob) {
    try {
      setProcessing(true);
      
      // Obtener JWT del localStorage
      const token = localStorage.getItem("token");
      if (!token) {
        throw new Error("No hay sesión activa. Por favor inicia sesión.");
      }

      // Preparar FormData con el audio
      const formData = new FormData();
      formData.append('file', audioBlob, 'recording.webm');

      console.log("📤 Enviando audio al backend...");

      // Enviar a tu voice_service
      const res = await fetch('http://localhost:8003/voice-command', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Error al procesar el audio');
      }

      const data = await res.json();
      console.log("✅ Respuesta del backend:", data);

      // Actualizar estados con la respuesta
      setTranscript(data.query || "");
      setResponse(data.response || "");
      
      // Notificar al componente padre si existe
      if (onCommandResponse) {
        onCommandResponse(data);
      }

    } catch (error) {
      console.error("❌ Error enviando audio:", error);
      setError(error.message || "Error al procesar el comando de voz");
    } finally {
      setProcessing(false);
    }
  }

  return (
    <div className="bg-white rounded-xl shadow p-6 mb-6">
      <h3 className="text-lg font-bold mb-4 text-gray-900">Control por Voz</h3>

      {/* Botón de micrófono */}
      <div className="flex flex-col items-center justify-center mb-4">
        <button
          className={`rounded-full p-6 transition ${
            recording
              ? "bg-red-200 hover:bg-red-300 animate-pulse"
              : processing
              ? "bg-yellow-100"
              : "bg-blue-100 hover:bg-blue-200"
          }`}
          onClick={toggleMicrophone}
          disabled={processing}
          aria-label={recording ? "Detener grabación" : "Iniciar grabación"}
        >
          <Mic className={`w-8 h-8 ${
            recording ? "text-red-600" : processing ? "text-yellow-600" : "text-blue-600"
          }`} />
        </button>
        <span className="text-sm text-gray-500 mt-2">
          {recording ? "Grabando audio..." : processing ? "Procesando..." : "Toca para hablar"}
        </span>
      </div>

      {/* Mensajes de error */}
      {error && (
        <div className="text-red-500 text-sm mb-3 flex items-center">
          <span className="mr-2">⚠️</span>
          {error}
        </div>
      )}

      {/* Transcripción */}
      {transcript && (
        <div className="mb-3 p-3 bg-blue-50 rounded-lg">
          <span className="block text-xs text-blue-600 font-semibold mb-1">Tu comando:</span>
          <span className="block text-gray-700 text-sm break-words">
            "{transcript}"
          </span>
        </div>
      )}

      {/* Respuesta del sistema */}
      {response && (
        <div className="mb-3 p-3 bg-green-50 rounded-lg">
          <span className="block text-xs text-green-600 font-semibold mb-1">Respuesta:</span>
          <span className="block text-gray-700 text-sm break-words">
            {response}
          </span>
        </div>
      )}

      <div>
        <span className="block font-semibold text-sm mb-1 text-slate-600">
          Comandos disponibles:
        </span>
        <ul className="list-disc pl-5 text-xs text-gray-500 space-y-1">
          <li>Buscar placa ABC-123</li>
          <li>¿Cuántos tickets tengo?</li>
          <li>Mostrar mis estadísticas</li>
          <li>¿Cuál fue la última detección?</li>
          <li>Listar usuarios del sistema</li>
        </ul>
      </div>
    </div>
  );
}
