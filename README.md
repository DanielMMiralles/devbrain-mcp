# 🧠 DevBrain MCP Server (v3.1.0)

[![MCP Specification](https://img.shields.io/badge/MCP-2024--11--05-blue.svg)](https://modelcontextprotocol.io/)
[![Version](https://img.shields.io/badge/version-3.1.0-brightgreen.svg)](https://github.com/DanielMMiralles/devbrain-mcp)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-ready-green.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

**DevBrain** es un servidor unificado de [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) que actúa como un **Sistema Operativo Cognitivo y Capa de Abstracción Superior sobre Gentle-AI**. Conecta modelos de inteligencia artificial con un cerebro de conocimiento en **Obsidian** (+6,350 notas técnicas), memoria Hebbiana neuroplástica, cuadro de mando ejecutivo vivo (**Portada**) y un motor de **Razonamiento Bi-Focal (Inteligencia Sincrónica y Diacrónica)**.

---

## 🌟 Novedades de la Versión 3.1.0 (Cognitive Bi-Focal Release)

### 1. ⚖️ Razonamiento Bi-Focal: Sincronía vs. Diacronía (Token-Efficient)
Los LLMs comerciales suelen sufrir de **amnesia diacrónica**: evalúan únicamente el código que cabe en su prompt actual e ignoran el porqué histórico de las decisiones previas, reintroduciendo bugs ya resueltos. DevBrain v3.1.0 dota a los agentes de visión bi-focal:

- **Eje Sincrónico (El "Ahora" / Coherencia Estructural)**:
  - Analiza el sistema en un instante de tiempo presente.
  - Valida coherencia con AST, compilador de tipos estrictos, linters y aserciones de [[Playwright]].
- **Eje Diacrónico (El "Por qué" / Evolución Temporal)**:
  - Analiza la causalidad histórica: decisiones pasadas (ADRs en `04-APRENDIZAJES/decisiones/`), memoria de errores (`04-APRENDIZAJES/errores/`), git history y snapshots semanales.
  - Otorga **inmunidad a la regresión**: el agente no "simplifica" código defensivo creyendo erróneamente que es código muerto.
- **Regla de Proporcionalidad Anti-Gasto de Tokens**:
  - *Tareas Triviales (<2 pasos)*: 100% modo sincrónico directo. Cero gasto de tokens en arqueología histórica.
  - *Tareas Sustanciales (ODD ≥2 pasos)*: Inyección automática acotada de las 2-3 decisiones clave relevantes (<200 tokens) antes de modificar código sensible.

### 2. 📰 Portada Viva (`Portada.md` — L1 Cache Cognitivo)
Ubicada en la raíz del Vault, estructura la ontología en:
- **Horizonte Activo**: Los 2 o 3 proyectos en foco de la semana.
- **Dimensiones & Áreas**: 
  - *Dimensión I (Sistemas Core & Producción)*: B2B, Logística, Marketplaces.
  - *Dimensión II (IA, Agentes & Automatización)*: Sistemas Multi-Agente, Metasistema.
  - *Dimensión III (DevOps, Infraestructura & Educación)*: K8s, Cloud, I+D.
- **Malla Transversal**: Herramientas y estándares canónicos que alimentan a todos los proyectos en paralelo.
- Responde a consultas ejecutivas en **<800 tokens** mediante `get_project_context(project_name="portada")`.

### 3. 📸 Automatización de Snapshots Semanales (`capture_weekly_snapshot`)
- Motor nativo [`WeeklySnapshotEngine`](src/weekly_snapshot.py) que automatiza la "Foto de los Viernes".
- Agrega telemetría de tareas ODD y recibos RDD, salud del Cortex y actividad de proyectos.
- Actualiza atómicamente la Portada y archiva un snapshot inmutable en `04-APRENDIZAJES/snapshots/snapshot-YYYY-WW.md`.
- Disponible tanto en CLI (`devbrain snapshot`) como en herramienta MCP (`capture_weekly_snapshot`).

### 4. 🎭 E2E Testing Framework Canónico con Playwright
- Estandarización de [[Playwright]] como framework E2E oficial del ecosistema.
- Jerarquía semántica estricta (`getByRole` > `getByLabel` > `getByText` > `getByTestId`).
- Prohibición de hard sleeps (`page.waitForTimeout`); uso obligatorio de auto-waiting nativo.
- Aislamiento de sesiones con `storageState` y fixtures tipadas multi-rol (`adminPage`, `userPage`).

---

## 🛠️ Las 24 Herramientas MCP Nativas

| Categoría | Herramienta | Descripción |
| :--- | :--- | :--- |
| **Orquestación & Abstracción** | `orchestrate_gentle_task` | Capa superior sobre Gentle-AI: clasifica, prepara ODD/SDD y espeja en Engram en 1 solo paso. |
| **Snapshots & Portada** | `capture_weekly_snapshot` | Automatiza el snapshot semanal (Foto de los Viernes) y actualiza `Portada.md`. |
| **Navegación & Contexto** | `get_project_context` | Recupera el 360° de un proyecto o la Portada ejecutiva en <20ms. |
| | `list_projects` | Lista todos los proyectos insignia descubiertos y el estado de la Portada. |
| | `search_knowledge` | Búsqueda FTS5 en +6,350 notas del Vault con reranker sináptico de Hebb. |
| **Memoria Persistente** | `recall_memory` | Consulta decisiones históricas (ADRs) y reglas persistentes por proyecto. |
| | `remember_decision` | Registra una nueva decisión arquitectónica duradera en Vault, Engram y SQLite. |
| **Calidad & Telemetría** | `audit_cortex_health` | Audita salud del cerebro: enlaces rotos, duplicados y notas viejas (LTD). |
| | `audit_project_health` | Audita dependencias, estado de contenedores y deuda técnica de un proyecto. |
| | `optimize_token_budget` | Compresión de contexto mediante AST code slicing (-80% a -90% tokens). |
| **Protocolo ODD & SDD** | `classify_odd_task` | Clasificación determinista (READ_ONLY, SMALL_DIRECT, SUBSTANTIAL_ODD). |
| | `prepare_odd_task` | Genera el documento de feature ODD y su espejo en Engram. |
| | `reconcile_odd_resume` | Reconcilia estado local vs memoria Engram al reanudar sesiones. |
| | `orchestrator_session_bridge` | Mensajería inter-sesión con semántica ACK para Gentle-Shell. |
| | `prepare_sdd_preflight` | Bloque de autoridad y contexto SDD liviano. |
| | `propose_spec` | Crea propuestas formales OpenSpec. |
| | `validate_spec` | Valida cumplimiento de especificaciones spec.md. |
| | `get_spec_questions` | Cuestionario adaptativo por tipo de sistema (API, CLI, Frontend). |
| | `generate_scaffold` | Generación de esqueletos de código limpios en NestJS o FastAPI. |
| **Grafo AST & Gateway** | `query_code_graph` | Consulta el grafo sintáctico para clases, módulos y métodos. |
| | `sync_project_graph` | Indexa el código fuente y genera el grafo AST del proyecto. |
| | `package_project_context` | Empaqueta el código real en un bundle Markdown ultracompacto. |
| | `debate_project_feasibility` | Protocolo Red Team para desafiar viabilidad y costos ocultos. |
| | `route_model_dispatch` | Gateway inteligente que selecciona el modelo óptimo (FAST vs FRONTIER vs CODER). |

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
