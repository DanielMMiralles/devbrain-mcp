---
tags: [ai, agents, token-optimization, gentleman-programming, architecture]
categoria: automation-agents
---
# ⚡ Gentle-AI & Sub-Agent Orchestration (Ahorro de Tokens del 50-70%)

## El Problema del Monolito de Contexto
Alimentar a un único agente masivo con todo el contexto, código, reglas y documentación de un proyecto satura rápidamente la ventana de contexto, eleva los costos de tokens por las nubes y provoca degradación en la calidad del razonamiento (*Lost in the Middle*).

## La Solución de Gentleman Programming: Orquestación por Sub-Agentes
Inspirada en el ecosistema `Gentleman-Programming/gentle-ai` y `pi-gentle-subagents`:

```
                    [Agente Orquestador / Arquitecto]
                     (Contexto liviano, toma decisiones)
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
[Sub-Agente Planner]      [Sub-Agente Coder]        [Sub-Agente Tester]
(Lee OpenSpec & DDD)     (Solo edita 1 archivo)     (Corre tests unitarios)
```

## Beneficios Medidos
1. **Reducción del 50% al 70% en consumo de tokens**: Cada sub-agente recibe únicamente los 500-1,000 tokens de contexto indispensables para su subtarea.
2. **Especialización**: El sub-agente de tests no alucina con la base de datos; el sub-agente de código no gasta tokens reescribiendo la especificación.
3. **Determinismo**: Mayor tasa de éxito en la primera pasada siguiendo [[Spec-Driven Development (SDD)]].
