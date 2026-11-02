"""
creative_odd.py: Marco de Trabajo D-ODD (Dynamic Outcome-Driven Development)
Evita la rigidez cognitiva y el sesgo de anclaje contextual ("Vault Overfitting")
mediante clasificación Cynefin, estimulación lateral de De Bono y triangulación dialéctica.
"""

from __future__ import annotations

import re
import hashlib
from enum import Enum
from typing import Dict, List, Any, Optional

class CynefinDomain(str, Enum):
    CLEAR = "clear"               # Simple, mejores prácticas canónicas, vía rápida
    COMPLICATED = "complicated"   # Análisis técnico experto (FTS5 + Graphify)
    COMPLEX = "complex"           # Emergente: Prohibido converger en 1 sola respuesta, requiere D-ODD
    CHAOTIC = "chaotic"           # Incidentes / Inestabilidad: Contención inmediata primero

class CreativeMode(str, Enum):
    DIVERGENT = "divergent"               # Explora activamente arquitecturas fuera del Vault
    RED_TEAM = "red_team"                 # Cuestiona y ataca las premisas del Vault
    FIRST_PRINCIPLES = "first_principles" # Descompone el problema en restricciones físicas/básicas
    LATERAL = "lateral"                   # Aplica provocaciones ortogonales de Edward de Bono
    CONSERVATIVE = "conservative"         # Alineación estricta con el historial del Vault


# Banco de Provocaciones de Pensamiento Lateral (De Bono aplicado a Software)
LATERAL_PROVOCATIONS = [
    {
        "id": "ZERO_DEPENDENCY",
        "title": "Restricción de Cero Dependencias",
        "question": "¿Cómo resolverías esto utilizando exclusivamente la librería estándar y primitivas nativas del runtime, sin agregar paquetes externos?",
        "focus": "Simplicidad radical, menor superficie de ataque y cero fricción de supply chain."
    },
    {
        "id": "DEEP_MODULE",
        "title": "Inversión de Módulo Profundo (Ousterhout / Matt Pocock)",
        "question": "¿Cómo diseñarías la interfaz para que sea extraordinariamente simple (1 función o contrato limpio) mientras toda la complejidad queda encapsulada sin fugas?",
        "focus": "Ocultación de información, alta cohesión y bajo acoplamiento cognitivo."
    },
    {
        "id": "LATENCY_LOCALITY",
        "title": "Restricción de Latencia Crítica & Localidad",
        "question": "Si la operación tuviese un SLA estricto de p95 < 2ms, ¿cómo cambiaría la arquitectura de datos para eliminar saltos de I/O o locks de red?",
        "focus": "In-memory caching, estructuras de datos compactas y procesamiento local."
    },
    {
        "id": "INVERSION_COUNTERFACTUAL",
        "title": "Inversión Contrafáctica (Boyd OODA / Red Team)",
        "question": "¿Qué sucedería si la premisa que da por sentada el Vault fuese completamente falsa o estuviese desactualizada para el ecosistema actual (2026)?",
        "focus": "Desafío a la inercia histórica y prevención de deuda técnica acumulada."
    },
    {
        "id": "RADICAL_PRUNING",
        "title": "Poda Radical (Filtro Ponytail / YAGNI Extremo)",
        "question": "¿Cuál es la versión mínima que aporta el 90% del valor eliminando el 80% del código y las abstracciones hipotéticas para el futuro?",
        "focus": "Entrega de valor inmediato, menos líneas que mantener y mayor velocidad de iteración."
    },
    {
        "id": "APPEND_ONLY_IMMUTABLE",
        "title": "Inmutabilidad & Bitácora Append-Only",
        "question": "¿Cómo se estructuraría el estado si las mutaciones destructivas estuviesen prohibidas y todo fuera una secuencia auditable de eventos o snapshots?",
        "focus": "Depurabilidad determinista, concurrencia sin carreras y trazabilidad total."
    }
]


