---
tags: [ai, agents, memory, engram, gentleman-programming, mcp]
categoria: automation-agents
---
# 🧠 Engram (Persistent Memory para Agentes de IA)

## ¿Qué es?
Herramienta de código abierto desarrollada por **Gentleman Programming** (`Gentleman-Programming/engram`). Es un binario autónomo escrito en Go con base de datos SQLite embebida y búsqueda de texto completo **FTS5**, que provee memoria de largo plazo agnóstica para agentes de IA.

## Capacidades Clave
- **Memoria entre Sesiones**: Permite que agentes como Claude Code, Cursor, OpenCode o Antigravity recuerden decisiones arquitectónicas, bugs resueltos y contexto del proyecto sin requerir re-explicarlo.
- **Servidor MCP Nativo**: Expone herramientas de memoria (`remember`, `recall`, `search_memory`) vía [[Model Context Protocol (MCP)]].
- **Ahorro Radical de Tokens**: En lugar de cargar todo el historial o archivos gigantescos en la ventana de contexto, el agente consulta a Engram únicamente los fragmentos relevantes mediante FTS5.

## Conexión con DevBrain
- DevBrain actúa como la **base de conocimiento ontológica (la biblioteca)**, mientras que Engram actúa como la **memoria episódica rápida de trabajo (el cuaderno de notas del agente)**.
