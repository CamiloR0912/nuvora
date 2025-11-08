import sounddevice as sd
import soundfile as sf
import numpy as np
import requests
import sys

SAMPLE_RATE = 16000  # Whisper prefiere 16kHz
DURATION = 5  # segundos

def record_audio(filename="test_audio.wav", duration=DURATION):
    """Graba audio desde el micrófono"""
    print(f"🎤 Grabando {duration} segundos... Habla ahora!")
    
    audio = sd.rec(int(duration * SAMPLE_RATE), 
                   samplerate=SAMPLE_RATE, 
                   channels=1, 
                   dtype=np.float32)
    sd.wait()
    
    print("✅ Grabación completada")
    
    # Guardar archivo
    sf.write(filename, audio, SAMPLE_RATE)
    print(f"💾 Audio guardado en: {filename}")
    
    return filename

def test_transcribe(audio_file):
    """Prueba el endpoint de transcripción"""
    print(f"\n📤 Enviando audio a /transcribe...")
    
    with open(audio_file, 'rb') as f:
        files = {'file': (audio_file, f, 'audio/wav')}
        response = requests.post('http://localhost:8003/transcribe', files=files)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Transcripción: {data['text']}")
        return data['text']
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None

def test_voice_command(audio_file):
    """Prueba el endpoint completo de comando de voz"""
    print(f"\n📤 Enviando audio a /voice-command...")
    
    with open(audio_file, 'rb') as f:
        files = {'file': (audio_file, f, 'audio/wav')}
        response = requests.post('http://localhost:8003/voice-command', files=files)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Resultado completo:")
        print(f"   Pregunta: {data['query']}")
        print(f"   Intención: {data['intent']}")
        print(f"   Respuesta: {data['response']}")
        return data
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    print("=== Prueba de Voice Command Service ===\n")
    
    # Opción 1: Grabar nuevo audio
    if len(sys.argv) > 1 and sys.argv[1] == "record":
        audio_file = record_audio()
    # Opción 2: Usar archivo existente
    elif len(sys.argv) > 1:
        audio_file = sys.argv[1]
    else:
        print("Uso:")
        print("  python test_audio.py record          # Grabar nuevo audio")
        print("  python test_audio.py archivo.wav     # Usar archivo existente")
        sys.exit(1)
    
    # Probar transcripción simple
    test_transcribe(audio_file)
    
    # Probar comando completo
    test_voice_command(audio_file)