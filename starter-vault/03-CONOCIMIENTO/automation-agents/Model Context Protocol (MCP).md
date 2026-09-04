---
tags: [herramienta, ai, standard, protocol, mcp]
nombre: Model Context Protocol (MCP)
categoria: automation-agents
---

# Model Context Protocol (MCP)

## ¿Qué es?
Estándar abierto creado por Anthropic para conectar asistentes y agentes de IA con sistemas de datos externos, herramientas, repositorios y entornos de ejecución de forma segura y unificada.

## Arquitectura
- **MCP Host**: La aplicación cliente o agente (ej. Claude Desktop, IDE, orquestador).
- **MCP Client**: Mantiene una conexión 1:1 con un servidor MCP.
- **MCP Server**: Expone recursos, herramientas (tools) y prompts mediante JSON-RPC.

## Casos de Uso con [[LangGraph]] y [[FastAPI]]
- Exponer bases de datos [[PostgreSQL]] o flujos de [[n8n]] como herramientas dinámicas para agentes sin hardcodear llamadas de API.