def classify_cynefin(
    objective: str,
    files_touched_estimate: int = 1,
    context_text: str = ""
) -> Dict[str, Any]:
    """Clasifica el requerimiento dentro del marco Cynefin adaptado a software.
    
    Determina si la tarea puede resolverse por vía canónica directa (Clear/Complicated)
    o si exige la activación obligatoria del motor de divergencia D-ODD (Complex).
    """
    text = f"{objective} {context_text}".lower()

    # Patrones para dominio Caótico (Incidentes graves, rotura de build, corrupción)
    chaotic_signals = [
        "caído", "crash", "corrupción", "data loss", "bloqueante",
        "production down", "rollback urgente", "fuga de memoria crítica", "segfault"
    ]
    if any(sig in text for sig in chaotic_signals):
        return {
            "domain": CynefinDomain.CHAOTIC.value,
            "badge": "🔥 [CYNEFIN: CAÓTICO]",
            "action_protocol": "stabilize_first",
            "divergence_required": False,
            "rationale": "Situación crítica o de contención. La prioridad absoluta es estabilizar, revertir o contener antes de innovar."
        }

    # Patrones para dominio Complejo (Arquitectura, incertidumbre, exploración, diseño)
    complex_patterns = [
        r"\b(arquitect\w*|architect\w*)\b",
        r"\b(diseñ\w*|design\w*)\b",
        r"\b(innova\w*)\b",
        r"\b(estructur\w*|structur\w*)\b",
        r"\b(estratég\w*|strateg\w*)\b",
        r"\b(alternativ\w*)\b",
        r"\b(evalua\w*|benchmark\w*)\b",
        r"\b(escalab\w*|scalab\w*)\b",
        r"\b(concurren\w*)\b",
        r"\b(desacopl\w*|decoupl\w*)\b",
        r"\b(migraci[oó]n|migrat\w*)\b",
        r"\b(nuevo\s+m[oó]dulo|new\s+module)\b",
        r"\b(divergen\w*|creativ\w*)\b",
        r"\b(toma\s+de\s+decisiones|decision\s+making)\b",
        r"\b(refactor\w*|rediseñ\w*)\b",
        r"\b(orquest\w*|orchestrat\w*)\b",
        r"\b(framework|d-odd)\b"
    ]
    has_complex_signals = any(re.search(pat, objective.lower()) for pat in complex_patterns)

    if has_complex_signals or files_touched_estimate >= 4:
        return {
            "domain": CynefinDomain.COMPLEX.value,
            "badge": "🌀 [CYNEFIN: COMPLEJO / EMERGENTE]",
            "action_protocol": "divergent_triangulation",
            "divergence_required": True,
            "rationale": "Problema de dominio complejo o multifactorial. Se prohíbe converger prematuramente en una sola receta del Vault; se requiere triangulación D-ODD."
        }

    # Patrones para dominio Complicado (Requiere análisis experto pero sigue patrones conocidos)
    complicated_signals = [
        "optimizar query", "indexación", "endpoint", "validación", "integrar api",
        "parsing", "esquema", "tipado", "test suite", "fts5"
    ]
    if any(sig in text for sig in complicated_signals) or files_touched_estimate > 1:
        return {
            "domain": CynefinDomain.COMPLICATED.value,
            "badge": "🧩 [CYNEFIN: COMPLICADO / EXPERTO]",
            "action_protocol": "analytical_graph",
            "divergence_required": False,
            "rationale": "Problema analítico bien acotado. Guiado por Graphify, búsqueda FTS5 y mejores prácticas ya establecidas."
        }

    # Dominio Claro (Vía rápida / Tareas directas)
    return {
        "domain": CynefinDomain.CLEAR.value,
        "badge": "⚡ [CYNEFIN: CLARO / CANÓNICO]",
        "action_protocol": "fast_track",
        "divergence_required": False,
        "rationale": "Requerimiento directo con relación causa-efecto obvia. Ejecución rápida y directa sin sobrecarga cognitiva."
    }


def select_provocations(objective: str, count: int = 2) -> List[Dict[str, str]]:
    """Selecciona provocaciones ortogonales deterministas basadas en el hash del requerimiento."""
    if not objective.strip():
        return LATERAL_PROVOCATIONS[:count]

    # Usar hash para selección determinista pero variada
    seed_val = int(hashlib.md5(objective.encode("utf-8")).hexdigest(), 16)
    provs = list(LATERAL_PROVOCATIONS)
    # Shuffle determinista ligero
    selected = []
    available = provs.copy()
    for i in range(min(count, len(available))):
        idx = (seed_val + i * 3) % len(available)
        selected.append(available.pop(idx))
    return selected


