"""
DevBrain CLI Help & Knowledge Center (v1.0)
Sistema de ayuda visual interactivo y categorizado para DevBrain CLI, HUD, herramientas MCP y protocolos.
"""
from __future__ import annotations
import sys
from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown

from cli_theme import ThemeColors

AVAILABLE_TOPICS: dict[str, str] = {
    "live": "Opciones del HUD en vivo a 60fps, paneles y telemetría en tiempo real",
    "odd": "Protocolo Organic Driven Development (ODD), clasificaciones y ciclo de trabajo",
    "mcp": "Catálogo completo de las 21 herramientas MCP de DevBrain y sus firmas",
    "hosts": "Guía de conexión para Google Antigravity (AGY), Cursor IDE y Claude Code",
    "neuro": "Motor de neuroplasticidad, regla de Hebb, LTP/LTD y bonus sináptico",
    "shell": "Uso de la terminal interactiva REPL, comandos rápidos y dock questions"
}

def render_help_overview(console: Console, theme: ThemeColors) -> None:
    """Renderiza el manual general de comandos y funcionalidades de DevBrain CLI."""
    
    # 1. Banner Superior
    grid = Table.grid(expand=True)
    grid.add_column(justify="center", ratio=1)
    
    banner = Text.assemble(
        ("🧠 DEVBRAIN v3.0 ", f"bold {theme.primary}"),
        ("— MANUAL DE COMANDOS & FUNCIONALIDADES\n", f"bold {theme.secondary}"),
        ("Controlador PLC Neuroplástico • Telemetría Cognitiva • Suite Gentle-AI & ODD", f"dim {theme.dim}")
    )
    grid.add_row(banner)
    console.print(Panel(grid, box=box.ROUNDED, border_style=theme.primary))

    # 2. Tabla de Comandos Principales
    table = Table(
        title="⚡ Comandos del CLI ('devbrain <comando>')",
        box=None,
        expand=True,
        header_style=f"bold {theme.secondary}",
        padding=(0, 1)
    )
    table.add_column("Comando", style=f"bold {theme.accent}", ratio=2)
    table.add_column("Sintaxis & Argumentos", style=f"{theme.primary}", ratio=3)
    table.add_column("Descripción & Propósito", style=f"{theme.text}", ratio=5)
    table.add_column("Área", justify="center", style=f"dim {theme.dim}", ratio=2)

    # Monitoreo & HUD
    table.add_row(
        "live, hud",
        "devbrain live [--rate S] [--papa] [--once]",
        "Inicia el Cognitive HUD en vivo a 60fps. Monitorea tokens, costos USD, latencias p50/p95, traza de pensamiento y carril de orquestación.",
        "🖥️ HUD"
    )
    table.add_row(
        "stats",
        "devbrain stats",
        "Muestra el resumen consolidado de la sesión: llamadas MCP, tokens in/out, throughput y costos acumulados.",
        "📊 Métricas"
    )
    # Terminal & Diagnóstico
    table.add_row(
        "shell",
        "devbrain shell",
        "Abre la terminal interactiva estilo Gentle-Shell con autocompletado inteligente y dock questions ODD.",
        "💬 Shell"
    )
    table.add_row(
        "doctor",
        "devbrain doctor",
        "Ejecuta diagnóstico de salud unificado: DevBrain, FTS5, Engram v2.0 y Gentle-AI v3.1+.",
        "🩺 Salud"
    )
    # Conocimiento & Memoria
    table.add_row(
        "search",
        "devbrain search \"<query>\"",
        "Busca en +1,675 notas técnicas del Vault de Obsidian con FTS5 y aceleración por sinapsis dinámicas.",
        "💡 Cerebro"
    )
    table.add_row(
        "memory",
        "devbrain memory \"<query>\"",
        "Recupera decisiones arquitectónicas, lecciones aprendidas y directrices de Obsidian y Engram.",
        "🧠 Memoria"
    )
    # ODD
    table.add_row(
        "odd",
        "devbrain odd \"<tarea>\"",
        "Evalúa deterministamente una tarea bajo el protocolo ODD (READ_ONLY, SMALL_DIRECT o SUBSTANTIAL_ODD).",
        "🏷️ ODD"
    )
    # Configuración & Temas
    table.add_row(
        "theme",
        "devbrain theme [gentleman|cyberpunk|obsidian|monokai|papa]",
        "Consulta o cambia la paleta de colores del CLI y el HUD con persistencia en ~/.devbrain/config.json.",
        "🎨 Visual"
    )
    table.add_row(
        "papa",
        "devbrain papa",
        "Alterna el 'Modo Papa' minimalista monocromático para ultra-bajo consumo de recursos y batería.",
        "⚡ Batería"
    )
    table.add_row(
        "help",
        "devbrain help [tema]",
        "Muestra esta guía general o la documentación profunda de un tópico específico.",
        "📖 Ayuda"
    )

    console.print(Panel(table, box=box.ROUNDED, border_style=theme.secondary))

    # 3. Capacidades Arquitectónicas Clave
    arch_table = Table.grid(expand=True, padding=(0, 2))
    arch_table.add_column(ratio=1)
    arch_table.add_column(ratio=1)

    col1 = Text.assemble(
        ("⚙️ Arquitectura PLC Router\n", f"bold {theme.primary}"),
        ("Clasifica peticiones en ultra-baja latencia (<5ms). Las consultas de memoria y búsqueda se resuelven en ", f"{theme.text}"),
        ("LOCAL_FAST", f"bold {theme.success}"),
        (", mientras que las orquestaciones pesadas se delegan a Gentle-PI.", f"{theme.text}")
    )
    col2 = Text.assemble(
        ("🧬 Grafo Sináptico Hebbiano\n", f"bold {theme.accent}"),
        ("Implementa plasticidad biológica (regla de Hebb, LTP, LTD y poda). Las co-activaciones refuerzan las conexiones y generan un ", f"{theme.text}"),
        ("Synaptic Bonus", f"bold {theme.secondary}"),
        (" que prioriza resultados en búsquedas.", f"{theme.text}")
    )
    arch_table.add_row(col1, col2)

    console.print(Panel(arch_table, title="[bold]🔬 Arquitectura & Filosofía de DevBrain v3.0[/bold]", box=box.ROUNDED, border_style=theme.accent))

    # 4. Tópicos de Ayuda Detallada
    topics_text = Text()
    topics_text.append("Profundiza en cualquier aspecto con ", style=f"{theme.text}")
    topics_text.append("devbrain help <tópico>", style=f"bold {theme.accent}")
    topics_text.append(":\n\n", style=f"{theme.text}")
    
    for t_name, t_desc in AVAILABLE_TOPICS.items():
        topics_text.append(f"  • devbrain help {t_name:<7}", style=f"bold {theme.secondary}")
        topics_text.append(f" ──► {t_desc}\n", style=f"dim {theme.dim}")

    console.print(Panel(topics_text, title="[bold]📚 Tópicos de Ayuda Especializada[/bold]", box=box.ROUNDED, border_style=theme.dim))


