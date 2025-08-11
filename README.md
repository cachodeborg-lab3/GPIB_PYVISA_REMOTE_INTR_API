# 🎛️ GPIB Python API v2.0

API REST completa para control de instrumentos GPIB/SCPI con detección automática, gestión de conexiones, control de errores avanzado y **URL configurable**.

## ✨ Características Principales

### 🔍 **Detección Automática**
- **Identificación de adaptadores GPIB** disponibles
- **Listado de instrumentos conectados** con información detallada
- **Prueba de conexión** individual por instrumento
- **Información del sistema** GPIB completo

### 🔐 **Sistema de Autenticación**
- Autenticación por tokens Bearer
- Control de permisos (solo lectura vs lectura/escritura)
- Gestión de usuarios configurable

### 📡 **Comunicación SCPI**
- **Lectura** de instrumentos (`*IDN?`, etc.)
- **Escritura** de comandos SCPI
- **Query** (comando + respuesta)
- Timeouts configurables

### 🔧 **Gestión de Conexiones**
- **Apertura automática** de conexiones
- **Cierre individual** de instrumentos
- **Cierre masivo** de todas las conexiones
- **Pool de conexiones** reutilizables

### 🛡️ **Control de Errores**
- Logging detallado de operaciones
- Manejo de timeouts
- Respuestas de error estructuradas
- Validación de parámetros

### ⚙️ **URL Configurable**
- **URL del servidor configurable** desde el cliente web
- **Valor por defecto**: `http://localhost:8000`
- **Prueba de conexión** automática
- **Flexibilidad** para diferentes entornos

## 🚀 Instalación

### Requisitos
- Python 3.7+
- Adaptador GPIB (físico o virtual)
- PyVISA y drivers correspondientes

### Instalación de Dependencias
```bash
pip install -r requirements.txt
```

### Configuración
1. Editar `config.json` para configurar usuarios y tokens
2. Verificar que PyVISA detecte tu adaptador GPIB
3. Ejecutar el servidor

## 🏃‍♂️ Uso

### Iniciar Servidor
```bash
# Opción 1: Directo
python app.py

# Opción 2: Con uvicorn (recomendado)
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Acceder al Cliente Web
1. **Abrir navegador** en: `http://localhost:8000`
2. **Configurar URL del servidor** (por defecto: `http://localhost:8000`)
3. **Probar conexión** con el botón "Probar Conexión al Servidor"
4. **Ingresar token**: `abc123` (admin) o `xyz789` (usuario)

### Tokens de Acceso
```json
{
  "admin": {
    "token": "abc123",
    "permissions": "readwrite"
  },
  "user": {
    "token": "xyz789", 
    "permissions": "readonly"
  }
}
```

## 📋 Endpoints de la API

### 🔍 **Detección y Diagnóstico**

#### `GET /system/info`
Obtiene información del sistema GPIB

**Ejemplo de uso:**
```bash
curl -H "Authorization: Bearer abc123" \
     http://localhost:8000/system/info
```

**Respuesta:**
```json
{
  "success": true,
  "backend": "Resource Manager of Visa Library at py",
  "version": "PyVISA",
  "available_resources": ["GPIB0::5::INSTR", "GPIB0::6::INSTR"],
  "open_connections": 2,
  "open_addresses": ["GPIB0::5::INSTR", "GPIB0::6::INSTR"]
}
```

#### `GET /gpib/adapters`
Lista adaptadores GPIB disponibles

**Ejemplo de uso:**
```bash
curl -H "Authorization: Bearer abc123" \
     http://localhost:8000/gpib/adapters
```

**Respuesta:**
```json
{
  "success": true,
  "adapters": [
    {
      "address": "GPIB0::5::INSTR",
      "type": "GPIB",
      "status": "available",
      "instrument_info": "KEITHLEY INSTRUMENTS INC.,MODEL 2000,123456,01.01.01",
      "instrument_type": "MODEL 2000"
    }
  ],
  "total_found": 1
}
```

#### `GET /gpib/instruments`
Lista instrumentos conectados con detalles

**Ejemplo de uso:**
```bash
curl -H "Authorization: Bearer abc123" \
     http://localhost:8000/gpib/instruments
```

