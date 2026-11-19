# 🧠 DevBrain MCP Server (v4.0.0)

[![MCP Specification](https://img.shields.io/badge/MCP-2024--11--05-blue.svg)](https://modelcontextprotocol.io/)
[![Version](https://img.shields.io/badge/version-4.0.0-brightgreen.svg)](https://github.com/DanielMMiralles/devbrain-mcp)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Gentle-AI](https://img.shields.io/badge/gentle--ai-4.5.0%20%7C%204.8.0-purple.svg)](https://github.com/Gentleman-Programming/gentle-ai)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

**DevBrain** es un Sistema Operativo Cognitivo sobre [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) que integra **Ontología Jerárquica de 4 Niveles**, **Búsqueda Híbrida Local (SQLite FTS5 + Vectores RRF)**, **Portada Viva Materializada**, **Instintos y Guardrails inspirados en ECC**, **Neuroplasticidad Hebbiana**, y **D-ODD v3** sobre la suite **Gentle-AI**.

---

## 🌟 Novedades de la Versión 4.0.0 (Autonomía, Ontología 4-Niveles & Activación Nativa)

### 1. 🏛️ Ontología Jerárquica de 4 Niveles + Actividades tipo Beads
- **`Dimensiones → Áreas → Proyectos → Actividades`** definida declarativamente en `06-SISTEMA/ontologia.yaml` y servida desde SQLite WAL fuera de OneDrive (`~/.devbrain/cortex.db`) en `<15ms`.
- Resuelve aliases fragmentados automáticamente (`Lidera_project2026` → `Lidera-Project`, rutas locales → ID canónico).
- Nivel 4 con grafo de dependencias (`ready` | `in_progress` | `blocked` | `done`).

### 2. 🔌 Plugin Nativo AGY + Hooks v4 + Patrones ECC (`affaan-m/ECC`)
- Empaquetado como plugin nativo en `~/.gemini/config/plugins/devbrain/` (`SessionStart` con briefing L1 `<400` tokens, `PreInvocation` sin campos deprecated, `PreToolUse` guardrail contra `--no-verify` y fuga de secretos `<5ms`, `PostToolUse` y `Stop` con estado de sesión).
- **ECC Instincts**: aprendizajes acotados al proyecto (`confidence: 0.40 → 0.95`) con auto-promoción a Área al alcanzar `>= 0.80` y `>= 3` confirmaciones.

### 3. 🔍 Búsqueda Híbrida Embebida (FTS5 + Vectorizer RRF) & Memoria Bi-Temporal
- SQLite fuera de OneDrive (`~/.devbrain/cortex_fts.db`) con guarda contra archivos placeholder de OneDrive Files On-Demand.
- Fusión Reciprocal Rank Fusion (BM25 + Similitud Coseno Vectorial NumPy 256D) y validez bi-temporal (`valid_from`, `valid_until`, `superseded_by`).

---

## 🛠️ Las 12 Herramientas Profundas MCP + 3 Resources (`v4.0.0`)

*(Todos los endpoints legacy siguen activos en `tools/call` por retrocompatibilidad.)*

| Categoría | Herramienta / Resource | Descripción | Ruta PLC |
| :--- | :--- | :--- | :---: |
| **🧠 Contexto v4** | `brain_context` | Lectura unificada (`<40ms`): Portada L1, Linaje 4-niveles, Actividades, Instintos y Búsqueda Híbrida RRF. | `LOCAL_FAST` |
| **🏛️ Ontología v4** | `brain_tree` | Navega `Dimensión → Área → Proyecto → Actividad`, lista tareas `ready` o sincroniza `ontologia.yaml`. | `LOCAL_FAST` |
| **📋 Actividades v4** | `brain_activity` | Gestiona actividades con `blocked_by` y regenera `Portada.md` atómicamente. | `LOCAL_FAST` |
| **🧩 Memoria v4** | `brain_remember` | Registra decisiones (con reemplazo bi-temporal `supersedes`) o instintos ECC por proyecto. | `LOCAL_FAST` |
| **🌀 Marco D-ODD** | `assess_decision` | Gate Cynefin (5 dims), recomienda flota de especialistas y abre divergencia Tesis/Antítesis. | `LOCAL_FAST` |
| | `commit_decision` | Compromete síntesis, espeja Engram, crea actividades Nivel 4 y actualiza `Portada.md`. | `LOCAL_FAST` |
| | `close_decision` | Cierra con evidencia real, refuerza sinapsis/instintos, extrae anti-patrón si falló y actualiza Portada. | `LOCAL_FAST` |
| | `decision_ledger_stats` | Métricas de adopción de antítesis y calibración del gate. | `LOCAL_FAST` |
| **🚀 Gentle-AI** | `orchestrate_gentle_task` | Abstracción unificada Gentle-AI (ODD / SDD / Fast-Path en 1 paso). | `LOCAL_FAST` |
| **🌲 Grafo AST** | `query_code_graph` | Consulta el grafo sintáctico AST para clases, módulos y dependencias. | `DELEGATABLE` |
| **🩺 Cortex & HUD** | `audit_cortex_health` | Audita enlaces rotos, duplicados y poda sináptica. | `DELEGATABLE` |
| | `capture_weekly_snapshot` | Snapshot semanal leyendo métricas de SQLite + materialización de `Portada.md`. | `LOCAL_FAST` |
| **📡 Resources** | `devbrain://portada\|tree\|ready` | Recursos MCP nativos expuestos en `resources/list` y `resources/read`. | `RESOURCE` |

---

## 🚀 Inicio Rápido (Quick Start)

### Opción 1: CLI Nativo en Terminal

```powershell
# Ver estado del cerebro y HUD cognitivo
devbrain live

# Capturar la foto semanal de los viernes (Snapshot)
devbrain snapshot -v "Cierre de semana: DevBrain v4 operativo."

# Diagnóstico unificado
devbrain doctor
```

### Opción 2: Google Antigravity / Gemini CLI (`mcp_config.json` + Plugin Nativo)

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

```bash
py -3.12 -m unittest discover -s tests -p "test_*.py" -v
py -3.12 tests/test_mcp_stdio.py
```

---

## 📄 Licencia

Distribuido bajo la licencia MIT. Creado con arquitectura de alto rendimiento para desarrollo con IA de nueva generación.