def triangulate_cognitive_odd(
    objective: str,
    project_name: str = "General",
    creative_mode: str = "divergent",
    vault_context: str = "",
    files_touched_estimate: int = 2
) -> Dict[str, Any]:
    """Ejecuta el protocolo de Triangulación Dialéctica D-ODD.
    
    1. Desacopla el Outcome (Job-to-be-Done).
    2. Modela la Tesis (Canónica del Vault).
    3. Construye la Antítesis (Divergente / Red Team fuera del cerebro).
    4. Inyecta Provocaciones de Pensamiento Lateral (De Bono).
    5. Sintetiza la solución ganadora con tareas ODD orientadas a resultados.
    """
    clean_obj = objective.strip() or "Optimización de arquitectura de software"
    cynefin = classify_cynefin(clean_obj, files_touched_estimate, vault_context)
    provocations = select_provocations(clean_obj, count=2)

    # 1. Extracción de Outcomes (Job-to-be-Done)
    outcomes = {
        "job_to_be_done": clean_obj,
        "success_criteria": [
            "El comportamiento responde a la necesidad real sin añadir dependencias prescindibles.",
            "La solución es verificable mediante pruebas automatizadas con evidencia observada.",
            "La interfaz resultante es profunda y no filtra complejidad interna hacia el cliente.",
            "Consistencia temporal: no rompe los contratos existentes del sistema."
        ],
        "invariants": [
            "Compatibilidad total con el entorno y la suite Gentle-AI (v4.5+).",
            "Latencia de ejecución predecible sin bloqueos innecesarios en caliente."
        ]
    }

    # 2. Tesis: La Solución Canónica (Inercia del Vault)
    thesis_title = f"Enfoque Canónico Incremental (Basado en Memoria del Vault)"
    if vault_context:
        thesis_desc = (
            f"Aprovechar los patrones y snippets existentes en el Vault para [[{project_name}]]. "
            f"Seguir la convención histórica del repositorio minimizando cambios estructurales."
        )
        thesis_pros = ["Alta familiaridad para el equipo.", "Bajo riesgo inmediato de regresión.", "Cero tiempo invertido en rediseñar esquemas."]
        thesis_risks = ["Acumulación de deuda técnica por parches sobre parches.", "Riesgo de anclaje a decisiones tomadas cuando el contexto era distinto."]
    else:
        thesis_desc = (
            "Implementación estándar convencional según el canon habitual del proyecto, "
            "extendiendo las clases y módulos ya presentes."
        )
        thesis_pros = ["Predecible y directo.", "Mínima perturbación de la estructura de carpetas."]
        thesis_risks = ["Potencial rigidez cognitiva.", "Desaprovecha oportunidades de simplificación radical."]

    # 3. Antítesis: La Solución Disruptiva (Fuera del Cerebro / Primeros Principios)
    mode_lower = creative_mode.lower()
    if mode_lower == CreativeMode.RED_TEAM.value:
        antithesis_title = "Antítesis Red-Team: Desafío de Supuestos Fundamentales"
        antithesis_desc = (
            "Cuestionar si el componente realmente debe existir o si el requerimiento es un síntoma de una abstracción rota. "
            "Reemplazar capas intermedias por una solución directa de primeros principios."
        )
        diff_focus = "Eliminación de intermediarios y desacoplamiento estricto."
    elif mode_lower == CreativeMode.FIRST_PRINCIPLES.value:
        antithesis_title = "Antítesis de Primeros Principios: Reconstrucción desde Restricciones Físicas"
        antithesis_desc = (
            "Ignorar el historial previo. Analizar únicamente los datos de entrada, el estado deseado y la transformación matemática más directa."
        )
        diff_focus = "Diseño axiomático y estructuras de datos puras."
    elif mode_lower == CreativeMode.LATERAL.value:
        antithesis_title = f"Antítesis de Pensamiento Lateral (Provocación: {provocations[0]['title']})"
        antithesis_desc = (
            f"Forzar el diseño bajo la restricción: {provocations[0]['question']} "
            "Romper la secuencia lógica previsible para descubrir un atajo arquitectónico elegante."
        )
        diff_focus = provocations[0]["focus"]
    else: # DIVERGENT (default)
        antithesis_title = "Antítesis Divergente: Arquitectura Moderna Desacoplada (2026)"
        antithesis_desc = (
            "Diseñar un módulo profundo y autocontenido con tipos rigurosos y cero acoplamiento temporal. "
            "Aislar la nueva capacidad detrás de una frontera limpia, haciéndola completamente testeable sin simular el entorno."
        )
        diff_focus = "Alta modularidad, diseño emergente y contratos explícitos."

    # 4. Síntesis Dialéctica: Decisión Equilibrada por Outcomes
    synthesis_title = "Síntesis D-ODD: Arquitectura Verificable Orientada a Resultados"
    synthesis_rationale = (
        "Se adopta la robustez y simplicidad de la Antítesis en la interfaz pública y el núcleo de datos, "
        "pero respetando las fronteras y convenciones de entrega de la Tesis para garantizar interoperabilidad inmediata sin fricción."
    )

    # 5. Plan de Tareas ODD de Acción Inmediata (Gentle-AI compatible)
    tasks = [
        f"Definir el contrato de entrada/salida e invariantes del outcome para: {clean_obj[:50]}",
        f"Implementar el núcleo funcional desacoplado aplicando la síntesis D-ODD",
        "Ejecutar pruebas observadas con evidencia de ejecución y validación de casos frontera",
        "Integrar con la superficie pública del proyecto manteniendo compatibilidad regresiva"
    ]

    return {
        "objective": clean_obj,
        "project": project_name,
        "cynefin": cynefin,
        "creative_mode": creative_mode,
        "outcomes": outcomes,
        "provocations": provocations,
        "thesis": {
            "title": thesis_title,
            "description": thesis_desc,
            "pros": thesis_pros,
            "risks": thesis_risks
        },
        "antithesis": {
            "title": antithesis_title,
            "description": antithesis_desc,
            "focus": diff_focus
        },
        "synthesis": {
            "title": synthesis_title,
            "rationale": synthesis_rationale
        },
        "tasks": tasks
    }


