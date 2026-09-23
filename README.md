# 🧠 DevBrain MCP Server

[![MCP Specification](https://img.shields.io/badge/MCP-2024--11--05-blue.svg)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-ready-green.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

**DevBrain** es un servidor unificado de [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) que conecta modelos de inteligencia artificial (Claude, GPT, Gemini, Antigravity, Cursor) con un cerebro de conocimiento en **Obsidian** (~1,675 notas técnicas), un conjunto de herramientas **OpenSpec (Spec-Driven Development)** y un sistema de memoria persistente **Gentle-AI / Engram**.

---

## ✨ Características Principales

- **Arquitectura PLC Neuroplástica (DevBrain v3.0)**:
  - **PLC Router (`src/plc_router.py`)**: Controlador de ultra-baja latencia (<5ms) que resuelve lecturas in-process (fast path) y delega tareas pesadas de orquestación y subagentes a Gentle-PI/Shell.
  - **Grafo Sináptico Dinámico (`src/neuroplasticity.py`)**: Motor de plasticidad biológica (Hebb, LTP, LTD, poda sináptica). Conecta conceptos adaptativamente según co-activación en sesiones reales y potencia el reranking con un Synaptic Bonus.
- **21 Herramientas MCP Nativas (DevBrain v3.0 - PLC & ODD)**:
  - `classify_odd_task`: Clasificación determinista según protocolo ODD con activación contextual neuroplástica.
  - `prepare_odd_task`: Generación del documento `odd/tasks/<feature>.md` y su espejo Engram `odd/<feature>/tasks`.
  - `reconcile_odd_resume`: Reconciliación de estado local vs memoria Engram al reanudar sesiones.
  - `orchestrator_session_bridge`: Soporte para el protocolo de mensajería inter-sesión de Gentle-Shell con semántica ACK.
  - `prepare_sdd_preflight`: Contrato SDD liviano (Gentle-AI v3.0).
  - `get_project_context`, `list_projects`, `search_knowledge`: Navegación ontológica y catálogo de conocimiento con indexador FTS5.
  - `propose_spec`, `validate_spec`, `get_spec_questions`, `generate_scaffold`: Suite completa SDD/BDD (OpenSpec).
  - `remember_decision`, `recall_memory`: Memoria persistente y lecciones aprendidas (Gentle-AI / Engram v2).
  - `package_project_context`, `audit_project_health`: Empaquetado ultracompacto y auditoría de salud.
  - `debate_project_feasibility`: Modo Debate Sin Filtros (Red Team) para estresar viabilidad y costos ocultos.
  - `audit_ponytail_complexity`: Auditoría de simplicidad y poda de sobre-ingeniería según la escalera YAGNI.
  - `query_code_graph`, `sync_project_graph`: Motor AST Graphify para extraer relaciones de símbolos y dependencias.
  - `route_model_dispatch`: Gateway inteligente multi-modelo (FAST vs FRONTIER vs CODER) con soporte OmniRoute.
- **Resolución Resiliente de Vault**: Soporta indistintamente `VAULT_PATH` o `VAULT_DIR`, lectura automática de `.env` y fallback instantáneo a `./starter-vault` (100% plug-and-play).
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

### Opción 3: Daemon de Aprendizaje en Segundo Plano (Opcional)

Si deseas que el observador monitoree automáticamente tus repositorios Git locales y registre commits y decisiones en tu Vault de Obsidian:

```powershell
# Instalar como tarea programada en segundo plano (Windows)
powershell -ExecutionPolicy Bypass -File src/scripts/install_daemon_service.ps1 -Action install

# Para desinstalar cuando lo desees:
powershell -ExecutionPolicy Bypass -File src/scripts/install_daemon_service.ps1 -Action uninstall
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

## 📜 Protocolos Operativos del Agente (`docs/protocols/`)

DevBrain no solo provee herramientas pasivas, sino protocolos de conducta e ingeniería para agentes de IA:

1. **[Protocolo de Debate Sin Filtros](docs/protocols/protocolo_debate_redteam.md)**:
   - Activa el rol de *Principal Systems Architect / Red Team Auditor*.
   - Suspende el sesgo de complacencia (*sycophancy*) y somete cualquier propuesta al test de las 5 preguntas de fuego (SPOF, costos ocultos, mantenimiento a las 3 AM).
2. **[Reglas Ponytail (Lazy Senior Dev)](docs/protocols/ponytail_rules.md)**:
   - Escalera de 6 peldaños YAGNI para forzar la simplificación radical: ¿Tiene que existir? -> ¿Existe ya? -> ¿Standard Lib? -> ¿Nativo? -> ¿Una sola línea?
3. **[Protocolo de Ingesta Tecnológica (DIP)](docs/protocols/protocolo_ingesta_tecnologica.md)**:
   - Pipeline de 4 fases para evaluar repos de GitHub, librerías o paradigmas modernos, destilarlos en fichas atómicas para el Vault y activarlos en proyectos reales sin acumular deuda técnica.

---

## 🖥️ DevBrain Native CLI & Cognitive HUD (Estilo Gentle-Shell)

DevBrain incluye ahora un **CLI nativo interactivo** y un **HUD de Telemetría Cognitiva en Tiempo Real** para inspeccionar exactamente cómo piensa el agente, cómo orquesta las tareas y qué recursos consume:

```bash
# Iniciar el HUD de telemetría cognitiva en vivo (60fps)
devbrain live

# Iniciar la terminal interactiva con autocompletado y dock questions
devbrain shell

# Ver resumen de métricas acumuladas (tokens, costos USD, p50/p95, herramientas)
devbrain stats

# Diagnóstico de salud del ecosistema (Python, FTS5, Engram, Gentle-PI, Vault)
devbrain doctor

# Consultas directas al cerebro con reranking sináptico
devbrain search "organic driven development"

# Cambiar paleta visual o alternar Modo Papa (ahorro de batería / minimalista)
devbrain theme cyberpunk
devbrain papa

# Manual completo interactivo y guías especializadas por tópico
devbrain help
devbrain help live      # Ayuda profunda sobre el HUD y paneles
devbrain help odd       # Guía de clasificación ODD y fail-safe
devbrain help mcp       # Catálogo de las 21 herramientas y rutas PLC
devbrain help hosts     # Guía de conexión para Antigravity, Cursor y Claude
devbrain help neuro     # Fórmulas de Hebb, LTP/LTD y bonus sináptico
```

### 📊 Indicadores en Vivo ("¿Cómo Piensa?")
- **Consumo de Tokens & Costos**: Desglose `Tokens In` / `Out` / `Total`, Throughput (`tok/s`), Costo acumulado en USD por modelo (Gemini 3.8 Flash, Claude 3.5/Sonnet, GPT-5, etc.).
- **Latencias de Respuesta**: Medición en tiempo real de latencia mediana ($p50$) y de cola ($p95$).
- **Corteza Sináptica Hebbiana**: Visualización de sinapsis activas disparadas por co-activación contextual en la sesión.
- **Rastro de Razonamiento del PLC**: Exposición de la traza de pensamiento y decisión del PLC Router (`LOCAL_FAST`, `DELEGATE`, `ORCHESTRATE`).
- **Carril de Orquestación Ecosistémico**: Integración visual de pipeline con **Gentle-PI** y **Engram v2.0**.
- **Personalización Visual**: Temas `Gentleman-Dark`, `Cyberpunk`, `Obsidian-Dark`, `Monokai` y `Modo Papa` austero.

### 🔌 Conexión con Hosts e IDEs (Antigravity, Cursor, Claude Code)
El CLI de DevBrain opera de forma **completamente desacoplada** a través de un bus de eventos atómico (`~/.devbrain/live_events.jsonl` y `session_stats.json`):
- **Antigravity (AGY)**: Detecta automáticamente el entorno AGY vía handshake de inicialización MCP o variables de entorno. Puedes tener tu agente trabajando en AGY mientras mantienes una terminal abierta al lado con `devbrain live` viendo cada tool call en tiempo real.
- **Cursor IDE**: Detecta sesiones de Cursor mediante variables de traza y el cliente MCP de Cursor. El HUD refleja inmediatamente las consultas que Cursor delega a DevBrain.
- **Claude Code**: Conexión nativa vía configuración en `claude_desktop_config.json` o subproceso stdio.

---

## 📂 Estructura del Repositorio

```
devbrain-mcp/
├── devbrain.cmd                # Launcher Windows CMD para terminal global
├── devbrain.ps1                # Launcher Windows PowerShell
├── Dockerfile                  # Construccion minimalista Python 3.12 (<60MB)
├── docker-compose.yml          # Orquestacion con volumenes montados
├── mcp_client_config.json      # Plantillas de configuracion para IDEs
├── docs/
│   └── protocols/              # Protocolos operativos (Debate, Ponytail, Ingesta)
├── skills/                     # Catalogo de Agent Skills (Core, ODD, Debate, Ponytail)
├── config/
│   ├── projects.json           # Definicion de proyectos monitoreados
│   └── projects.yaml           # Formato YAML alternativo
├── src/
│   ├── devbrain_cli.py         # Entrypoint del CLI unificado ('devbrain')
│   ├── cli_help.py             # Sistema de ayuda y manual interactivo con temas
│   ├── cli_hud.py              # Dashboard TUI en vivo con Rich (Cognitive HUD)
│   ├── cli_shell.py            # Terminal interactiva REPL con prompt-toolkit
│   ├── cli_theme.py            # Motor de temas visuales y Modo Papa
│   ├── telemetry.py            # Event Bus, cálculo de tokens/costos y métricas p50/p95
│   ├── devbrain_mcp.py         # Servidor MCP stdio (21 herramientas integradas)
│   ├── plc_router.py           # PLC Router (fast-path local vs Gentle-PI)
│   ├── neuroplasticity.py      # Motor de plasticidad sináptica (LTP/LTD Hebb)
│   ├── devbrain_index.py       # Motor de búsqueda FTS5 y reranking híbrido
│   ├── devspec/                # Suite OpenSpec (BDD, scaffold, preguntas)
│   └── scripts/                # Motores de debate, graphify, model hub, packager, daemon
├── starter-vault/              # Plantilla inicial de Obsidian Vault lista para usar
└── tests/
    ├── test_cli_telemetry.py   # Tests de telemetría, temas y renderizado HUD
    ├── test_neuroplasticity.py # Tests de plasticidad sináptica y PLC Router
    ├── test_odd_mcp.py         # Tests de herramientas ODD y contratos de sesión
    └── test_mcp_stdio.py       # Suite de pruebas automatizadas JSON-RPC stdio
```

---

## 📄 Licencia

MIT License — Totalmente de código abierto para compartir y colaborar con la comunidad.

