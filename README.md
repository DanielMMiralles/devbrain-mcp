# 🧠 DevBrain MCP Server

[![MCP Specification](https://img.shields.io/badge/MCP-2024--11--05-blue.svg)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-ready-green.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

**DevBrain** es un servidor unificado de [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) que conecta modelos de inteligencia artificial (Claude, GPT, Gemini, Antigravity, Cursor) con un cerebro de conocimiento en **Obsidian** (~1,675 notas técnicas), un conjunto de herramientas **OpenSpec (Spec-Driven Development)** y un sistema de memoria persistente **Gentle-AI / Engram**.

---

## ✨ Características Principales

- **12 Herramientas MCP Nativas**:
  - `get_project_context`: Lee arquitectura y contexto de proyectos insignia.
  - `list_projects`: Lista proyectos activos con sus stacks tecnológicos.
  - `search_knowledge`: Búsqueda de patrones arquitectónicos y notas de ingeniería.
  - `propose_spec`, `validate_spec`, `get_spec_questions`, `generate_scaffold`: Suite completa SDD/BDD.
  - `remember_decision`, `recall_memory`, `log_learning`: Memoria persistente entre sesiones de IA.
  - `package_project_context`: Empaquetador de código para reducir consumo de tokens en ~80%.
  - `audit_project_health`: Auditoría de dependencias y Dockerfiles.
- **Cero Dependencias de Terceros**: Construido al 100% sobre la biblioteca estándar de Python 3.12.
- **Contenerizado con Docker**: Despliegue con un solo comando o ejecución nativa con Python.
- **Multiplataforma**: Compatible con Windows, macOS y Linux.

---

## 🚀 Inicio Rápido (Quick Start)

### Opción 1: Con Docker (Recomendado)

1. Clona este repositorio:
   ```bash
   git clone https://github.com/DanielMMiralles/devbrain-mcp.git
   cd devbrain-mcp
   ```

2. Configura tu archivo `.env`:
   ```bash
   cp .env.example .env
   # Edita .env con las rutas a tu Obsidian Vault y proyectos locales
   ```

3. Construye y corre la imagen:
   ```bash
   docker compose build
   ```

4. Agrega el servidor a tu cliente MCP favorito (ver [Configuración de Clientes](#-configuracion-de-clientes-mcp)).

---

### Opción 2: Ejecución Local con Python (Sin Docker)

Requisitos: **Python 3.12+** y **Git**.

```bash
# Variables de entorno opcionales (toman valores por defecto si no se indican)
export VAULT_DIR="/ruta/a/tu/Obsidian Vault"
export PROJECTS_DIR="/ruta/a/tus/proyectos"

python src/devbrain_mcp.py
```

---

## 🔌 Configuración de Clientes MCP

### Google Antigravity / Gemini CLI (`mcp_config.json`)
```json
{
  "mcpServers": {
    "devbrain": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v", "C:\\Users\\tu_usuario\\Documents\\Obsidian Vault:/vault",
        "-v", "C:\\Users\\tu_usuario\\Desktop:/projects:ro",
        "devbrain/mcp-server:latest"
      ]
    }
  }
}
```

### Claude Desktop (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "devbrain": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v", "/Users/tu_usuario/Obsidian Vault:/vault",
        "-v", "/Users/tu_usuario/Developer:/projects:ro",
        "devbrain/mcp-server:latest"
      ]
    }
  }
}
```

---

## 🧪 Pruebas Automatizadas

Para validar que el protocolo stdio JSON-RPC responde al 100% de la especificación MCP:

```bash
python tests/test_mcp_stdio.py
```

---

## 📂 Estructura del Repositorio

```
devbrain-mcp/
├── Dockerfile                  # Construccion minimalista Python 3.12 (<60MB)
├── docker-compose.yml          # Orquestacion con volumenes montados
├── mcp_client_config.json      # Plantillas de configuracion para IDEs
├── config/
│   ├── projects.json           # Definicion de proyectos monitoreados
│   └── projects.yaml           # Formato YAML alternativo
├── src/
│   ├── devbrain_mcp.py         # Entrypoint del servidor MCP
│   ├── devspec/                # Suite OpenSpec (BDD, scaffold, preguntas)
│   └── scripts/                # Empaquetador, auditor, daemon, RAG
└── tests/
    └── test_mcp_stdio.py       # Suite de pruebas automatizadas JSON-RPC
```

---

## 📄 Licencia

MIT License — Totalmente de código abierto para compartir y colaborar con la comunidad.
