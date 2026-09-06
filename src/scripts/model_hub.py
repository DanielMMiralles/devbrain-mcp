"""
DevBrain Elite Model Hub & Omni Router Gateway:
Configuracion optimizada con despacho inteligente multi-modelo.
Soporta enrutamiento via OmniRoute (http://localhost:8000/v1) con conmutacion automatica
y fallback directo segun criticidad de la tarea.
"""
import sys
import io
import os
import json
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

OMNI_ROUTE_URL = os.getenv("OMNI_ROUTE_URL", "http://localhost:8000/v1")

ROUTING_PROFILES = {
    "FAST": {
        "tier": "Mecanico & Alta Frecuencia (Costo Minimo)",
        "models": ["gemini-2.5-flash", "claude-3-5-haiku", "deepseek-chat"],
        "recommended": "gemini-2.5-flash",
        "description": "Ideal para daemons en background, extraccion de tags, clasificacion de inbox y tareas de monitoreo.",
        "cost_tier": "$"
    },
    "FRONTIER": {
        "tier": "Razonamiento Profundo & Auditoria Implacable",
        "models": ["claude-3-7-sonnet", "gemini-2.5-pro", "gpt-4o"],
        "recommended": "claude-3-7-sonnet",
        "description": "Utilizado para Modo Debate Sin Filtros, diseno de arquitectura distribuida, OpenSpec y refactorizaciones de alto riesgo.",
        "cost_tier": "$$$"
    },
    "CODER": {
        "tier": "Scaffolding & Cumplimiento BDD Estricto",
        "models": ["claude-3-5-sonnet", "gpt-4o", "qwen-2.5-coder-32b"],
        "recommended": "claude-3-5-sonnet",
        "description": "Generacion determinista de DTOs, controllers, servicios y migraciones de bases de datos.",
        "cost_tier": "$$"
    }
}

TASK_MAPPING = {
    "debate": "FRONTIER",
    "architecture": "FRONTIER",
    "red_team": "FRONTIER",
    "spec": "FRONTIER",
    "code": "CODER",
    "scaffold": "CODER",
    "refactor": "CODER",
    "daemon": "FAST",
    "summary": "FAST",
    "inbox": "FAST",
    "rag": "FAST",
    "graphify": "FAST"
}

import urllib.request

def check_endpoint_health(url: str, timeout_sec: float = 0.2) -> bool:
    """Verifica si el gateway local OmniRoute esta activo sin bloquear."""
    try:
        # Peticion rapida al endpoint
        req = urllib.request.Request(f"{url}/models", method="GET")
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            return resp.status in [200, 401, 403]
    except Exception:
        return False

def route_model(task_type: str = "general") -> dict:
    profile_key = TASK_MAPPING.get(task_type.lower(), "FRONTIER")
    profile = ROUTING_PROFILES[profile_key]
    is_online = check_endpoint_health(OMNI_ROUTE_URL)
    status = "ONLINE (Gateway Activo)" if is_online else "STANDBY (Despacho directo por API / Provider Fallback)"
    return {
        "task_type": task_type,
        "profile": profile_key,
        "recommended_model": profile["recommended"],
        "fallback_models": profile["models"],
        "endpoint": OMNI_ROUTE_URL,
        "endpoint_status": status,
        "cost_tier": profile["cost_tier"],
        "description": profile["description"]
    }

def print_matrix():
    print("=== DEV-BRAIN OMNI ROUTER & MODEL HUB ===")
    print(f"Gateway Endpoint: {OMNI_ROUTE_URL}")
    for key, info in ROUTING_PROFILES.items():
        print(f"\n* [{key}] -> {info['tier']} ({info['cost_tier']})")
        print(f"  Recomendado: {info['recommended']}")
        print(f"  Pool de Fallback: {', '.join(info['models'])}")
        print(f"  Uso: {info['description']}")

if __name__ == "__main__":
    print_matrix()
    test_route = route_model("debate")
    print(f"\nEjemplo de despacho para 'debate':\n{json.dumps(test_route, indent=2, ensure_ascii=False)}")