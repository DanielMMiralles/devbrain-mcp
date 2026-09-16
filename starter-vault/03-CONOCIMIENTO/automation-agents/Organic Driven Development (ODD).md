---
title: Organic Driven Development (ODD)
category: automation-agents
tags: [ai, agents, odd, gentle-ai, engram, workflows, software-engineering, tdd]
status: canonical
created: 2026-09-16
version: 3.0.0
---

# Organic Driven Development (ODD)

> **"La estructura aparece en proporción a la necesidad. Nunca más, nunca menos. Por eso organic: los procesos no se imponen, emergen."** — *Alan Buscaglia (Gentle-AI v3.0)*

## 1. El Cambio de Paradigma: Adiós a la Burocracia de Admisión
Durante las versiones 2.x de Gentle-AI, **Spec-Driven Development (SDD)** acumuló una sobrecarga procedimental considerable:
- Investigaciones obligatorias como "trámite de admisión".
- Múltiples artefactos fragmentados (`proposal.md`, `spec.md`, `design.md`, `tasks.md`, `verification.md`).
- Attestations y formalismos previos para archivar o comenzar cambios triviales.

**Gentle-AI v3.0** retira **108 rutas burocráticas** de SDD y establece **Organic Driven Development (ODD)** como el flujo de desarrollo predeterminado para todos los agentes del ecosistema (Pi, OpenCode, Claude Code, Cursor, Antigravity, etc.). 

SDD no desaparece: **sigue disponible de forma simplificada y liviana** para cuando el desarrollador elija explícitamente (`use SDD`), pero ya no es la puerta de entrada obligatoria. La puerta de entrada es la ausencia de fricción.

```
┌───────────────────────────────────────────────────────────┐
│                    PETICIÓN DEL USUARIO                   │
└─────────────────────────────┬─────────────────────────────┘
                              ▼
                ¿Autoriza cambios de código?
               /                            \
             NO                              SÍ
             ▼                               ▼
    [READ_ONLY]                    Explorar código existente
   Cero ceremonia.                           │
  Explicar / indagar.                        ▼
                            ¿Trabajo sustancial (≥ 2 pasos)?
                           /                                \
                         NO                                  SÍ
                         ▼                                   ▼
                  [SMALL_DIRECT]                      [SUBSTANTIAL_ODD]
              Ejecutar directamente              Crear `odd/tasks/<feature>.md`
              con checks funcionales.           y espejar en Engram antes
                                                 de la primera edición.
```

---

## 2. El Protocolo ODD en 7 Pasos

1. **Autorizar**: Determinar si la solicitud autoriza cambios reales en el código. Las peticiones de lectura, consulta, investigación o documentación se resuelven sin crear carpetas, tareas ni ceremonias.
2. **Explorar**: Inspeccionar el código y los requisitos de forma estrictamente proporcional a la petición.
3. **Resolver Incertidumbre**: Si hay dudas técnicas o dependencias externas, realizar una investigación acotada. Si hay una decisión de producto no resuelta, hacer **una sola pregunta enfocada** con stop/wait. Para premisas de alto riesgo no comprobadas, emitir a lo sumo un desafío crítico independiente.
4. **Clasificar**: 
   - *Trabajo pequeño / entendido* (< 2 pasos significativos): Se ejecuta directamente.
   - *Trabajo sustancial* (≥ 2 pasos significativos o progreso digno de preservación): Requiere seguimiento formal con documento de feature.
5. **Rastrear antes del primer cambio**: Crear el documento canónico `odd/tasks/<feature-name>.md` y su espejo en Engram `odd/<feature-name>/tasks` antes de escribir la primera línea de código fuente. Notificar al usuario en una sola línea:
   ```text
   [ODD] Creado odd/tasks/<feature-name>.md con N tareas espejado en Engram.
   ```