**Respuesta:**
```json
{
  "success": true,
  "instruments": [
    {
      "address": "GPIB0::5::INSTR",
      "manufacturer": "KEITHLEY INSTRUMENTS INC.",
      "model": "MODEL 2000",
      "serial": "123456",
      "version": "01.01.01",
      "status": "connected",
      "full_idn": "KEITHLEY INSTRUMENTS INC.,MODEL 2000,123456,01.01.01"
    }
  ],
  "total_connected": 1
}
```

#### `GET /gpib/test/{address}`
Prueba conexión con instrumento específico

**Ejemplo de uso:**
```bash
curl -H "Authorization: Bearer abc123" \
     http://localhost:8000/gpib/test/GPIB0::5::INSTR
```

**Respuesta:**
```json
{
  "success": true,
  "address": "GPIB0::5::INSTR",
  "response": "KEITHLEY INSTRUMENTS INC.,MODEL 2000,123456,01.01.01",
  "status": "connected"
}
```

### 📡 **Comunicación SCPI**

#### `GET /gpib/read`
Lee identificación del instrumento

**Ejemplo de uso:**
```bash
curl -H "Authorization: Bearer abc123" \
     "http://localhost:8000/gpib/read?address=GPIB0::5::INSTR"
```

**Respuesta:**
```json
{
  "success": true,
  "data": "KEITHLEY INSTRUMENTS INC.,MODEL 2000,123456,01.01.01",
  "address": "GPIB0::5::INSTR"
}
```

#### `POST /gpib/write`
Envía comando SCPI (solo admin)

**Ejemplo de uso:**
```bash
curl -X POST \
     -H "Authorization: Bearer abc123" \
     "http://localhost:8000/gpib/write?address=GPIB0::5::INSTR&command=*RST"
```

**Respuesta:**
```json
{
  "success": true,
  "status": "ok",
  "address": "GPIB0::5::INSTR",
  "command": "*RST"
}
```

#### `POST /gpib/query`
Ejecuta comando y obtiene respuesta

**Ejemplo de uso:**
```bash
curl -X POST \
     -H "Authorization: Bearer abc123" \
     "http://localhost:8000/gpib/query?address=GPIB0::5::INSTR&command=MEAS:VOLT:DC?"
```

**Respuesta:**
```json
{
  "success": true,
  "data": "1.2345E+00",
  "address": "GPIB0::5::INSTR",
  "command": "MEAS:VOLT:DC?"
}
```

### 🔧 **Gestión de Conexiones**

#### `DELETE /gpib/close/{address}`
Cierra conexión específica

**Ejemplo de uso:**
```bash
curl -X DELETE \
     -H "Authorization: Bearer abc123" \
     http://localhost:8000/gpib/close/GPIB0::5::INSTR
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Conexión cerrada con GPIB0::5::INSTR"
}
```

#### `DELETE /gpib/close-all`
Cierra todas las conexiones

**Ejemplo de uso:**
```bash
curl -X DELETE \
     -H "Authorization: Bearer abc123" \
     http://localhost:8000/gpib/close-all
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Todas las conexiones cerradas"
}
```

## 🎨 Cliente Web

### ⚙️ **Configuración del Servidor**
- **Campo de URL**: Configurable al inicio de la página
- **Valor por defecto**: `http://localhost:8000`
- **Prueba de conexión**: Botón para verificar conectividad
- **Estados visuales**: Indicadores de éxito/error

### 📊 **Panel de Control**
- **Información del Sistema**: Estado del backend GPIB
- **Detección de Adaptadores**: Búsqueda automática
- **Listado de Instrumentos**: Con información detallada
- **Prueba de Conexión**: Verificación individual

### 📡 **Comunicación SCPI**
- **Lectura**: Comando `*IDN?` automático
- **Escritura**: Envío de comandos SCPI
- **Query**: Comando + respuesta
- **Resultados formateados**: JSON legible

### 🔧 **Gestión Avanzada**
- **Cierre individual**: Por dirección GPIB
- **Cierre masivo**: Todas las conexiones
- **Estados visuales**: Indicadores de éxito/error
- **Logs en tiempo real**: Feedback inmediato

## 🛠️ Configuración Avanzada

### Timeouts
Los timeouts están configurados en `instruments.py`:
- **Conexión**: 10 segundos
- **Prueba**: 5 segundos
- **Query**: 10 segundos

### Logging
El sistema incluye logging detallado:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### CORS
Configurado para desarrollo:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🔍 Diagnóstico de Problemas

