---
name: devbrain-odd
description: >-
  Protocolo canónico de Organic Driven Development (ODD) integrado sobre Gentle-AI:
  escalamiento orgánico sin burocracia, orquestación en 1 paso vía orchestrate_gentle_task,
  espejo en Engram, ciclo TDD observado (RED->GREEN->REFACTOR) y reanudación resiliente.
---

# DevBrain ODD Skill (Organic Driven Development sobre Gentle-AI)

Esta habilidad dota al agente del criterio arquitectónico de **ODD** operando como una capa de abstracción superior sobre Gentle-AI.

## 🎯 Principio Nuclear: Proporcionalidad y Cero Fricción
1. **La estructura aparece en proporción a la necesidad**:
   - **Lectura / Preguntas / Explicaciones**: Cero ceremonia, sin artefactos. Responde directamente.
   - **Cambios pequeños (<2 pasos)**: Implementar directamente con Gentle-AI y comprobaciones funcionales.
   - **Trabajo sustancial (≥2 pasos)**: Usar `orchestrate_gentle_task(task_description)` para generar `odd/tasks/<feature>.md` y espejar en Engram en 1 solo paso automático antes de codificar.

2. **Heurística de Tareas (~400 líneas)**:
   - Es una guía orientativa de carga cognitiva por tarea, no un límite duro ni justificación para fragmentaciones forzadas que dañen la cohesión del código.

3. **TDD Observado**:
   - Cuando TDD esté activo, ejecutar y documentar la prueba fallando (RED) antes de implementar el código (GREEN) y refactorizar (REFACTOR). La evidencia debe ser observada en tiempo de ejecución, no meramente narrada.

4. **Doble Persistencia Desacoplada**:
   - Local: `odd/tasks/<feature>.md`
   - Memoria Engram: `odd/<feature>/tasks`

5. **Resolución Interactiva de Incertidumbre**:
   - En el Paso 3 (Resolver Incertidumbre), emplear el sistema nativo de preguntas en el dock de Gentle Shell (hasta 4 preguntas con opciones, selección simple/múltiple y texto libre).

6. **Capa de Revisión Fail-Safe (Gentle-AI v3.7.0)**:
   - Review viene encendido de fábrica por defecto con análisis de riesgo fail-closed.
   - Selección de modelos por revisor (Claude Code, OpenCode, Codex).

## 🛠️ Herramienta Principal de Orquestación
- `orchestrate_gentle_task(task_description, project_name)`:
  **La vía recomendada**: Clasifica la complejidad, recupera decisiones pasadas de memoria y prepara el plan ODD/Engram en **un solo llamado atómico (<10ms)**, sin requerir ping-pongs de herramientas intermedias.
- Herramientas auxiliares de bajo nivel (retrocompatibles): `classify_odd_task`, `prepare_odd_task`, `reconcile_odd_resume`, `orchestrator_session_bridge`.
