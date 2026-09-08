---
tags: [ai, agents, token-optimization, gentleman-programming, architecture, gentle-ai]
categoria: automation-agents
version_actual: "v2.7.0"
ultima_actualizacion: 2026-09-08
---

# ⚡ Gentle-AI & Sub-Agent Orchestration (Ahorro de Tokens del 50-70%)

## ¿Qué es Gentle-AI?
**Gentle-AI** (`Gentleman-Programming/gentle-ai`) es la capa de configuración, orquestación y arnés agnóstico para desarrolladores que utilizan agentes de código (Claude Code, Cursor, OpenCode, Codex, Pi y más). Su principio fundamental es **cero dependencia (no agent lock-in)**: en lugar de imponer una plataforma propietaria, potencia los agentes existentes dotándolos de:
1. **Memoria persistente entre sesiones** (integración nativa con [[Engram (Gentleman Programming Persistent Memory)]]).
2. **Desarrollo Guiado por Especificaciones** ([[Spec-Driven Development (SDD)]] / OpenSpec).
3. **Catálogo de Habilidades Curadas y Servidores MCP** ([[Model Context Protocol (MCP)]]).
4. **Sistema de Personas & Bounded Reviews** (revisiones acotadas sin alucinaciones).

---

## 🎯 Novedades Críticas en la Versión v2.7.0 ("We Count, We Assess, We Ask Less of You")

- **Evaluación Dinámica de Riesgo Previo (`gentle-ai review assess --json`)**:
  - Antes de iniciar cualquier revisión o invocar sub-agentes verificadores, analiza el cambio respondiendo al nivel de cautela requerido con tres niveles tipados: `passive`, `medium` o `high`.
  - Los cambios menores o inofensivos (ej: documentación, refactor cosmético o assets) no pagan el sobrecosto de tokens de un verificador secundario.
  - Los cambios de riesgo medio/alto continúan recibiendo un segundo par de ojos verificador de forma estricta.

- **Composición Nativa de Especificaciones SDD (`gentle-ai sdd-archive-compose`)**:
  - Al cerrar un ciclo SDD, el comando compone y fusiona de forma determinista los deltas de especificación en el documento canónico dentro de `openspec/specs/`, eliminando la necesidad de consolidaciones manuales.

- **Ciclo de Vida de Revisión Resiliente y Sin Puntos Muertos (*No Dead Ends*)**:
  - Si el host de un agente no puede ejecutar un rol de revisor determinado, lo declara formalmente y la revisión continúa en vez de bloquearse.
  - Veredictos de indeterminación mediante campos tipados legibles por máquina en lugar de interpretación heurística de lenguaje natural.
  - Manejo inteligente de renombrado de archivos (evitando que se clasifiquen como reescrituras masivas) y clasificación de archivos binarios como activos pasivos.
  - Capacidad de reanudar revisiones de cambios comiteados tras nuevos commits en el árbol de trabajo.

- **Telemetría Transparente y Anónima**:
  - Medición transparente de instalaciones y latidos diarios con cero PII (sin nombres de archivo, repositorios, usuarios, máquinas ni IPs).
  - Proceso desacoplado en background con presupuesto de 3 segundos que nunca bloquea ni ralentiza comandos del desarrollador.
  - Control total: desactivable en cualquier momento con `gentle-ai telemetry disable` o la variable de entorno `GENTLE_AI_TELEMETRY=0`.

- **Sincronización Desatendida (`gentle-ai sync`)**:
  - Refresca los assets gestionados en los agentes soportados (`~/.pi/`, `.claude/`, etc.), propagando las nuevas reglas de delegación basadas en riesgo.

---

## 🏗️ Patrón de Arquitectura: Sub-Agentes Especializados

### El Problema del Monolito de Contexto
Alimentar a un único agente masivo con todo el contexto, código, reglas y documentación de un proyecto satura rápidamente la ventana de contexto, eleva exponencialmente los costos de tokens y provoca degradación en el razonamiento (*Lost in the Middle*).

### La Solución Gentleman Programming:
```
                    ┌───────────────────────────────┐
                    │ Agente Orquestador / Arquitecto│
                    │  (Contexto liviano, evalúa SDD│
                    │   y despacha micro-tareas)    │
                    └───────────────┬───────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          ▼                         ▼                         ▼
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│ Sub-Agente Plan  │      │ Sub-Agente Code  │      │ Sub-Agente Test  │
│(Lee OpenSpec/DDD)│      │(Solo edita 1 file│      │(Ejecuta TDD con  │
│                  │      │ con diff exacto) │      │ evidencia limpia)│
└──────────────────┘      └──────────────────┘      └──────────────────┘
```

---

## 📊 Beneficios Medidos en DevBrain
1. **Reducción del 50% al 70% en consumo de tokens**: Cada sub-agente recibe únicamente los 500–1,500 tokens estrictamente necesarios para su tarea.
2. **Especialización Radical**: El agente de código no gasta tokens re-planificando ni alucinando tests; el evaluador de tests valida contra contratos BDD.
3. **Determinismo & Verificación Optimizada**: Mayor tasa de éxito en el primer intento siguiendo las directrices de [[Spec-Driven Development (SDD)]] y sin duplicar verificadores en tareas de bajo riesgo.

---

## 🔗 Conexiones en el Grafo DevBrain
- Memoria episódica persistente: [[Engram (Gentleman Programming Persistent Memory)]]
- Arnés para agente Pi: [[Gentle-Pi (Senior Architect Harness para Pi)]]
- Catálogo de habilidades: [[Gentleman-Skills Framework]]
- Metodología de especificaciones: [[Spec-Driven Development (SDD)]]