### Error: "No se encontraron adaptadores GPIB"
1. Verificar instalación de PyVISA
2. Comprobar drivers del adaptador
3. Ejecutar `python -c "import pyvisa; rm = pyvisa.ResourceManager(); print(rm.list_resources())"`

### Error: "Timeout en comunicación"
1. Verificar conexión física
2. Comprobar dirección GPIB
3. Ajustar timeouts en `instruments.py`

### Error: "Token inválido"
1. Verificar token en `config.json`
2. Usar formato correcto: `Bearer <token>`
3. Comprobar permisos del usuario

### Error: "Failed to fetch"
1. Verificar que el servidor esté ejecutándose
2. Comprobar URL del servidor en el cliente
3. Probar conexión con el botón "Probar Conexión al Servidor"

## 📝 Ejemplos de Uso

### Python Client
```python
import requests

# Configurar
BASE_URL = "http://localhost:8000"
TOKEN = "abc123"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Obtener información del sistema
response = requests.get(f"{BASE_URL}/system/info", headers=HEADERS)
print(response.json())

# Listar instrumentos
response = requests.get(f"{BASE_URL}/gpib/instruments", headers=HEADERS)
instruments = response.json()
print(f"Encontrados {instruments['total_connected']} instrumentos")

# Leer instrumento
response = requests.get(
    f"{BASE_URL}/gpib/read?address=GPIB0::5::INSTR", 
    headers=HEADERS
)
print(response.json()['data'])

# Enviar comando
response = requests.post(
    f"{BASE_URL}/gpib/write?address=GPIB0::5::INSTR&command=*RST",
    headers=HEADERS
)
print(response.json())

# Ejecutar query
response = requests.post(
    f"{BASE_URL}/gpib/query?address=GPIB0::5::INSTR&command=MEAS:VOLT:DC?",
    headers=HEADERS
)
print(response.json()['data'])
```

### cURL
```bash
# Obtener información del sistema
curl -H "Authorization: Bearer abc123" \
     http://localhost:8000/system/info

# Listar adaptadores
curl -H "Authorization: Bearer abc123" \
     http://localhost:8000/gpib/adapters

# Probar conexión
curl -H "Authorization: Bearer abc123" \
     http://localhost:8000/gpib/test/GPIB0::5::INSTR

# Leer instrumento
curl -H "Authorization: Bearer abc123" \
     "http://localhost:8000/gpib/read?address=GPIB0::5::INSTR"

# Enviar comando
curl -X POST \
     -H "Authorization: Bearer abc123" \
     "http://localhost:8000/gpib/write?address=GPIB0::5::INSTR&command=*RST"

# Ejecutar query
curl -X POST \
     -H "Authorization: Bearer abc123" \
     "http://localhost:8000/gpib/query?address=GPIB0::5::INSTR&command=MEAS:VOLT:DC?"
```

### JavaScript/Fetch
```javascript
// Configuración
const BASE_URL = 'http://localhost:8000';
const TOKEN = 'abc123';
const HEADERS = {
    'Authorization': `Bearer ${TOKEN}`,
    'Content-Type': 'application/json'
};

// Obtener información del sistema
async function getSystemInfo() {
    const response = await fetch(`${BASE_URL}/system/info`, { headers: HEADERS });
    const data = await response.json();
    console.log(data);
}

// Listar instrumentos
async function listInstruments() {
    const response = await fetch(`${BASE_URL}/gpib/instruments`, { headers: HEADERS });
    const data = await response.json();
    console.log(`Encontrados ${data.total_connected} instrumentos`);
}

// Leer instrumento
async function readInstrument(address) {
    const response = await fetch(`${BASE_URL}/gpib/read?address=${address}`, { headers: HEADERS });
    const data = await response.json();
    console.log(data.data);
}

// Enviar comando
async function sendCommand(address, command) {
    const response = await fetch(`${BASE_URL}/gpib/write?address=${address}&command=${command}`, {
        method: 'POST',
        headers: HEADERS
    });
    const data = await response.json();
    console.log(data);
}
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

Para soporte técnico o preguntas:
- Crear un issue en GitHub
- Revisar la documentación en `/docs`
- Verificar logs del servidor

---

**Desarrollado para Certificaciones de Física 2023** 🧪⚡ 