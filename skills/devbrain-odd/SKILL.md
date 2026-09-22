---
name: devbrain-odd
description: >-
  Protocolo canónico de Organic Driven Development (ODD) para agentes de software:
  escalamiento orgánico sin burocracia, documento único de feature (odd/tasks/<feature>.md),
  espejo en Engram, ciclo TDD observado (RED->GREEN->REFACTOR) y reanudación resiliente.
---

# DevBrain ODD Skill (Organic Driven Development)

Esta habilidad dota al agente del criterio arquitectónico y la disciplina de ingeniería de **ODD (Gentle-AI v3.0)**.

## Principios Fundamentales
1. **La estructura aparece en proporción a la necesidad**:
   - Peticiones de lectura / explicación: Cero ceremonia, sin artefactos.
   - Cambios pequeños (<2 pasos): Implementar directamente con verificaciones proporcionales.
   - Trabajo sustancial (≥2 pasos): Crear `odd/tasks/<feature-name>.md` y espejar en Engram antes de la primera edición.
2. **Heurística de Tareas (~400 líneas)**:
   - Es una guía orientativa de carga cognitiva por tarea, no un límite duro ni justificación para fragmentaciones forzadas.
3. **TDD Observado**:
   - Cuando TDD esté activo, ejecutar y documentar la prueba fallando (RED) antes de implementar el código (GREEN) y refactorizar (REFACTOR). La evidencia debe ser observada en tiempo de ejecución, no meramente narrada.
4. **Doble Persistencia Desacoplada**:
   - Local: `odd/tasks/<feature>.md`
   - Memoria Engram: `odd/<feature>/tasks`
5. **Resolución Interactiva de Incertidumbre**:
   - En el Paso 3 (Resolver Incertidumbre), emplear el sistema nativo de preguntas en el dock de Gentle Shell (hasta 4 preguntas con opciones, selección simple/múltiple y texto libre, navegables por teclado).
6. **Capa de Revisión Fail-Safe (Gentle-AI v3.5.0)**:
   - Review viene PRENDIDO de fábrica por defecto. El análisis de riesgo es fail-closed: cualquier fallo se evalúa automáticamente como riesgoso/medio-alto. Se apaga solo por comando explícito del usuario (`gentle-ai review mode disable`).

## Herramientas ODD en DevBrain MCP
- `classify_odd_task`: Evalúa deterministamente la naturaleza del pedido.
- `prepare_odd_task`: Genera la estructura formal de la feature y el payload de Engram.
- `reconcile_odd_resume`: Reconcilia el estado entre el disco y Engram ante interrupciones.
- `orchestrator_session_bridge`: Maneja el protocolo de notificaciones inter-sesión en Gentle-Shell.
