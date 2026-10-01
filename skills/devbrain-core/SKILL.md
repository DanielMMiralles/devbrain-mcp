---
name: devbrain-core
description: >-
  Capa de abstracción superior sobre Gentle-AI y base de conocimiento (+6,300 notas):
  recuperación instantánea de contexto, optimización AST de tokens, memoria arquitectónica
  Hebbiana y orquestación ágil en 1 solo paso con Gentle-PI y Engram.
---

# DevBrain Core Skill — Capa Cognitiva Superior sobre Gentle-AI

Esta habilidad posiciona a **DevBrain como una capa de abstracción cognitiva superior sobre la suite Gentle-AI**.
DevBrain no reinventa la rueda: delega la ejecución dinámica y las revisiones a Gentle-AI en el fondo, mientras aporta memoria profunda, compresión y conocimiento instantáneo.

## 🎯 Principio Rector: Acción Directa y Cero Burocracia
- **Gentle-AI como Motor de Ejecución**: Si el usuario pide un cambio claro, un bugfix o una explicación puntual, **actúa directamente** con las herramientas nativas de edición y ejecución. No invoques pasos burocráticos ni intermediarios innecesarios.
- **Sin Reingeniería**: No reinventes lo que Gentle-AI ya hace nativamente (revisión RDD, pipelines SDD, runner de tests, preguntas en dock). DevBrain provee la inteligencia y el contexto que alimentan a Gentle-AI.

## 🧠 Cuándo invocar a DevBrain (Bajo Demanda)
Invoca las herramientas de DevBrain únicamente cuando necesites una capacidad cognitiva especializada:

1. **Contexto Arquitectónico Inmediato (<20ms)**:
   - `get_project_context(project_name)`: Carga el 360° del proyecto (README, arquitectura, grafo AST y dependencias) sin buscar manualmente.
   - `search_knowledge(query)`: Consulta las 6,307 notas del Vault Obsidian, patrones GoF, DDD táctico y gotchas de producción potenciados por neuroplasticidad de Hebb.

2. **Ahorro Extremo de Tokens (-80% a -90%)**:
   - `optimize_token_budget(target_text, max_tokens)`: Aplica AST Code Slicing (poda cuerpos internos manteniendo firmas e interfaces) antes de cargar archivos voluminosos al prompt.

3. **Memoria y Decisiones Persistentes**:
   - `recall_memory(query)`: Consulta acuerdos previos para no contradecir decisiones de arquitectura.
   - `remember_decision(title, details, project)`: Registra directrices o reglas que deben sobrevivir a reinicios de contexto (espejadas en SQLite, Engram y Vault).

4. **Orquestación en 1 Solo Paso (`orchestrate_gentle_task`)**:
   - Para tareas mayores, multi-fase o con necesidad de espejo en Engram:
     Invoca `orchestrate_gentle_task(task_description, project_name)`.
     DevBrain clasifica, prepara el plan ODD/SDD y sincroniza con Engram **en 1 sola llamada local (<10ms)**, devolviéndote la directiva lista para codificar de inmediato sin ceremonias ni ping-pongs de 5 turnos.

5. **Salud del Grafo y Auto-Mantenimiento**:
   - `audit_cortex_health()`: Audita enlaces rotos con auto-reparación en 1-clic y poda sináptica.

## 🛡️ Capa de Revisión y Resiliencia (Gentle-AI v3.7.0)
- Review (RDD) viene encendido de fábrica por defecto con análisis de riesgo fail-safe.
- Selección de modelos por revisor (Per-Reviewer Model Selection) para balancear costo y profundidad.
- Totalmente compatible con `gentle-shell --link` y workspaces aislados.
