"""
Test de autenticación service-to-service con API Key
Verifica que el Voice Service puede autenticarse con el Backend
"""
import requests
import os
import sys

# Configuración
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
SERVICE_API_KEY = os.getenv("SERVICE_API_KEY", "nuvora-service-key-2024-change-in-prod")

def test_con_api_key():
    """Test con API Key válida - debe funcionar"""
    print("\n✅ Test 1: Autenticación con API Key válida")
    
    headers = {
        "X-API-Key": SERVICE_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BACKEND_URL}/vehiculos/activos", headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Exitoso: {len(data)} vehículos activos")
            return True
        else:
            print(f"   ✗ Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"   ✗ Excepción: {e}")
        return False

def test_sin_autenticacion():
    """Test sin autenticación - debe fallar con 401"""
    print("\n❌ Test 2: Sin autenticación (debe fallar)")
    
    try:
        response = requests.get(f"{BACKEND_URL}/vehiculos/activos", timeout=5)
        
        if response.status_code == 401:
            print(f"   ✓ Correctamente rechazado (401)")
            return True
        else:
            print(f"   ✗ Esperaba 401, recibió: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Excepción: {e}")
        return False

def test_api_key_invalida():
    """Test con API Key incorrecta - debe fallar con 401"""
    print("\n❌ Test 3: API Key incorrecta (debe fallar)")
    
    headers = {
        "X-API-Key": "clave-incorrecta-123",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BACKEND_URL}/vehiculos/activos", headers=headers, timeout=5)
        
        if response.status_code == 401:
            print(f"   ✓ Correctamente rechazado (401)")
            return True
        else:
            print(f"   ✗ Esperaba 401, recibió: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Excepción: {e}")
        return False

def test_historial():
    """Test de endpoint de historial"""
    print("\n✅ Test 4: Obtener historial con API Key")
    
    headers = {
        "X-API-Key": SERVICE_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BACKEND_URL}/vehiculos/historial", headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Exitoso: {len(data)} vehículos en historial")
            return True
        else:
            print(f"   ✗ Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"   ✗ Excepción: {e}")
        return False

def test_eventos_vehiculos():
    """Test de endpoint de eventos de vehículos"""
    print("\n✅ Test 5: Obtener conteo de eventos")
    
    headers = {
        "X-API-Key": SERVICE_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BACKEND_URL}/vehicle-events/count", headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Exitoso: {data.get('count', 0)} eventos detectados")
            return True
        elif response.status_code == 404:
            print(f"   ℹ️  Endpoint no encontrado (normal si no está implementado)")
            return True
        else:
            print(f"   ✗ Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"   ✗ Excepción: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔐 TEST DE AUTENTICACIÓN SERVICE-TO-SERVICE")
    print("=" * 60)
    print(f"\n📍 Backend URL: {BACKEND_URL}")
    print(f"🔑 Service API Key: {SERVICE_API_KEY[:20]}...")
    
    # Ejecutar tests
    resultados = []
    resultados.append(test_con_api_key())
    resultados.append(test_sin_autenticacion())
    resultados.append(test_api_key_invalida())
    resultados.append(test_historial())
    resultados.append(test_eventos_vehiculos())
    
    # Resumen
    print("\n" + "=" * 60)
    exitosos = sum(resultados)
    total = len(resultados)
    print(f"📊 RESUMEN: {exitosos}/{total} tests exitosos")
    
    if exitosos == total:
        print("✅ Todos los tests pasaron correctamente")
        sys.exit(0)
    else:
        print("❌ Algunos tests fallaron")
        sys.exit(1)
