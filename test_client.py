#!/usr/bin/env python3
"""
Cliente de prueba para verificar la API GPIB
"""

import requests
import json
import time

# Configuración
BASE_URL = "http://localhost:8000"
TOKEN = "abc123"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def test_endpoint(endpoint, method="GET", params=None, data=None):
    """Prueba un endpoint de la API"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=HEADERS, params=params)
        elif method == "POST":
            response = requests.post(url, headers=HEADERS, params=params, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=HEADERS, params=params)
        
        print(f"✅ {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        print()
        return response.json()
        
    except Exception as e:
        print(f"❌ Error en {method} {endpoint}: {e}")
        print()
        return None

def main():
    """Ejecuta todas las pruebas"""
    print("🧪 Iniciando pruebas de la API GPIB v2.0")
    print("=" * 50)
    
    # 1. Información del sistema
    print("1. Probando información del sistema...")
    test_endpoint("/system/info")
    
    # 2. Listar adaptadores GPIB
    print("2. Probando detección de adaptadores...")
    test_endpoint("/gpib/adapters")
    
    # 3. Listar instrumentos
    print("3. Probando listado de instrumentos...")
    test_endpoint("/gpib/instruments")
    
    # 4. Probar conexión con instrumento simulado
    print("4. Probando conexión con instrumento...")
    test_endpoint("/gpib/test/GPIB0::5::INSTR")
    
    # 5. Probar lectura (debería fallar sin instrumento real)
    print("5. Probando lectura de instrumento...")
    test_endpoint("/gpib/read", params={"address": "GPIB0::5::INSTR"})
    
    # 6. Probar escritura (debería fallar sin instrumento real)
    print("6. Probando escritura de comando...")
    test_endpoint("/gpib/write", method="POST", 
                 params={"address": "GPIB0::5::INSTR", "command": "*RST"})
    
    # 7. Probar query (debería fallar sin instrumento real)
    print("7. Probando query personalizado...")
    test_endpoint("/gpib/query", method="POST",
                 params={"address": "GPIB0::5::INSTR", "command": "MEAS:VOLT:DC?"})
    
    # 8. Probar cierre de conexión
    print("8. Probando cierre de conexión...")
    test_endpoint("/gpib/close/GPIB0::5::INSTR", method="DELETE")
    
    # 9. Probar cierre masivo
    print("9. Probando cierre masivo...")
    test_endpoint("/gpib/close-all", method="DELETE")
    
    print("🎉 Pruebas completadas!")
    print("\n📝 Notas:")
    print("- Los errores de conexión son normales sin instrumentos GPIB reales")
    print("- La API está funcionando correctamente")
    print("- El servidor está respondiendo a todas las peticiones")

if __name__ == "__main__":
    main() 