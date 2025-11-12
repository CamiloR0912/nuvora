"""
Prueba del Voice Command Service CON autenticación JWT
"""
import requests
import sys

# Configuración
VOICE_SERVICE_URL = "http://localhost:8003"
BACKEND_URL = "http://localhost:8000"

def login_and_get_token(username: str, password: str) -> str:
    """Hace login en el backend y obtiene el JWT token"""
    print(f"🔐 Iniciando sesión como: {username}")
    
    response = requests.post(
        f"{BACKEND_URL}/users/login",
        data={
            "username": username,
            "password": password
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ Login exitoso, token obtenido")
        return token
    else:
        print(f"❌ Error en login: {response.status_code} - {response.text}")
        return None

def test_voice_command_with_auth(audio_file: str, token: str):
    """Prueba el endpoint de comando de voz CON autenticación"""
    print(f"\n📤 Enviando audio con JWT a /voice-command...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    with open(audio_file, 'rb') as f:
        files = {'file': (audio_file, f, 'audio/wav')}
        response = requests.post(
            f"{VOICE_SERVICE_URL}/voice-command",
            files=files,
            headers=headers
        )
    
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

def test_voice_command_without_auth(audio_file: str):
    """Prueba el endpoint de comando de voz SIN autenticación (debe fallar con 422)"""
    print(f"\n📤 Enviando audio SIN JWT a /voice-command...")
    
    with open(audio_file, 'rb') as f:
        files = {'file': (audio_file, f, 'audio/wav')}
        response = requests.post(f"{VOICE_SERVICE_URL}/voice-command", files=files)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n⚠️  ADVERTENCIA: La petición sin JWT fue exitosa (no debería)")
        print(f"   Pregunta: {data['query']}")
        print(f"   Intención: {data['intent']}")
        print(f"   Respuesta: {data['response']}")
        return data
    else:
        print(f"✅ Correctamente rechazado con error {response.status_code}")
        try:
            error_detail = response.json().get('detail', response.text)
            print(f"   Motivo: Campo Authorization requerido")
        except:
            print(f"   Respuesta: {response.text}")
        return None

if __name__ == "__main__":
    print("=== Prueba de Voice Command Service con JWT ===\n")
    
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python test_audio_with_jwt.py archivo.wav")
        print("  python test_audio_with_jwt.py archivo.wav admin admin123")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    
    # Obtener credenciales
    if len(sys.argv) >= 4:
        username = sys.argv[2]
        password = sys.argv[3]
    else:
        username = "cam"
        password = "000"
    
    # Hacer login
    token = login_and_get_token(username, password)
    
    if not token:
        print("\n⚠️ No se pudo obtener el token, probando sin autenticación...")
        test_voice_command_without_auth(audio_file)
    else:
        # Probar CON autenticación
        print("\n" + "="*60)
        print("TEST 1: Con autenticación JWT")
        print("="*60)
        test_voice_command_with_auth(audio_file, token)
        
        # Probar SIN autenticación (para comparar)
        print("\n" + "="*60)
        print("TEST 2: Sin autenticación JWT")
        print("="*60)
        test_voice_command_without_auth(audio_file)
