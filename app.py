from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from instruments import (
    get_instrument, 
    close_all_instruments, 
    get_gpib_adapters, 
    list_connected_instruments, 
    test_instrument_connection,
    get_system_info
)
from auth import verify_token, get_permissions
import uvicorn
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GPIB API", description="API para control de instrumentos GPIB", version="2.0.0")

# CORS para pruebas desde navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_current_user(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Falta token")
    token = auth[7:]
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=403, detail="Token inválido")
    return token

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("client.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/system/info")
def get_system_information(token: str = Depends(get_current_user)):
    """Obtiene información del sistema GPIB"""
    try:
        return get_system_info()
    except Exception as e:
        logger.error(f"Error al obtener información del sistema: {e}")
        raise HTTPException(status_code=500, detail=f"Error del sistema: {str(e)}")

@app.get("/gpib/adapters")
def list_gpib_adapters(token: str = Depends(get_current_user)):
    """Lista todos los adaptadores GPIB disponibles"""
    try:
        return get_gpib_adapters()
    except Exception as e:
        logger.error(f"Error al listar adaptadores GPIB: {e}")
        raise HTTPException(status_code=500, detail=f"Error al buscar adaptadores: {str(e)}")

@app.get("/gpib/instruments")
def list_instruments(token: str = Depends(get_current_user)):
    """Lista todos los instrumentos conectados con sus direcciones"""
    try:
        return list_connected_instruments()
    except Exception as e:
        logger.error(f"Error al listar instrumentos: {e}")
        raise HTTPException(status_code=500, detail=f"Error al listar instrumentos: {str(e)}")

@app.get("/gpib/test/{address}")
def test_connection(address: str, token: str = Depends(get_current_user)):
    """Prueba la conexión con un instrumento específico"""
    try:
        return test_instrument_connection(address)
    except Exception as e:
        logger.error(f"Error al probar conexión con {address}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al probar conexión: {str(e)}")

@app.get("/gpib/read")
def read_gpib(address: str, token: str = Depends(get_current_user)):
    """Lee datos de un instrumento GPIB"""
    try:
        instr = get_instrument(address)
        response = instr.query("*IDN?")
        return {"success": True, "data": response, "address": address}
    except Exception as e:
        logger.error(f"Error al leer de {address}: {e}")
        raise HTTPException(status_code=500, detail=f"Error de lectura: {str(e)}")

@app.post("/gpib/write")
def write_gpib(address: str, command: str, token: str = Depends(get_current_user)):
    """Escribe comandos a un instrumento GPIB"""
    try:
        perms = get_permissions(token)
        if perms != "readwrite":
            raise HTTPException(status_code=403, detail="Solo lectura permitida")
        
        instr = get_instrument(address)
        instr.write(command)
        return {"success": True, "status": "ok", "address": address, "command": command}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al escribir a {address}: {e}")
        raise HTTPException(status_code=500, detail=f"Error de escritura: {str(e)}")

@app.post("/gpib/query")
def query_gpib(address: str, command: str, token: str = Depends(get_current_user)):
    """Ejecuta un comando SCPI y devuelve la respuesta"""
    try:
        instr = get_instrument(address)
        response = instr.query(command)
        return {"success": True, "data": response, "address": address, "command": command}
    except Exception as e:
        logger.error(f"Error al ejecutar query en {address}: {e}")
        raise HTTPException(status_code=500, detail=f"Error de query: {str(e)}")

@app.delete("/gpib/close/{address}")
def close_instrument(address: str, token: str = Depends(get_current_user)):
    """Cierra la conexión con un instrumento específico"""
    try:
        from instruments import open_instruments
        if address in open_instruments:
            open_instruments[address].close()
            del open_instruments[address]
            logger.info(f"Conexión cerrada con: {address}")
            return {"success": True, "message": f"Conexión cerrada con {address}"}
        else:
            return {"success": False, "message": f"No hay conexión abierta con {address}"}
    except Exception as e:
        logger.error(f"Error al cerrar conexión con {address}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al cerrar conexión: {str(e)}")

@app.delete("/gpib/close-all")
def close_all_connections(token: str = Depends(get_current_user)):
    """Cierra todas las conexiones de instrumentos"""
    try:
        close_all_instruments()
        return {"success": True, "message": "Todas las conexiones cerradas"}
    except Exception as e:
        logger.error(f"Error al cerrar todas las conexiones: {e}")
        raise HTTPException(status_code=500, detail=f"Error al cerrar conexiones: {str(e)}")

@app.on_event("shutdown")
def shutdown_event():
    close_all_instruments()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)