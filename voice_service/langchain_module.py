import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Intentar cargar LangChain con Ollama (opcional)
USE_LLM = False
try:
    from langchain_ollama import OllamaLLM
    from langchain_core.prompts import PromptTemplate
    
    llm = OllamaLLM(model="llama3", base_url="http://ollama:11434")
    
    template = """
Eres un asistente para un sistema de parqueo inteligente llamado Nuvora.
Convierte la pregunta del usuario en una instrucción estructurada en formato JSON.

Ejemplos:
Usuario: "¿Cuántos carros hay en total?"
Respuesta: {{"query_type": "total_cars"}}

Usuario: "¿Cuántos vehículos activos hay?"
Respuesta: {{"query_type": "active_vehicles"}}

Usuario: "Buscar placa ABC123"
Respuesta: {{"query_type": "search_plate", "plate": "ABC123"}}

Usuario: "Mostrar historial"
Respuesta: {{"query_type": "history"}}

Usuario: "Estadísticas del día"
Respuesta: {{"query_type": "daily_stats"}}

Usuario: "{user_input}"
Respuesta:"""

    prompt = PromptTemplate(template=template, input_variables=["user_input"])
    chain = prompt | llm
    USE_LLM = True
    logger.info("✅ LangChain con Ollama configurado")
    
except Exception as e:
    logger.warning(f"⚠️ No se pudo cargar Ollama, usando interpretación basada en reglas: {e}")

def interpret_with_llm(user_input: str) -> Dict[str, Any]:
    """Interpreta el comando usando LLM (Ollama)"""
    try:
        response = chain.invoke({"user_input": user_input})
        return json.loads(response)
    except Exception as e:
        logger.error(f"Error con LLM: {e}")
        return interpret_with_rules(user_input)

