---
tags: [ai, agents, skills, gentleman-programming, best-practices]
categoria: automation-agents
---
# 🎯 Gentleman-Skills Framework

## ¿Qué es?
Repositorio comunitario (`Gentleman-Programming/Gentleman-Skills`) que cataloga habilidades, prompts de sistema especializados y patrones de interacción para asistentes y agentes de código (Claude Code, OpenCode, Antigravity).

## Patrones Incorporados
- **Senior Architect Persona**: El agente actúa con mentalidad de ingeniero senior: cuestiona requerimientos ambiguos, exige contratos BDD previos y rechaza parches temporales.
- **SDD Enforcement**: Bloqueo estricto que prohíbe al agente escribir código de producción hasta que el `spec.md` y las tareas en `tasks.md` estén aprobados por el desarrollador.
- **Fail-Fast Error Handling**: Pautas para que el agente diagnostique la causa raíz en lugar de aplicar parches cosméticos que oculten el problema.
