---
tags: [ai, agents, memory, engram, gentleman-programming, mcp, sqlite, fts5]
categoria: automation-agents
version_actual: "v1.20.0"
ultima_actualizacion: 2026-09-07
---

# 🧠 Engram (Persistent Memory System para Agentes de IA)

## ¿Qué es Engram?
**Engram** (`Gentleman-Programming/engram`) es un sistema de memoria persistente de largo plazo, agnóstico al agente, desarrollado en **Go**. Funciona como un binario autónomo ultraligero que utiliza **SQLite embebido** con búsqueda de texto completo **FTS5** y ordenamiento ponderado **BM25**, proveyendo almacenamiento y recuperación inmediata de contexto episódico para agentes de código.

---

## 🚀 Capacidades y Novedades en la Versión v1.20.0

- **Ranking Ponderado BM25**: Sustitución del algoritmo por defecto de FTS5 por un ranking BM25 con pesos de relevancia, asegurando que las directrices más afines a la tarea actual aparezcan en los primeros resultados.
- **Project Override en Resúmenes (`mem_session_summary`)**: Posibilidad de aislar o redefinir el proyecto de la sesión en curso, permitiendo memorias compartidas entre microservicios o estrictamente privadas por repositorio.
- **TUI & Cloud Settings**: Interfaz en terminal enriquecida con pantalla de configuración de sincronización en la nube y confirmación de borrado seguro de sesiones.
- **Sanitización Robusta FTS5**: Escape automático de comillas internas en consultas de texto, eliminando fallos y excepciones por sintaxis inválida.
- **Deduplicación de Observaciones**: Mecanismo de importación idempotente que descarta duplicados en ingestas masivas de contexto.
- **Resiliencia con Pi & Agentes de Código**: Autorecuperación de la línea de estado (*statusline*) ante reinicios o desconexiones temporales de sesión.

---

## 🛠️ Modos de Interacción

1. **Servidor MCP Nativo (`engram serve`)**:
   - Expone herramientas estándar de memoria para clientes compatibles con [[Model Context Protocol (MCP)]] (`remember`, `recall`, `search_memory`, `mem_session_summary`).
2. **Línea de Comandos (CLI)**:
   - `engram save`: Almacena un recuerdo manual o directriz.
   - `engram search <query>`: Recupera notas mediante búsqueda BM25 en terminal.
   - `engram context`: Vuelca el contexto reciente para inyección rápida en prompts.
3. **HTTP API Rest**:
   - Endpoints para lectura y escritura desde scripts, extensiones o hooks de Git.
4. **TUI Interactiva**:
   - Visualizador de recuerdos, filtros por proyecto y métricas de almacenamiento.

---

## 🏛️ Rol en la Arquitectura DevBrain
- **DevBrain (Obsidian)** = **Base de Conocimiento Ontológica / Biblioteca Estructurada**: Contiene arquitectura, patrones GoF, Domain-Driven Design y documentación formal.
- **Engram** = **Memoria Episódica Rápida / Cuaderno de Bitácora del Agente**: Recuerda decisiones tácticas tomadas hace 5 minutos o hace 3 semanas, bugs esquivados y directrices del usuario sin saturar la ventana de contexto.

---

## 🔗 Conexiones en el Grafo DevBrain
- Capa de orquestación: [[Gentle-AI & Sub-Agent Orchestration (Token Saving)]]
- Arnés de ejecución: [[Gentle-Pi (Senior Architect Harness para Pi)]]
- Protocolo de herramientas: [[Model Context Protocol (MCP)]]
