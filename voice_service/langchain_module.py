import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Intentar cargar LangChain con Ollama (opcional)
USE_LLM = False
try:
    from langchain_ollama import OllamaLLM
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    
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
    Esto funciona sin necesidad de LLM externo.
    """
    text = user_input.lower().strip()
    
    # Reglas de interpretación
    if any(word in text for word in ["cuántos", "cuantos", "total", "cantidad"]):
        if any(word in text for word in ["activos", "parqueadero", "estacionados"]):
            return {"query_type": "active_vehicles"}
        if any(word in text for word in ["ingresaron", "entraron", "entrada"]):
            return {"query_type": "entries_count"}
        return {"query_type": "total_cars"}
    
    elif any(word in text for word in ["buscar", "busca", "encontrar", "placa"]):
        # Extraer placa (formato: ABC123 o ABC-123)
        import re
        plate_match = re.search(r'\b([A-Z]{3}[-\s]?\d{3})\b', text.upper())
        if plate_match:
            plate = plate_match.group(1).replace("-", "").replace(" ", "")
            return {"query_type": "search_plate", "plate": plate}
        return {"query_type": "search_plate", "plate": None}
    
    elif any(word in text for word in ["historial", "salidas", "cerrados"]):
        return {"query_type": "history"}
    
    elif any(word in text for word in ["estadísticas", "estadisticas", "resumen", "día"]):
        return {"query_type": "daily_stats"}
    
    elif any(word in text for word in ["cupos", "espacios", "disponibles"]):
        return {"query_type": "available_spaces"}
    
    elif any(word in text for word in ["última", "ultima", "reciente", "placa detectada"]):
        return {"query_type": "last_detection"}
    
    else:
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