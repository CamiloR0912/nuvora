import { useState, useRef } from "react";
import { Mic } from "lucide-react";

export function VoiceControlPanel({ lastCommand }) {
  const [recording, setRecording] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState("");
  const audioStreamRef = useRef(null);
  const recognitionRef = useRef(null);

  // 🔊 Maneja acceso al micrófono y reconocimiento de voz
  async function toggleMicrophone() {
    try {
      if (!recording) {
        // Verificar soporte del navegador para reconocimiento de voz
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
          throw new Error("Tu navegador no soporta reconocimiento de voz");
        }

        // Solicitar acceso al micrófono
        const stream = await navigator.mediaDevices.getUserMedia({ 
          audio: true,
          video: false 
        });
        audioStreamRef.current = stream;

        // Configurar reconocimiento de voz
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.lang = "es-ES";
        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;

        // Configurar eventos de reconocimiento
        recognitionRef.current.onresult = (event) => {
          const current = event.resultIndex;
          const result = event.results[current];
          const transcriptText = result[0].transcript;
          console.log("� Texto reconocido:", transcriptText);
          setTranscript(transcriptText);
        };

        recognitionRef.current.onerror = (event) => {
          console.error("❌ Error en reconocimiento:", event.error);
          setError("Error en reconocimiento de voz: " + event.error);
        };

        // Iniciar reconocimiento
        recognitionRef.current.start();
        setRecording(true);
        console.log("🎤 Reconocimiento de voz activado");
      } else {
        // Detener reconocimiento y grabación
        if (recognitionRef.current) {
          recognitionRef.current.stop();
        }
        if (audioStreamRef.current) {
          audioStreamRef.current.getTracks().forEach((track) => track.stop());
          audioStreamRef.current = null;
        }
        setRecording(false);
        console.log("🛑 Reconocimiento de voz desactivado");
      }
    } catch (error) {
      console.error("❌ Error:", error);
      setError(error.message || "Error al acceder al micrófono. Verifica los permisos del navegador.");
      alert(error.message || "Error al acceder al micrófono. Verifica los permisos del navegador.");
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
              : "bg-blue-100 hover:bg-blue-200"
          }`}
          onClick={toggleMicrophone}
          aria-label={recording ? "Detener grabación" : "Iniciar grabación"}
        >
          <Mic className={`w-8 h-8 ${recording ? "text-red-600" : "text-blue-600"}`} />
        </button>
        <span className="text-sm text-gray-500 mt-2">
          {recording ? "Grabando audio..." : "Toca para hablar"}
        </span>
      </div>

      {/* Mensajes de error */}
      {error && (
        <div className="text-red-500 text-sm mb-3 flex items-center">
          <span className="mr-2">⚠️</span>
          {error}
        </div>
      )}

      {/* Texto temporal y comandos */}
      <div className="mb-3">
        <span className="block text-xs text-gray-400">Último comando:</span>
        <span className="block font-medium text-gray-700 text-sm min-h-[20px] break-words">
          {transcript || lastCommand || "—"}
        </span>
      </div>

      <div>
        <span className="block font-semibold text-sm mb-1 text-slate-600">
          Comandos disponibles:
        </span>
        <ul className="list-disc pl-5 text-xs text-gray-500 space-y-1">
          <li>¿Cuántos carros hay?</li>
          <li>Mostrar cupos disponibles</li>
          <li>Buscar placa ABC-123</li>
          <li>Estadísticas del día</li>
        </ul>
      </div>
    </div>
  );
}
