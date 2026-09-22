---
name: devbrain-core
description: >-
  Acceso y navegación por el ecosistema DevBrain: consulta de la base de conocimiento
  (+1,600 notas técnicas), recuperación de contexto de proyectos insignia,
  empaquetado de contexto y orquestación con Organic Driven Development (ODD) y Gentle-Shell.
---

# DevBrain Core Skill

Esta habilidad conecta a los agentes con el segundo cerebro de desarrollo (DevBrain).

## Cuándo usar esta habilidad
- Al iniciar el trabajo en cualquiera de los proyectos insignia: Chambita-Ecosystem, AliaLog-System, Narval-SGN, Alia-IMA-LangGraph, Mayan-EDMS, Odysseus, AlaOrden-Web.
- Para buscar patrones GoF, principios de diseño cloud, DDD táctico o lecciones aprendidas en `03-CONOCIMIENTO`.
- Para clasificar y ejecutar tareas bajo el protocolo **ODD (Organic Driven Development)**.
- Para reanudar sesiones interrumpidas reconciliando el documento local con la memoria de Engram (`reconcile_odd_resume`).
- Para generar especificaciones formales OpenSpec/SDD únicamente cuando se solicite explícitamente (`use SDD`).

## Flujo Operativo Estándar (ODD First)
1. **Recuperar Contexto**: Invocar `get_project_context(project_name)` para cargar el README y arquitectura del proyecto.
2. **Consultar Decisiones Previas**: Usar `recall_memory(query)` para no contradecir decisiones arquitectónicas ya acordadas.
3. **Clasificar el Requerimiento**:
   - Usar `classify_odd_task(request_description)` para determinar si es `READ_ONLY`, `SMALL_DIRECT` o `SUBSTANTIAL_ODD`.
   - Si es consulta o documentación: responder directamente sin crear artefactos de tareas (cero ceremonia).
   - Si es cambio pequeño (<2 pasos): implementar directamente con checks funcionales.
   - Si es trabajo sustancial (≥2 pasos): generar `prepare_odd_task(feature_name, objective, tasks)` antes de la primera edición de código.
   - En resolución de incertidumbre (Paso 3 ODD): utilizar el sistema interactivo de preguntas en el dock de Gentle Shell (hasta 4 preguntas navegables por teclado).
4. **Modo TDD Observado**: Si TDD está activo, exigir el ciclo estricto RED → GREEN → REFACTOR en ejecución real (no narrado).
5. **Reanudación / Recuperación**: Ante interrupciones o reinicios de contexto, invocar `reconcile_odd_resume(feature_name)` para sincronizar `odd/tasks/<feature>.md` con Engram.
6. **Flujo SDD Opcional**: Usar `propose_spec` / `prepare_sdd_preflight` solo si el usuario pide explícitamente "use SDD".
7. **Empaquetar Contexto**: Al depurar código complejo, usar `package_project_context(project_name)` para obtener una vista condensada sin sobrecargar tokens.
8. **Capa de Revisión (Gentle-AI v3.5.0)**: Review (RDD) viene PRENDIDO de fábrica por defecto con análisis de riesgo fail-safe (los fallos de evaluación se consideran de alto riesgo). Solo el usuario puede desactivarlo (`gentle-ai review mode disable`).
