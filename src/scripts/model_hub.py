"""
DevBrain Elite Model Hub:
Configuración optimizada hacia la máxima capacidad cognitiva y de razonamiento profundo.
Prioriza exactitud arquitectónica, cero alucinaciones y estricto cumplimiento de BDD/DDD
sobre el costo de tokens.
"""
import sys
import json
from pathlib import Path

ELITE_MODELS = {
    "AGY_PRIMARY": {
        "tier": "Arquitecto Senior & Razonamiento Complejo (Top Tier)",
        "model_id": "claude-3-7-sonnet-thought / gemini-2.0-pro-exp",
        "description": "Modelo de referencia para redacción de specs, DDD táctico, diseño distribuido y refactorizaciones críticas con cadena de pensamiento extendida (Extended Thinking).",
        "surface": "Antigravity IDE & Chat Canvas"
    },
    "OPENCODE_TERMINAL": {
        "tier": "Agente Autónomo de Ejecución en Terminal",
        "model_id": "anthropic/claude-3-7-sonnet / opencode/deepseek-v4-flash-free",
        "description": "Orquestador de terminal para ejecución autónoma de tasks.md, tests BDD y compilación.",
        "surface": "OpenCode CLI"
    },
    "SPECIALIZED_CODER": {
        "tier": "Generación Determinista de Código & Scaffolding",
        "model_id": "claude-3-5-sonnet-latest / gpt-4o",
        "description": "Generación exacta de DTOs, NestJS controllers, FastAPI routers y esquemas de base de datos sin atajos sintácticos.",
        "surface": "Spec-to-Scaffold Engine"
    }
}

def print_matrix():
    print("=== CONFIGURACIÓN DE MODELOS DE ÉLITE (MÁXIMA CAPACIDAD) ===")
    for key, info in ELITE_MODELS.items():
        print(f"\n* [{key}] -> {info['tier']}")
        print(f"  Modelo: {info['model_id']}")
        print(f"  Entorno: {info['surface']}")
        print(f"  Capacidad: {info['description']}")

if __name__ == "__main__":
    print_matrix()