def format_creative_odd_markdown(data: Dict[str, Any]) -> str:
    """Formatea la triangulación dialéctica en un reporte Markdown ejecutivo de alta densidad."""
    cy = data["cynefin"]
    obj = data["objective"]
    proj = data["project"]
    mode = data["creative_mode"].upper()
    th = data["thesis"]
    anti = data["antithesis"]
    syn = data["synthesis"]
    provs = data["provocations"]
    tasks = data["tasks"]
    outcomes = data["outcomes"]

    lines = [
        f"# 🧠 DevBrain D-ODD: Triangulación Dialéctica & Divergencia Cognitiva",
        f"- **Proyecto**: [[{proj}]]",
        f"- **Objetivo**: {obj}",
        f"- **Modo Creativo**: `{mode}` | **Diagnóstico Cynefin**: {cy['badge']}",
        f"- **Directiva**: {cy['rationale']}",
        "",
        "---",
        "",
        "## 🎯 1. Desacoplamiento de Resultados (Job-to-be-Done)",
        f"**Propósito Fundamental**: {outcomes['job_to_be_done']}",
        "",
        "**Criterios de Aceptación Innegociables**:",
    ]
    for sc in outcomes["success_criteria"]:
        lines.append(f"- [ ] {sc}")
    lines.append("")
    lines.append("**Invariantes de Sistema**:")
    for inv in outcomes["invariants"]:
        lines.append(f"- 🛡️ {inv}")
    lines.append("")

    lines.extend([
        "## ⚖️ 2. Triangulación Dialéctica: Tesis vs. Antítesis",
        "",
        f"### 🏛️ Tesis (Canon del Vault / Memoria Histórica)",
        f"*{th['title']}*",
        f"{th['description']}",
        "",
        "**Puntos Fuertes**:",
    ])
    for p in th["pros"]:
        lines.append(f"- ✅ {p}")
    lines.append("")
    lines.append("**Riesgos de Rigidez / Estancamiento**:")
    for r in th["risks"]:
        lines.append(f"- ⚠️ {r}")
    lines.append("")

    lines.extend([
        f"### ⚡ Antítesis (Pensamiento Disruptivo / Fuera del Cerebro)",
        f"*{anti['title']}*",
        f"{anti['description']}",
        f"",
        f"**Foco de Ruptura**: {anti['focus']}",
        "",
        "### 🎲 3. Provocaciones de Pensamiento Lateral (Edward de Bono)",
    ])
    for idx, pv in enumerate(provs, 1):
        lines.append(f"**P{idx}: {pv['title']}**")
        lines.append(f"> {pv['question']}")
        lines.append(f"> *Enfoque*: {pv['focus']}\n")

    lines.extend([
        "## 🏆 4. Síntesis D-ODD (Decisión Final Basada en Outcomes)",
        f"*{syn['title']}*",
        f"{syn['rationale']}",
        "",
        "---",
        "",
        "## 📋 5. Tareas ODD de Acción Inmediata (Gentle-AI & Engram Ready)",
        "<!-- Heurística ODD: Orientación adaptativa por valor, sin sobrecarga burocrática -->"
    ])
    for idx, t in enumerate(tasks, 1):
        lines.append(f"- [ ] [TASK-{idx:02d}] {t}")

    lines.extend([
        "",
        "👉 **Directiva para el Agente**: El marco D-ODD ha desbloqueado la rigidez del Vault. Procede con TASK-01 ejecutando los tests y validando con evidencia real observada."
    ])

    return "\n".join(lines)


def run_creative_odd_pipeline(
    objective: str,
    project_name: str = "General",
    creative_mode: str = "divergent",
    vault_context: str = "",
    files_touched_estimate: int = 2
) -> str:
    """Función de entrada para invocar el pipeline D-ODD completo."""
    triangulation = triangulate_cognitive_odd(
        objective=objective,
        project_name=project_name,
        creative_mode=creative_mode,
        vault_context=vault_context,
        files_touched_estimate=files_touched_estimate
    )
    return format_creative_odd_markdown(triangulation)
