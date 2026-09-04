---
tags: [skill, sdd, openspec, workflow]
nombre: Spec-Driven Development (SDD)
categoria: practicas-desarrollo
---

# 📐 Spec-Driven Development (SDD)

## ¿Qué es?
Metodología de ingeniería de software donde la especificación no es un documento pasivo, sino la **fuente de verdad viva** que guía tanto a los desarrolladores como a los agentes de IA (Antigravity, Claude Code, Cursor).

## El Ciclo de 3 Pasos
1. **Propose (Proponer)**: Redactar la intención en `[[proposal]].md`, los contratos BDD en `[[spec]].md`, la arquitectura en `[[design]].md` y las tareas en `[[tasks]].md`.
2. **Apply (Ejecutar)**: El agente de IA implementa el código verificando cada tarea contra el contrato BDD.
3. **Archive (Consolidar)**: La especificación pasa al registro permanente del proyecto una vez que los tests aprueban.

## Regla de Oro
> *Si el comportamiento observable cambia sin que la [[spec]] haya sido actualizada primero, la implementación se considera defectuosa.*
