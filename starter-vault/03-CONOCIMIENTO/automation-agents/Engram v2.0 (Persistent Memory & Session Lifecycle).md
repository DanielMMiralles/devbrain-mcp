---
title: Engram v2.0 (Persistent Memory & Session Lifecycle)
category: automation-agents
tags: [ai, agents, engram, memory, context, gentle-ai, session-lifecycle]
status: canonical
created: 2026-09-16
version: 2.0.0-rc.12
---

# Engram v2.0 (Persistent Memory & Session Lifecycle)

> **"El coste de una nueva sesión no son los tokens: eres tú, re-explicando las mismas decisiones cada mañana. Engram elimina eso: tu agente escribe lo que aprende y lo consulta antes de preguntarte."** — *Gentle-AI & Engram Documentation*

## 1. Novedades Clave en Engram v2.0.0-rc.12
La versión candidata **v2.0.0-rc.12** (`Gentleman-Programming/engram`) introduce mejoras críticas de estabilidad y arquitectura:
1. **Mayor Integridad en Sincronización**: Resilencia contra corrupción de observaciones y verificación estricta de hash de contenido.
2. **Ciclos de Vida de Agentes y Sesiones más Confiables**: Control robusto del estado de subagentes huérfanos o interrumpidos.
3. **Mejor Manejo de Procesos en Windows**: Soporte nativo para spawn, señales y terminación limpia de procesos daemon y sockets stdio bajo Win32/PowerShell.
4. **Seguridad Reforzada**: Cifrado y validación en transporte de datos Cloud y contratos de CLI/MCP/plugins.
5. **Normalización Automática de Proyectos**: Auto-detección desde git remote en lowercase para evitar dispersión de nombres ("mi-repo" vs "Mi-Repo").

---

## 2. Integración Canónica con ODD (Organic Driven Development)
Bajo el protocolo ODD de Gentle-AI v3.0, Engram actúa como el respaldo gemelo de cada feature sustancial:
- **Tópico de Proyecto**: `odd/<feature-name>/tasks`
- **Contenido**: Copia exacta y completa del documento local `odd/tasks/<feature-name>.md` junto con su localizador de archivo en disco.
- **Resilencia ante Compactación**: Si la ventana de contexto del LLM se reinicia o satura, el orquestador lee la observación en Engram y reanuda sin perder tareas ya verificadas.

---

## 3. Comandos Esenciales de Engram CLI

| Comando | Cuándo Utilizarlo |
| :--- | :--- |
| `engram tui` | Explorar memorias de forma interactiva con filtros y búsqueda FTS. |
| `engram sync` | Exportar la memoria viva del proyecto a la carpeta versionable `.engram/` en Git. |
| `engram sync --import` | Importar recuerdos históricos al clonar un repositorio en una nueva máquina. |
| `engram projects list` | Ver todos los proyectos con recuento de observaciones. |
| `engram projects consolidate` | Corregir dispersión de nombres de proyecto redundantes. |
| `engram search <query>` | Búsqueda ultrarrápida desde la terminal sin abrir interfaz gráfica. |

---

## 4. Conexiones Neuronales en el Grafo DevBrain
- [[Organic Driven Development (ODD)]] — Protocolo diario que almacena el progreso de features en Engram.
- [[Gentle-Shell (Workspace & Multi-Orchestrator)]] — Entorno de ejecución en Pi que interactúa con las herramientas MCP de memoria.
- [[Spec-Driven Development (SDD)]] — Gestión de memorias para especificaciones de arquitectura.