6. **Implementar tarea por tarea**:
   - Guiarse por la **heurística orientativa de ~400 líneas** (adiciones + supresiones) por tarea como tamaño cognitivo aconsejable (no como regla rígida ni pretexto para fragmentaciones artificiales).
   - Aplicar el modo **TDD configurado**:
     - *TDD ON*: Requiere ciclo observado **RED** (test fallando antes de implementar) → **GREEN** (test pasando) → **REFACTOR**.
     - *TDD OFF*: Ejecutar comprobaciones funcionales y suites de tests existentes.
   - Marcar checkboxes únicamente con pruebas observadas en tiempo de ejecución.
7. **Cerrar**: Reportar el resultado verificado con honestidad, indicando comprobaciones pendientes o fallidas y el siguiente paso sugerido.

---

## 3. Estructura Canónica del Documento ODD (`odd/tasks/<feature>.md`)

```markdown
# Feature: <Nombre Descriptivo>
- **Project**: [[<Proyecto>]]
- **Created**: YYYY-MM-DD HH:MM:SS
- **Status**: in-progress
- **Workflow**: Organic Driven Development (ODD - Gentle-AI v3.0)
- **TDD Mode**: ENABLED (Observed RED -> GREEN -> REFACTOR) | DISABLED
- **Test Runner**: <pytest | pnpm test | npm test | cargo test>
- **Engram Mirror Locator**: `odd/<feature-name>/tasks`

## 🎯 Objective & Problem
Justificación del cambio y problema concreto a resolver.

## 🛡️ Scope & Constraints
Límites explícitos, archivos o subsistemas fuera de alcance.

## 📋 Actionable Tasks
- [ ] [TASK-01] Tarea inicial atómica (~400 líneas)
- [ ] [TASK-02] Tarea secundaria coherente

## ✅ Acceptance Criteria & Invariants
- [ ] Criterio verificable 1
- [ ] Sin regresiones en pruebas existentes

## 🔬 Verification Evidence
- [TASK-01]: Test output observado: 12 passed in 0.4s.

## ⏭️ Progress & Next Step
- Current: Initialized
- Next: Iniciar TASK-01.
```

---

## 4. Reconciliación y Resilencia ante Interrupciones

Uno de los mayores dolores en agentes autónomos es la pérdida de contexto tras compactación de memoria o desconexión de sesión.
ODD resuelve esto mediante **doble almacenamiento desacoplado**:
1. **Archivo físico**: `odd/tasks/<feature>.md` (controlado por git en el proyecto).
2. **Memoria de agente**: Tópico Engram `odd/<feature>/tasks`.

Al reanudar una sesión (`reconcile_odd_resume`), el orquestador:
- Lee ambas fuentes simultáneamente.
- Detecta divergencias (por ejemplo, tareas marcadas como completadas en Engram pero no en disco).
- Preserva el progreso validado sin sobrescrituras destructivas.
- Reanuda en la primera tarea pendiente verificable.

---

## 5. Composabilidad de Capas: ODD + SDD + RDD

| Capa | Estado por Defecto | Activación | Propósito |
| :--- | :--- | :--- | :--- |
| **ODD** | **Activo (Por defecto)** | Automático en todas las peticiones | Flujo adaptativo continuo con cero fricción. |
| **SDD** | Opcional | "use SDD" o propuesta formal | Especificación multipartes (spec, design, tasks). |
| **Review / RDD** | Opcional | `gentle-ai review mode enable` | Árbitros independientes y evaluación formal de riesgos. |

---

## 6. Conexiones Neuronales en el Grafo DevBrain
- [[Gentle-Shell (Workspace & Multi-Orchestrator)]] — Entorno de ejecución en Pi para ODD.
- [[Engram (Gentle-AI Persistent Memory)]] — Espejo de persistencia para tareas y decisiones.
- [[Spec-Driven Development (SDD)]] — Metodología previa ahora integrada como rama opcional.
- [[Clean Architecture & Puertos y Adaptadores]] — Invariantes de diseño que ODD protege.
- [[Test Driven Development (TDD)]] — Protocolo RED-GREEN-REFACTOR integrado en ODD.
