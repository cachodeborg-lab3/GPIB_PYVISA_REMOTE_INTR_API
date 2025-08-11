import pyvisa
import logging

# Configurar logging para mejor control de errores
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

rm = pyvisa.ResourceManager()
open_instruments = {}

def get_gpib_adapters():
    """Identifica todos los adaptadores GPIB disponibles"""
    try:
        adapters = []
        # Buscar recursos GPIB
        resources = rm.list_resources('?*')
        
        for resource in resources:
            if 'GPIB' in resource:
                try:
                    # Intentar abrir el recurso para verificar que esté disponible
                    instr = rm.open_resource(resource)
                    adapter_info = {
                        'address': resource,
                        'type': 'GPIB',
                        'status': 'available'
                    }
                    
                    # Intentar obtener información del instrumento
                    try:
                        idn = instr.query('*IDN?').strip()
                        adapter_info['instrument_info'] = idn
                        adapter_info['instrument_type'] = idn.split(',')[1].strip() if ',' in idn else 'Unknown'
                    except Exception as e:
                        adapter_info['instrument_info'] = 'No response'
                        adapter_info['instrument_type'] = 'Unknown'
                        logger.warning(f"No se pudo obtener información del instrumento en {resource}: {e}")
                    
                    instr.close()
                    adapters.append(adapter_info)
                    
                except Exception as e:
                    logger.error(f"Error al acceder al recurso {resource}: {e}")
                    adapters.append({
                        'address': resource,
                        'type': 'GPIB',
                        'status': 'error',
                        'error': str(e)
                    })
        
        return {
            'success': True,
            'adapters': adapters,
            'total_found': len(adapters)
        }
        
    except Exception as e:
        logger.error(f"Error al buscar adaptadores GPIB: {e}")
        return {
            'success': False,
            'error': str(e),
            'adapters': [],
            'total_found': 0
        }

def list_connected_instruments():
    """Lista todos los instrumentos conectados con sus direcciones"""
    try:
        instruments = []
        resources = rm.list_resources()
        
        for resource in resources:
            if 'GPIB' in resource:
                try:
                    instr = rm.open_resource(resource)
                    
                    # Intentar obtener identificación del instrumento
                    try:
                        idn = instr.query('*IDN?').strip()
                        manufacturer, model, serial, version = idn.split(',') if ',' in idn else (idn, 'Unknown', 'Unknown', 'Unknown')
                        
                        instrument_info = {
                            'address': resource,
                            'manufacturer': manufacturer.strip(),
                            'model': model.strip(),
                            'serial': serial.strip(),
                            'version': version.strip(),
                            'status': 'connected',
                            'full_idn': idn
                        }
                    except Exception as e:
                        instrument_info = {
                            'address': resource,
                            'manufacturer': 'Unknown',
                            'model': 'Unknown',
                            'serial': 'Unknown',
                            'version': 'Unknown',
                            'status': 'connected_no_response',
                            'error': str(e)
                        }
                    
                    instr.close()
                    instruments.append(instrument_info)
                    
                except Exception as e:
                    logger.error(f"Error al acceder al instrumento {resource}: {e}")
                    instruments.append({
                        'address': resource,
                        'manufacturer': 'Unknown',
                        'model': 'Unknown',
                        'serial': 'Unknown',
                        'version': 'Unknown',
                        'status': 'error',
                        'error': str(e)
                    })
        
        return {
            'success': True,
            'instruments': instruments,
            'total_connected': len(instruments)
        }
        
    except Exception as e:
        logger.error(f"Error al listar instrumentos: {e}")
        return {
            'success': False,
            'error': str(e),
            'instruments': [],
            'total_connected': 0
        }

def test_instrument_connection(address):
    """Prueba la conexión con un instrumento específico"""
    try:
        instr = rm.open_resource(address)
        
        # Configurar timeout
        instr.timeout = 5000  # 5 segundos
        
        # Intentar obtener identificación
        try:
            idn = instr.query('*IDN?').strip()
            instr.close()
            return {
                'success': True,
                'address': address,
                'response': idn,
                'status': 'connected'
            }
        except Exception as e:
            instr.close()
            return {
                'success': False,
                'address': address,
                'error': f"No se pudo comunicar con el instrumento: {str(e)}",
                'status': 'no_response'
            }
            
    except Exception as e:
        return {
            'success': False,
            'address': address,
            'error': f"No se pudo abrir la conexión: {str(e)}",
            'status': 'connection_failed'
        }

def get_instrument(address):
    """Obtiene un instrumento, con mejor manejo de errores"""
    try:
        if address not in open_instruments:
            logger.info(f"Abriendo conexión con instrumento: {address}")
            instr = rm.open_resource(address)
            # Configurar timeout por defecto
            instr.timeout = 10000  # 10 segundos
            open_instruments[address] = instr
            logger.info(f"Conexión establecida con: {address}")
        return open_instruments[address]
    except Exception as e:
        logger.error(f"Error al abrir instrumento {address}: {e}")
        raise Exception(f"No se pudo conectar con el instrumento {address}: {str(e)}")

def close_all_instruments():
    """Cierra todas las conexiones de instrumentos"""
    try:
        for address, instr in open_instruments.items():
            try:
                logger.info(f"Cerrando conexión con: {address}")
                instr.close()
            except Exception as e:
                logger.error(f"Error al cerrar instrumento {address}: {e}")
        open_instruments.clear()
        logger.info("Todas las conexiones de instrumentos cerradas")
    except Exception as e:
        logger.error(f"Error al cerrar instrumentos: {e}")

def get_system_info():
    """Obtiene información del sistema GPIB"""
    try:
        return {
            'success': True,
            'backend': str(rm),
            'version': 'PyVISA',
            'available_resources': rm.list_resources('?*'),
            'open_connections': len(open_instruments),
            'open_addresses': list(open_instruments.keys())
        }
    except Exception as e:
        logger.error(f"Error al obtener información del sistema: {e}")
        return {
            'success': False,
            'error': str(e)
        }
