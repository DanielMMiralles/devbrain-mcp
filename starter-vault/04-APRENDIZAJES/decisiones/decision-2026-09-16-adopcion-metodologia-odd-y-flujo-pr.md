---
tags: [decision, engram-memory, odd, gentle-ai, gentle-shell, architecture, workflows, tdd]
proyecto: "[[General]]"
fecha: 2026-09-16
---

# 🧠 Decisión / Regla Persistente: Adopcion Metodologia ODD y Flujo Proporcional Gentle AI v3

## Contexto y Aplicabilidad
- Proyecto: [[General]]
- Fecha registrada: 2026-09-16

## Detalle de la Regla o Decisión
### Decisión:
Adoptar formalmente **Organic Driven Development (ODD - Gentle-AI v3.0)** como la metodología estándar por defecto para todos los agentes y proyectos del ecosistema (Antigravity, Cursor, Claude Code, OpenCode, Pi / Gentle-Shell).

### Reglas y Contratos Operativos:
1. **Zero Ceremony para Consultas e Investigación ([READ_ONLY])**:
   - Peticiones de solo lectura, análisis, explicación o revisión técnica NO generan carpetas, tareas ni ceremonias. El agente responde e investiga directamente.

2. **Ejecución Directa para Tareas Pequeñas ([SMALL_DIRECT])**:
   - Cambios de <=1 archivo o alcance acotado (<2 pasos significativos) se implementan de inmediato aplicando verificaciones funcionales proporcionales, sin crear documentos duraderos en disco.

3. **Seguimiento Formal Unificado para Tareas Sustanciales ([SUBSTANTIAL_ODD])**:
   - Para trabajo >=2 pasos o progreso digno de preservación, antes de editar código fuente se genera un único documento canónico odd/tasks/<feature-name>.md espejado en Engram bajo odd/<feature-name>/tasks.
   - Notificación al usuario en una sola línea: '[ODD] Creado odd/tasks/<feature-name>.md con N tareas espejado en Engram.'

4. **Retiro de Burocracia Rígida de SDD y Modo Opt-In**:
   - Se retiran las 108 rutas burocráticas heredadas de SDD. SDD deja de ser el flujo obligatorio y queda como opt-in explícito ([EXPLICIT_SDD]) cuando el usuario pida textualmente 'use SDD'.

5. **Heurística de Tareas (~400 líneas)**:
   - ~400 líneas modificadas por tarea es una guía orientativa de foco cognitivo, NUNCA un límite estricto ni justificación para splits artificiales que dañen la cohesión del código.

6. **TDD Observado y Evidencia en Ejecución**:
   - Si TDD está habilitado (tdd_mode: true), el agente debe observar y registrar evidencia real del ciclo RED -> GREEN -> REFACTOR antes de dar una tarea por completada.

7. **Reanudación Resiliente**:
   - Al retomar una sesión tras interrupciones, el agente debe usar reconcile_odd_resume para alinear el documento local con la memoria persistente de Engram.

## Mandato para Agentes
- Los agentes de IA deben respetar este contrato en todas las sesiones futuras.
