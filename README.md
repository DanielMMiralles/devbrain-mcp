# 🧠 DevBrain MCP Server (v3.7.0)

[![MCP Specification](https://img.shields.io/badge/MCP-2024--11--05-blue.svg)](https://modelcontextprotocol.io/)
[![Version](https://img.shields.io/badge/version-3.7.0-brightgreen.svg)](https://github.com/DanielMMiralles/devbrain-mcp)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Gentle-AI](https://img.shields.io/badge/gentle--ai-3.7.0%20%7C%204.5.1-purple.svg)](https://github.com/Gentleman-Programming/gentle-ai)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

**DevBrain** es un servidor unificado de [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) que actúa como un **Sistema Operativo Cognitivo, Controlador Lógico Programable (PLC) y Capa de Abstracción Superior sobre Gentle-AI**. Conecta modelos de IA con un cerebro de conocimiento en **Obsidian** (+6,350 notas técnicas), memoria Hebbiana neuroplástica, cuadro de mando ejecutivo vivo (**Portada**), motor de **Razonamiento Bi-Focal** y el marco **D-ODD (Dynamic Outcome-Driven Development)** con motor de varianza visual anti-clon.

---

## 🌟 Novedades de la Versión 3.7.0 (D-ODD & Visual Variance Release)

### 1. 🌀 Marco D-ODD v2 (Dynamic Outcome-Driven Development)
Rompe el anclaje cognitivo estático del Vault aislando contextos entre la Tesis (apoyada en la historia del proyecto) y la Antítesis (desde primeros principios, sin contaminación de notas):
- **Gate Semántico Cynefin (`assess_decision`)**: Clasifica en 5 dimensiones (reversibilidad, blast radius, incertidumbre, novedad y alternativas) para activar divergencia lateral solo cuando amerita.
- **Ledger Inmutable en SQLite WAL (`decision_ledger.py`)**: Registra el ciclo de vida completo (`open` -> `commit` -> `evidence` -> `close`).
- **Bucle de Aprendizaje y Calibración Continua**: Recalibra dinámicamente el umbral del gate en base a la tasa de adopción de la antítesis y resultados observados.

### 2. 🎨 Motor de Varianza Visual & Veto Anti-Clon
- Evita que los modelos converjan por defecto en la misma plantilla oscura (`slate-950` + acentos ámbar + fila de 4 tarjetas Bento).
- Sortea direcciones de arte contrastadas por proyecto (*Swiss Technical Paper*, *ISA-101 High-Contrast Field HMI*, *Brutalist Hairline Matrix*, *Editorial Dossier Split*).
- Exige la carga obligatoria de fuentes reales en `index.html` y tipografías industriales/editoriales diferenciadas.

### 3. 🎩 Integración Completa con Gentle-AI Suite (Noviembre 2026)
- **`gentle-ai` v3.7.0**: Capacidad de asignación granular de modelos por revisor con fallback tolerante a fallos.
- **`gentle-shell` v4.5.1 / `pi` v1.5.0**: Terminal interactiva aislada en `~/.gentle-shell/agent` con soporte nativo de mensajería inter-orquestador.
- **`engram` v3.6.1**: Motor de memoria persistente con handshake stdio y SQLite WAL.
- **`gga` v2.10.1**: Gentleman Guardian Angel integrado globalmente en PATH.
- **Diagnóstico Unificado**: `gentle-ai doctor` verificado en **8/8 checks pasados (Status: healthy)**.

### 4. 📸 Automatización de Snapshots Semanales (`capture_weekly_snapshot`)
- Motor nativo [`WeeklySnapshotEngine`](src/weekly_snapshot.py) que automatiza la "Foto de los Viernes".
- Agrega telemetría de tareas ODD, recibos RDD, salud del Cortex y actividad de proyectos.
- Actualiza atómicamente la Portada y archiva un snapshot inmutable en `04-APRENDIZAJES/snapshots/snapshot-YYYY-WW.md`.

---

## 🛠️ Catálogo Oficial de las 29 Herramientas MCP Nativas

| Categoría | Herramienta | Descripción | Ruta PLC |
| :--- | :--- | :--- | :---: |
| **🌀 Marco D-ODD** | `assess_decision` | Gate semántico Cynefin (5 dimensiones), clasificación de veredicto y apertura de decisión. | `LOCAL_FAST` |
| | `commit_decision` | Compromete síntesis (tesis/antítesis/híbrido) y genera tareas ODD espejadas en Engram. | `LOCAL_FAST` |
| | `close_decision` | Cierra decisión con evidencia observada de tests y recalibra el gate. | `LOCAL_FAST` |
| | `decision_ledger_stats` | Métricas del bucle de aprendizaje: adopción de antítesis y fire rate. | `LOCAL_FAST` |
| | `stimulate_creative_odd` | Estimulación lateral con paquetes de contexto aislados y provocaciones. | `LOCAL_FAST` |
| **🚀 Abstracción Gentle-AI** | `orchestrate_gentle_task` | Abstracción unificada Gentle-AI (ODD/SDD/FastPath en 1 paso automático). | `LOCAL_FAST` |
| **📸 Portada & Snapshots** | `capture_weekly_snapshot` | Automatiza el snapshot semanal (Foto de los Viernes), actualiza `Portada.md` y calibra gate. | `LOCAL_FAST` |
| **💡 Navegación & Contexto** | `get_project_context` | Recupera el 360° de un proyecto o la Portada ejecutiva en <20ms. | `LOCAL_FAST` |
| | `list_projects` | Lista todos los proyectos insignia descubiertos y el estado de la Portada. | `LOCAL_FAST` |
| | `search_knowledge` | Búsqueda FTS5 en +6,350 notas del Vault con reranker sináptico de Hebb. | `LOCAL_FAST` |
| **🧠 Memoria Persistente** | `recall_memory` | Consulta decisiones históricas (ADRs) y reglas persistentes por proyecto. | `LOCAL_FAST` |
| | `remember_decision` | Registra una nueva decisión arquitectónica duradera en Vault, Engram y SQLite WAL. | `LOCAL_FAST` |
| **🏷️ ODD & Sesión** | `classify_odd_task` | Clasificación determinista (READ_ONLY, SMALL_DIRECT, SUBSTANTIAL_ODD). | `LOCAL_FAST` |
| | `prepare_odd_task` | Genera el documento de feature ODD y su espejo en Engram. | `DELEGATABLE` |
| | `reconcile_odd_resume` | Reconcilia estado local vs memoria Engram y muestra decisiones D-ODD abiertas. | `DELEGATABLE` |
| | `orchestrator_session_bridge` | Mensajería inter-sesión con semántica ACK para Gentle-Shell. | `ORCHESTRATE` |
| **📋 OpenSpec / SDD** | `prepare_sdd_preflight` | Bloque de autoridad y contexto SDD liviano. | `ORCHESTRATE` |
| | `propose_spec` | Crea propuestas formales OpenSpec bajo demanda explícita. | `DELEGATABLE` |
| | `validate_spec` | Valida cumplimiento de especificaciones spec.md. | `DELEGATABLE` |
| | `get_spec_questions` | Cuestionario adaptativo por tipo de sistema (API, CLI, Frontend). | `LOCAL_FAST` |
| | `generate_scaffold` | Generación de esqueletos de código limpios en NestJS o FastAPI. | `DELEGATABLE` |
| **🛡️ Gobernanza & Calidad** | `package_project_context` | Empaqueta el código real en un bundle Markdown ultracompacto (-85% tokens). | `DELEGATABLE` |
| | `audit_project_health` | Auditoría con diagnóstico en vivo de Gentle-AI doctor. | `DELEGATABLE` |
| | `debate_project_feasibility` | Protocolo Red Team para desafiar viabilidad, acoplamientos y costos ocultos. | `DELEGATABLE` |
| | `audit_cortex_health` | Audita salud del cerebro: enlaces rotos, duplicados y notas viejas (LTD). | `DELEGATABLE` |
| **⚡ Optimización & Grafo** | `optimize_token_budget` | Compresión de contexto mediante AST code slicing y deduplicación diferencial. | `LOCAL_FAST` |
| | `route_model_dispatch` | Gateway inteligente que selecciona el modelo óptimo (Fast, Frontier, Coder). | `LOCAL_FAST` |
| | `query_code_graph` | Consulta el grafo sintáctico para clases, módulos y métodos. | `DELEGATABLE` |
| | `sync_project_graph` | Indexa el código fuente y genera el grafo AST del proyecto (Graphify). | `DELEGATABLE` |

---

## 🚀 Inicio Rápido (Quick Start)

### Opción 1: CLI Nativo en Terminal

```powershell
# Ver estado del cerebro y HUD cognitivo
devbrain live

# Capturar la foto semanal de los viernes (Snapshot)
devbrain snapshot -v "Cierre de semana: suite Playwright y RBAC validados."

# Diagnóstico unificado
devbrain doctor
```

### Opción 2: Configuración en Google Antigravity / Gemini CLI (`mcp_config.json`)

```json
{
  "mcpServers": {
    "devbrain": {
      "command": "C:\\Users\\tu_usuario\\AppData\\Local\\Programs\\Python\\Python312\\python.exe",
      "args": [
        "C:\\Users\\tu_usuario\\OneDrive\\Documentos\\Obsidian Vault\\06-SISTEMA\\mcp\\devbrain_mcp.py"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1"
      }
    }
  }
}
```

### Opción 3: Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "devbrain": {
      "command": "python",
      "args": [
        "/ruta/a/tu/Obsidian Vault/06-SISTEMA/mcp/devbrain_mcp.py"
      ]
    }
  }
}
```

---

## 🧪 Verificación de Contratos y Tests

La suite automatizada valida el 100% de la especificación MCP sobre stdio JSON-RPC:

```bash
py -3.12 tests/test_mcp_stdio.py
py -3.12 -m pytest tests/test_odd_mcp.py
```

---

## 📄 Licencia

Distribuido bajo la licencia MIT. Creado con arquitectura de alto rendimiento para desarrollo con IA de nueva generación.
