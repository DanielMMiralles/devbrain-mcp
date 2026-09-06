"""
devbrain_debate.py: Motor de evaluacion critica sin filtros (Red Team & Ponytail Audit).
Analiza propuestas arquitectonicas, ideas de negocio y stacks tecnicos con cero complacencia.
"""

import sys
import io
import re
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Indicadores de sobre-ingenieria comun (Red Flags)
OVERENGINEERING_FLAGS = [
    (r"\b(microservicios?|microservices?)\b", "Microservicios prematuros", "Un monolito modular en una sola base de datos casi siempre es 10x mas barato y facil de mantener en etapas iniciales."),
    (r"\b(kubernetes|k8s)\b", "Orquestacion pesada (K8s)", "¿Realmente se requiere Kubernetes o basta con Docker Compose / Systemd / PaaS ligero?"),
    (r"\b(kafka|rabbitmq)\b", "Brokers de mensajeria complejos", "Postgres (LISTEN/NOTIFY o tabla de jobs) o Redis Streams resuelven la mayoria de casos sin la complejidad operativa de un cluster Kafka."),
    (r"\b(graphql)\b", "GraphQL innecesario", "REST simple con endpoints claros o RPC ahorra complejidad de resolvers, N+1 queries y caching."),
    (r"\b(redis)\b", "Cache prematuro", "A menos que haya miles de peticiones concurrentes por segundo, optimizar queries con indices en Postgres es gratis y no anade SPOF."),
    (r"\b(elasticsearch|solr)\b", "Motor de busqueda dedicado", "Postgres Full-Text Search o pg_trgm cubre el 95% de casos de busqueda sin duplicar datos ni requerir sincronizacion."),
    (r"\b(langchain|llamaindex)\b", "Frameworks de agentes pesados", "Muchas veces un script directo con llamadas a API y prompts estructurados es mas mantenible que cadenas de abstraccion opacas."),
    (r"\b(abstract\s*factory|factory\b.*\bgenerica|factory\b.*\bpattern|\bfactory\b.*\bproveedor)\b", "Patrones de Fabrica Prematuros", "Un diccionario de funciones o un switch simple elimina capas completas de abstraccion innecesarias."),
    (r"\b(herencia\b.*(?:nivel|multiple)|\bhierarchy\b|\bniveles\s*de\s*herencia)\b", "Jerarquias de herencia profundas", "Composicion sobre herencia. Mas de 2 niveles de herencia crea un laberinto de fragilidad."),
    (r"\b(custom\s*(orm|framework|auth|protocolo|engine)|motor\s*propio)\b", "Reinvencion de la rueda", "Usar librerias estandar probadas en produccion en lugar de construir un framework propio."),
    (r"\b(event\s*sourcing|cqrs)\b", "Event Sourcing / CQRS Prematuro", "Solo se justifica ante auditoria financiera estricta o altisima concurrencia; para CRUD convencional duplica el codigo.")
]

def analyze_feasibility(proposal_text: str, project_name: str = "General") -> str:
    """Ejecuta el protocolo de debate y auditoria Ponytail sobre una propuesta."""
    clean_text = proposal_text.strip()
    if not clean_text:
        return "Error: No se proporciono texto ni contexto para la evaluacion."

    detected_flags = []
    for pattern, name, advice in OVERENGINEERING_FLAGS:
        if re.search(pattern, clean_text, re.IGNORECASE):
            detected_flags.append((name, advice))

    # Determinar veredicto preliminar
    if len(detected_flags) >= 3:
        verdict = "SOBREDIMENSIONADO / ALTO RIESGO DE FRACASO OPERATIVO"
        verdict_color = "❌"
    elif len(detected_flags) in [1, 2]:
        verdict = "VIABLE CON RECORTES OBLIGATORIOS (FILTRO PONYTAIL)"
        verdict_color = "⚠️"
    else:
        verdict = "PRAGMATICO / ARQUITECTURA SANA"
        verdict_color = "✅"

    report = []
    report.append(f"# 🥊 Veredicto Tecnico DevBrain: {project_name}")
    report.append("")
    report.append(f"## 1. Dictamen Ejecutivo")
    report.append(f"**Veredicto**: {verdict_color} `{verdict}`")
    report.append("")
    report.append("> [!WARNING]")
    report.append("> **Modo Debate Activo**: Analisis sin filtros de cortesia. Enfocado en costos ocultos, mantenimiento real y simplicidad radical.")
    report.append("")

    report.append("## 2. Analisis de Friccion y Riesgos de Operacion (Red Teaming)")
    if detected_flags:
        for name, advice in detected_flags:
            report.append(f"- **{name}**: {advice}")
    else:
        report.append("- No se detectaron patrones tipicos de sobre-ingenieria en los terminos analizados.")

    report.append("")
    report.append("## 3. La Escalera Ponytail (¿Que podar?)")
    report.append("1. **YAGNI**: Todo lo que no atienda un requerimiento de esta semana debe ser descartado.")
    report.append("2. **Standard Lib / Nativo Primero**: Favorecer herramientas ya instaladas en el sistema antes de anadir dependencias.")
    report.append("3. **Monolito antes que distribuido**: Mantener el estado en un unico punto de verdad verificable.")

    report.append("")
    report.append("## 4. Alternativa Cinica Minima (Recomendacion)")
    if detected_flags:
        report.append(f"Reducir el stack eliminando {[f[0] for f in detected_flags]}. Construir una solucion de un solo proceso respaldada por SQLite/Postgres o funciones nativas. Salir a produccion en dias, no meses.")
    else:
        report.append("La direccion parece sobria. Asegurar contratos de prueba BDD claros con OpenSpec antes de escribir codigo.")

    return "\n".join(report)

def audit_complexity(target_text: str) -> str:
    """Auditoria especifica de Ponytail para analizar codigo o requerimientos tecnicos."""
    lines = target_text.strip().splitlines()
    total_lines = len(lines)
    
    # Evaluar patrones de sobre-ingenieria
    detected_flags = []
    for pattern, name, advice in OVERENGINEERING_FLAGS:
        if re.search(pattern, target_text, re.IGNORECASE):
            detected_flags.append((name, advice))
            
    report = ["# ✂️ Auditoria de Complejidad Ponytail\n"]
    report.append(f"- **Lineas analizadas**: {total_lines}")
    
    if detected_flags:
        report.append(f"- **Veredicto**: ⚠️ Alerta de Sobre-Ingenieria Detectada ({len(detected_flags)} patrones)")
        report.append("\n### Violaciones YAGNI Encontradas:")
        for name, advice in detected_flags:
            report.append(f"- **{name}**: {advice}")
        report.append("\n### Accion Inmediata:")
        report.append("Podar estas abstracciones y usar la solucion nativa o estandar mas directa.")
    else:
        report.append("- **Veredicto**: ✅ Diseno Limpio / Conforme a la escalera YAGNI.")
        report.append("- No se detectaron sobre-abstracciones flagrantes.")
        
    return "\n".join(report)

if __name__ == "__main__":
    test_input = sys.argv[1] if len(sys.argv) > 1 else "Queremos montar un cluster de microservicios con Kubernetes, Kafka, GraphQL y Elasticsearch para gestionar pedidos de comida."
    print(analyze_feasibility(test_input, "Test-Project"))