def interpret_with_rules(user_input: str) -> Dict[str, Any]:
    """
    Interpreta el comando usando reglas simples (fallback).
    Basado en el sistema de tickets actual.
    """
    import unicodedata
    
    # Normalizar texto: quitar tildes y convertir a minúsculas
    def normalize_text(text: str) -> str:
        """Elimina tildes y normaliza el texto"""
        text = text.lower().strip()
        # Eliminar tildes
        text = ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )
        return text
    
    text = normalize_text(user_input)
    
    # ========== BÚSQUEDA DE PLACAS (PRIORIDAD ALTA) ==========
    
    import re
    
    # Función para reconstruir placas de transcripciones fragmentadas
    def reconstruct_plate(text: str) -> str:
        """
        Intenta reconstruir placas que Whisper transcribió con espacios.
        Ej: "a vd 1-1-1" → "AVD111"
        """
        # Eliminar espacios y guiones, convertir a mayúsculas
        cleaned = text.upper().replace(" ", "").replace("-", "")
        # Reemplazar letras sueltas comunes de Whisper
        cleaned = cleaned.replace("VD", "VD").replace("LL", "LL")
        return cleaned
    
    # Buscar patrón de placa: 3 letras + 2-3 números (ABC123, ZCX123, etc.)
    plate_match = re.search(r'\b([A-Z]{3}[-\s]?\d{2,3})\b', user_input.upper())
    
    if plate_match:
        plate = plate_match.group(1).replace("-", "").replace(" ", "")
        return {"query_type": "search_plate", "plate": plate}
    
    # Si menciona palabras clave de búsqueda pero no encontró placa en formato estándar
    # Buscar cualquier combinación de letras y números que parezca una placa
    if any(word in text for word in ["buscar", "busca", "encontrar", "ver", "estado", "consultar", "revisar", "verificar"]):
        # Intentar reconstruir placa de texto fragmentado
        # Ej: "buscar carro a vd 1-1-1" → extraer "avd111"
        palabras = user_input.upper().split()
        
        # Buscar índice de palabra clave
        keyword_idx = -1
        for i, palabra in enumerate(palabras):
            if any(kw in palabra.lower() for kw in ["buscar", "ver", "estado", "consultar"]):
                keyword_idx = i
                break
        
        # Si encontramos keyword, tomar todo lo que viene después
        if keyword_idx >= 0:
            resto = " ".join(palabras[keyword_idx + 1:])
            # Limpiar palabras comunes
            resto = resto.replace("CARRO", "").replace("PLACA", "").replace("EL", "").replace("LA", "")
            # Reconstruir placa quitando espacios y guiones
            placa_reconstruida = reconstruct_plate(resto)
            
            # Verificar si tiene formato de placa (letras + números, mínimo 5 caracteres)
            if re.search(r'[A-Z]{2,}', placa_reconstruida) and re.search(r'\d{2,}', placa_reconstruida):
                if len(placa_reconstruida) >= 5 and len(placa_reconstruida) <= 7:
                    return {"query_type": "search_plate", "plate": placa_reconstruida}
        
        # Método anterior: buscar palabras con letras Y números
        for palabra in reversed(palabras):  # Revisar desde el final
            # Limpiar guiones y espacios
            palabra_limpia = palabra.replace("-", "").replace(" ", "")
            # Verificar si tiene letras Y números
            if re.search(r'[A-Z]{2,}', palabra_limpia) and re.search(r'\d{2,}', palabra_limpia):
                # Extraer solo letras y números
                placa_extraida = re.sub(r'[^A-Z0-9]', '', palabra_limpia)
                if len(placa_extraida) >= 5:  # Al menos 5 caracteres para ser placa válida
                    return {"query_type": "search_plate", "plate": placa_extraida}
        
        # Si mencionó buscar pero no encontramos placa
        return {"query_type": "search_plate", "plate": None}
    
    # Si menciona "placa" específicamente
    if "placa" in text:
        # Buscar cualquier combinación de letras y números después de "placa"
        placa_match = re.search(r'placa\s+([A-Z0-9]+)', user_input.upper())
        if placa_match:
            return {"query_type": "search_plate", "plate": placa_match.group(1)}
        return {"query_type": "search_plate", "plate": None}
    
    # ========== COMANDOS DE TICKETS (más específicos primero) ==========
    
    # Mis tickets
    if any(word in text for word in ["mis tickets", "mis tiquets", "mis boletas", "tickets del turno"]):
        if any(word in text for word in ["abiertos", "abiertas", "activos", "activas"]):
            return {"query_type": "my_open_tickets"}
        return {"query_type": "my_tickets"}
    
    # Resumen/estadísticas personales
    if any(word in text for word in ["mi resumen", "mi turno", "mis estadisticas", "resumen del turno", "cuanto he ganado", "cuanto gane", "mis ganancias", "total ganado", "dinero", "recaudado"]):
        return {"query_type": "my_stats"}
    
    # Tickets abiertos
    if any(word in text for word in ["tickets abiertos", "tiquets abiertos"]):
        return {"query_type": "my_open_tickets"}
    
    # Carros/vehículos activos o adentro (sin "cuántos")
    if any(word in text for word in ["carros", "vehiculos", "motos", "autos"]):
        if any(word in text for word in ["abiertos", "abiertas", "activos", "activas", "adentro", "dentro", "estacionados", "parqueados"]):
            return {"query_type": "my_open_tickets"}
    
    # ========== CANTIDADES ==========
    
    if any(word in text for word in ["cuantos", "cuantas", "total", "cantidad"]):
        # Si pregunta explícitamente por el TOTAL de tickets históricos
        if any(word in text for word in ["total de tickets", "total de tiquets", "todos los tickets", "todos los tiquets", "total tickets", "total tiquets", "historico"]):
            return {"query_type": "my_tickets"}
        
        # Si menciona "tickets" o "tiquets" con "total" → total histórico
        if "total" in text and any(word in text for word in ["tickets", "tiquets", "boletas"]):
            return {"query_type": "my_tickets"}
        
        # Si pregunta por carros/vehículos/motos con "hay" → significa activos/adentro
        if any(word in text for word in ["carros", "vehiculos", "motos", "autos"]) and "hay" in text:
            if not re.search(r'[A-Z]{2,}\d{2,}', text.upper().replace("-", "").replace(" ", "")):
                return {"query_type": "my_open_tickets"}
        
        # Si pregunta explícitamente por abiertos/activos/adentro
        if any(word in text for word in ["abiertos", "abiertas", "activos", "activas", "adentro", "dentro", "estacionados", "parqueados"]):
            return {"query_type": "my_open_tickets"}
        
        # Por defecto, "cuántos" sin más contexto → tickets abiertos (lo más común)
        return {"query_type": "my_open_tickets"}
    
    # ========== ÚLTIMA DETECCIÓN/TICKET ==========
    
    if any(word in text for word in ["ultimo", "ultima", "reciente", "mas reciente", "ultimo registro", "ultima deteccion", "ultimo ticket", "ultimo vehiculo", "ultimo ingreso", "ultimo carro"]):
        return {"query_type": "last_detection"}
    
    # ========== USUARIOS ==========
    
    if any(word in text for word in ["usuarios", "lista de usuarios", "mostrar usuarios", "cuantos usuarios"]):
        return {"query_type": "list_users"}
    
    # ========== DEFAULT ==========
    
    return {"query_type": "unknown"}

def interpret(user_input: str) -> Dict[str, Any]:
    """
    Función principal de interpretación.
    Usa LLM si está disponible, sino usa reglas.
    """
    logger.info(f"🧠 Interpretando: {user_input}")
    
    if USE_LLM:
        result = interpret_with_llm(user_input)
    else:
        result = interpret_with_rules(user_input)
    
    logger.info(f"✅ Interpretación: {result}")
    return result