def render_topic_help(console: Console, theme: ThemeColors, topic: str) -> None:
    """Renderiza ayuda profunda y detallada sobre un tópico específico."""
    t_clean = topic.lower().strip()

    if t_clean in ["live", "hud"]:
        content = """### 🖥️ DevBrain Live Cognitive HUD (`devbrain live` / `devbrain hud`)

El HUD es un dashboard interactivo de terminal a 60fps renderizado con **Rich**, diseñado para ejecutarse en paralelo a tu agente de IA:

#### Flags y Opciones:
- `--rate <segundos>`: Intervalo de sondeo del bus de eventos (default: `0.5` segundos).
- `--papa`: Inicia directamente en **Modo Papa** (sin bordes coloridos, ahorro de ciclos de CPU y batería).
- `--once`: Renderiza un único cuadro estático con las métricas actuales y sale de inmediato (ideal para scripts o pipes).

#### Los 4 Paneles del Dashboard:
1. **Header Superior**: Indica el Host IDE activo (`Antigravity`, `Cursor`, `Claude Code`), modelo de IA detectado, paleta visual y estado de Modo Papa.
2. **Métricas de Rendimiento & Tokens**:
   - Conteo atómico: `Tokens In`, `Tokens Out`, `Tokens Totales`.
   - Estimador de Costo en USD en tiempo real según el modelo.
   - Throughput en tiempo real (`tokens/segundo`).
   - Latencias de respuesta: $p50$ (mediana) y $p95$ (cola de latencia).
   - Herramientas MCP más ejecutadas.
3. **💡 ¿Cómo Piensa? (Cognición & Sinapsis)**:
   - Última acción y decisión del **PLC Router** (`LOCAL_FAST`, `DELEGATE`, `ORCHESTRATE`).
   - Rastro de razonamiento del agente.
   - Sinapsis activas co-disparadas en la sesión mediante la regla de Hebb.
4. **🔄 Carril de Orquestación en Vivo**:
   - Diagrama de flujo secuencial del pipeline: `PLC -> ODD -> Gentle-PI -> Review Gate`.
   - Estado de conectividad de la suite (`engram`, `gentle-ai`, `gentle-shell`).
"""
        console.print(Panel(Markdown(content), title="[bold]🖥️ Guía Detallada: Live Cognitive HUD[/bold]", border_style=theme.secondary))

    elif t_clean in ["odd"]:
        content = """### 🏷️ Protocolo Organic Driven Development (ODD)

ODD reemplaza la burocracia rígida de los SDD tradicionales por un enfoque pragmático:
**"La estructura aparece en proporción a la necesidad. Nunca más, nunca menos."**

#### Niveles de Clasificación Determinista (`devbrain odd "<tarea>"`):
1. **`READ_ONLY`**:
   - Consultas de conocimiento, lectura de archivos, explicaciones, formateo o preguntas conceptuales.
   - **Acción**: Responder de inmediato. **Cero artefactos**, cero overhead.
2. **`SMALL_DIRECT`**:
   - Corrección de bugs puntuales, cambios cosméticos o modificaciones localizadas (<2 pasos significativos).
   - **Acción**: Implementación inmediata con verificaciones proporcionales. No crear carpetas de tarea.
3. **`SUBSTANTIAL_ODD`**:
   - Nuevos features, refactorizaciones de múltiples archivos, migraciones o trabajo con dependencias complejas (≥2 pasos).
   - **Acción OBLIGATORIA**: Invocar `prepare_odd_task` para generar `odd/tasks/<feature>.md` y su espejo persistente en Engram topic `odd/<feature>/tasks` antes de la primera edición de código.

#### Ecosistema & Guardrails de Gentle-AI v3.5.0:
- **Review (RDD) por Defecto**: El review viene encendido de fábrica con análisis de riesgo **fail-safe** (cualquier error de análisis se asume de alto riesgo por seguridad).
- **Dock Questions Interactivo**: Para resolver incertidumbre (Paso 3 ODD), se despliegan preguntas navegables por teclado en el dock sin interrumpir el chat principal.
"""
        console.print(Panel(Markdown(content), title="[bold]🏷️ Guía Detallada: Protocolo ODD[/bold]", border_style=theme.primary))

    elif t_clean in ["mcp", "tools"]:
        table = Table(title="🛠️ Las 21 Herramientas MCP de DevBrain v3.0", box=None, expand=True, padding=(0, 1))
        table.add_column("Categoría", style=f"bold {theme.primary}", ratio=2)
        table.add_column("Herramienta MCP", style=f"bold {theme.accent}", ratio=3)
        table.add_column("Propósito & Comportamiento", style=f"{theme.text}", ratio=5)
        table.add_column("Ruta PLC", justify="center", ratio=2)

        table.add_row("💡 Conocimiento", "get_project_context", "Recupera arquitectura, stack y README de proyectos insignia.", "[green]LOCAL_FAST[/green]")
        table.add_row("💡 Conocimiento", "list_projects", "Lista proyectos activos y descubiertos en disco.", "[green]LOCAL_FAST[/green]")
        table.add_row("💡 Conocimiento", "search_knowledge", "Búsqueda FTS5 en +1,675 notas con reranking sináptico.", "[green]LOCAL_FAST[/green]")
        table.add_row("🧠 Memoria", "remember_decision", "Guarda directrices en Vault y sincroniza con Engram v2.", "[green]LOCAL_FAST[/green]")
        table.add_row("🧠 Memoria", "recall_memory", "Consulta decisiones previas en Vault y Engram search.", "[green]LOCAL_FAST[/green]")

        table.add_row("📋 OpenSpec / SDD", "propose_spec", "Genera propuestas formales OpenSpec bajo demanda explícita.", "[yellow]DELEGATABLE[/yellow]")
        table.add_row("📋 OpenSpec / SDD", "validate_spec", "Valida que spec.md cumpla el 100% de la especificación.", "[yellow]DELEGATABLE[/yellow]")
        table.add_row("📋 OpenSpec / SDD", "get_spec_questions", "Preguntas clave adaptadas por tipo de sistema.", "[green]LOCAL_FAST[/green]")
        table.add_row("📋 OpenSpec / SDD", "generate_scaffold", "Genera esqueleto funcional en NestJS o FastAPI.", "[yellow]DELEGATABLE[/yellow]")
        table.add_row("📋 OpenSpec / SDD", "prepare_sdd_preflight", "Contrato SDD liviano con preflight de autoridad.", "[red]ORCHESTRATE[/red]")

        table.add_row("🛡️ Gobernanza", "package_project_context", "Bundle markdown ultracompacto del código real.", "[yellow]DELEGATABLE[/yellow]")
        table.add_row("🛡️ Gobernanza", "audit_project_health", "Auditoría con diagnóstico en vivo de Gentle-AI doctor.", "[yellow]DELEGATABLE[/yellow]")
        table.add_row("🛡️ Gobernanza", "debate_project_feasibility", "Modo Debate Sin Filtros (Red Team) contra SPOF y costos.", "[yellow]DELEGATABLE[/yellow]")
        table.add_row("🛡️ Gobernanza", "audit_ponytail_complexity", "Auditoría YAGNI para podar sobre-ingeniería.", "[yellow]DELEGATABLE[/yellow]")

        table.add_row("🌲 Grafo AST", "query_code_graph", "Consulta grafo sintáctico AST de símbolos y clases.", "[yellow]DELEGATABLE[/yellow]")
        table.add_row("🌲 Grafo AST", "sync_project_graph", "Indexa código fuente y genera relaciones AST Graphify.", "[yellow]DELEGATABLE[/yellow]")

        table.add_row("🏷️ ODD & Sesión", "classify_odd_task", "Clasificación determinista ODD (READ_ONLY, SMALL, SUBSTANTIAL).", "[green]LOCAL_FAST[/green]")
        table.add_row("🏷️ ODD & Sesión", "prepare_odd_task", "Crea odd/tasks/<feature>.md y espejo en Engram topic.", "[yellow]DELEGATABLE[/yellow]")
        table.add_row("🏷️ ODD & Sesión", "reconcile_odd_resume", "Reconcilia estado local con memoria Engram tras reinicio.", "[yellow]DELEGATABLE[/yellow]")
        table.add_row("🏷️ ODD & Sesión", "orchestrator_session_bridge", "Mensajería inter-orquestador con ACK de Gentle-Shell.", "[red]ORCHESTRATE[/red]")
        table.add_row("⚡ Optimización", "route_model_dispatch", "Recomienda LLM costo-eficiente (Fast, Frontier, Coder).", "[green]LOCAL_FAST[/green]")

        console.print(Panel(table, title="[bold]🛠️ Catálogo Oficial de Herramientas MCP & Rutas PLC[/bold]", border_style=theme.accent))

    elif t_clean in ["hosts", "ide", "cursor", "claude", "agy"]:
        content = """### 🔌 Conexión con Hosts e IDEs (Antigravity, Cursor, Claude Code)

DevBrain opera con un **bus de eventos desacoplado** (`~/.devbrain/live_events.jsonl`), lo que permite que tu IDE trabaje con el servidor MCP mientras mantienes una terminal con `devbrain live` monitoreando todo en tiempo real.

#### 1. Google Antigravity / Gemini CLI (`mcp_config.json`)
```json
{
  "mcpServers": {
    "devbrain": {
      "command": "python",
      "args": ["C:/Users/damm1/.gemini/antigravity/scratch/devbrain-mcp/src/devbrain_mcp.py"],
      "env": {
        "VAULT_DIR": "C:/Users/damm1/OneDrive/Documentos/Obsidian Vault"
      }
    }
  }
}
```

#### 2. Cursor IDE (`settings.json` o interfaz MCP)
- **Tipo**: `stdio` / `command`
- **Comando**: `python C:/Users/damm1/.gemini/antigravity/scratch/devbrain-mcp/src/devbrain_mcp.py`
- DevBrain detecta automáticamente a Cursor mediante los traces y headers de sesión.

#### 3. Claude Code / Claude Desktop (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "devbrain": {
      "command": "python",
      "args": ["C:/Users/damm1/.gemini/antigravity/scratch/devbrain-mcp/src/devbrain_mcp.py"]
    }
  }
}
```

#### 💡 Flujo de Trabajo Recomendado:
Abre una terminal lateral en Windows y corre:
```powershell
devbrain live
```
Cada vez que Cursor, Antigravity o Claude hagan una llamada MCP a DevBrain, verás cómo se actualizan instantáneamente los tokens, el costo, la traza de razonamiento y las sinapsis disparadas.
"""
        console.print(Panel(Markdown(content), title="[bold]🔌 Conexión de IDEs y Clientes MCP[/bold]", border_style=theme.secondary))

    elif t_clean in ["neuro", "plasticity", "sinapsis"]:
        content = r"""### 🧬 Motor de Neuroplasticidad Sináptica (`src/neuroplasticity.py`)

Inspirado en el funcionamiento del cerebro biológico, DevBrain no trata las notas de conocimiento como registros estáticos:

#### 1. Regla de Hebb (*"Neurons that fire together wire together"*):
Cuando dos notas o conceptos se activan dentro de la misma sesión de trabajo (por ejemplo `odd` y `tdd`), el motor crea y fortalece una sinapsis bidireccional entre ambos.

#### 2. Potenciación a Largo Plazo (LTP):
Cada co-activación incrementa el peso sináptico de acuerdo a la ecuación con saturación:
$$w_{nuevo} = w_{actual} + \Delta \cdot \\left(1 - \\frac{w_{actual}}{W_{max}}\\right)$$
Donde $W_{max} = 100.0$. Esto garantiza que los axones de mayor uso se consoliden sin desbordarse.

#### 3. Depresión a Largo Plazo (LTD) y Poda Sináptica:
- Las conexiones que no se usan decaen exponencialmente con una vida media de 30 días ($2^{-\\Delta t / 30}$).
- Durante la optimización periódica, las sinapsis residuales con peso $< 0.1$ se podan para mantener la red ágil.

#### 4. Synaptic Bonus en Búsquedas FTS5:
Al buscar en el cerebro con `search_knowledge`, el reranker compuesto calcula un bonus determinista basado en las sinapsis activas en la sesión actual, trayendo a la superficie notas contextualmente vinculadas.
"""
        console.print(Panel(Markdown(content), title="[bold]🧬 Motor de Neuroplasticidad & Grafo Sináptico[/bold]", border_style=theme.primary))

    elif t_clean in ["shell", "repl"]:
        content = """### 💬 DevBrain Interactive Shell (`devbrain shell`)

El Shell interactivo te permite dialogar y explorar el cerebro sin necesidad de abrir un IDE:

#### Comandos Slash Disponibles:
- `/search <query>`: Búsqueda con reranking sináptico en Vault.
- `/memory <query>`: Consulta decisiones arquitectónicas en Obsidian y Engram.
- `/remember <título> | <detalle>`: Guarda una directriz en disco y en Engram.
- `/odd <descripción>`: Clasificación ODD determinista.
- `/feature <nombre> | <objetivo>`: Crea tarea ODD y espejo en Engram.
- `/stats`: Muestra métricas de tokens y costos de la sesión.
- `/doctor`: Diagnóstico del ecosistema Gentle-AI.
- `/theme <paleta>`: Cambia el tema visual.
- `/papa`: Alterna Modo Papa.
- `/help [tema]`: Muestra la guía general o de un tópico.
- `/exit` o `/quit`: Cierra la sesión interactiva.
"""
        console.print(Panel(Markdown(content), title="[bold]💬 Terminal Interactiva Shell[/bold]", border_style=theme.secondary))

    else:
        console.print(f"[red]Tópico desconocido: '{topic}'.[/red]")
        console.print(f"Opciones válidas: [bold]{', '.join(AVAILABLE_TOPICS.keys())}[/bold]")
