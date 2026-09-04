"""
Generador de Preguntas Clave para Spec.md según el Tipo de Sistema.
Ayuda a definir los requerimientos y contratos BDD sin omitir detalles críticos.
"""
import sys
import argparse

QUESTIONNAIRES = {
    "api": [
        "¿Cuáles son los recursos principales y sus operaciones CRUD o transaccionales?",
        "¿Qué estrategia de autenticación y autorización se requiere (JWT, API Key, RBAC)?",
        "¿Cuáles son los SLAs de latencia y throughput esperados?",
        "¿Qué campos son estrictamente obligatorios y cuáles opcionales en el payload?",
        "¿Cómo debe responder la API ante errores (formato RFC 7807 problem+json)?"
    ],
    "agent": [
        "¿Cuál es el objetivo principal del agente y cuándo se considera completada la tarea?",
        "¿Qué herramientas ([[Model Context Protocol (MCP)]], APIs, DBs) tiene permitidas invocar?",
        "¿Cuáles son los límites de recursión y timeout para evitar bucles infinitos?",
        "¿Qué estado o memoria debe persistir entre invocaciones (checkpoints en DB)?",
        "¿Requiere validación humana (Human-in-the-loop) antes de ejecutar acciones destructivas?"
    ],
    "microservice": [
        "¿A qué Bounded Context de [[Domain-Driven Design (DDD)]] pertenece este servicio?",
        "¿Qué eventos de dominio publica y a cuáles se suscribe (Event-Driven)?",
        "¿Cómo gestiona la consistencia de datos (Saga pattern, transacciones locales)?",
        "¿Cuál es la política de resiliencia ante caídas de servicios upstream (Circuit Breaker)?",
        "¿Qué métricas de salud (healthcheck liveness/readiness) expondrá para [[Kubernetes]]?"
    ],
    "frontend": [
        "¿Qué componentes atómicos y organismos de UI ([[shadcn-ui]]) compondrán la vista?",
        "¿Cómo se gestiona el estado global y del servidor (TanStack Query, Zustand)?",
        "¿Cuáles son los estados visuales requeridos (Loading, Error, Empty, Data)?",
        "¿Cuáles son los breakpoints responsivos prioritarios con [[Tailwind CSS]]?"
    ]
}

def get_questions(system_type: str):
    st = system_type.lower()
    questions = QUESTIONNAIRES.get(st, QUESTIONNAIRES["api"])
    print(f"=== Preguntas Clave para Spec.md ({st.upper()}) ===")
    for idx, q in enumerate(questions, 1):
        print(f"{idx}. {q}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("type", choices=["api", "agent", "microservice", "frontend"], default="api")
    args = parser.parse_args()
    get_questions(args.type)
