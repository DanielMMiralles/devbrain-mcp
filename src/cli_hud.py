"""
DevBrain Live HUD & Cognitive Workspace (v2.0)
Dashboard interactivo de telemetría, cognición y orquestación:
- UI/UX de alta fidelidad con bordes redondeados (box.ROUNDED), tarjetas KPI y métricas en vivo.
- "¿Cómo Piensa?": Trazas cognitivas, decisiones del PLC Router y nodos sinápticos Hebbianos.
- Carril de Orquestación Ecosistémica (Gentle-PI, Engram v2.0, Review Guardrail).
- Soporte dual: Workspace Interactivo (HUD + Dock de entrada) y Modo Observador Pasivo con detección de cambios.
"""
from __future__ import annotations
import os
import sys

if sys.platform == "win32":
    try:
        if hasattr(sys.stdin, "reconfigure"): sys.stdin.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"): sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import time
from datetime import datetime
from rich import box
from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live

from telemetry import TelemetryEngine
from cli_theme import ConfigManager, ThemeColors

class DevBrainHUD:
    """Dashboard de monitoreo y cognición en tiempo real para DevBrain."""

    def __init__(self, console: Console | None = None, config_mgr: ConfigManager | None = None):
        self.console = console or Console(legacy_windows=False)
        self.config_mgr = config_mgr or ConfigManager()
        self.telemetry = TelemetryEngine.get_instance()
        self.theme = self.config_mgr.get_theme()

    def get_layout_mode(self) -> dict:
        """Determina el modo responsive actual basado en el ancho y alto del terminal."""
        width = self.console.size.width if self.console.size.width > 0 else 80
        height = self.console.size.height if self.console.size.height > 0 else 24
        return {
            "width": width,
            "height": height,
            "is_narrow": width < 90,
            "is_medium": 90 <= width < 125,
            "is_wide": width >= 125,
            "is_compact_height": height < 28
        }

    def generate_header(self, summary: dict, mode: dict | None = None) -> Panel:
        if mode is None:
            mode = self.get_layout_mode()
        client = summary.get("active_client", "Standalone")
        model = summary.get("active_model", "gemini-3.8-flash")
        is_papa = self.config_mgr.config.get("papa_mode", False)
        papa_str = "ACTIVO" if is_papa else "OFF"
        theme_name = self.theme.name

        grid = Table.grid(expand=True)
        if mode["is_narrow"]:
            grid.add_column(justify="left", ratio=1)
            grid.add_column(justify="right", ratio=1)

            t_left = Text.assemble(
                ("🧠 DEVBRAIN ", f"bold {self.theme.primary}"),
                ("v3.0", f"bold {self.theme.secondary}"),
                (" ●", f"bold {self.theme.success}"),
                (" │ ", f"dim {self.theme.dim}"),
                (f"{client[:12]}", f"bold {self.theme.secondary}")
            )
            t_right = Text.assemble(
                (f"{model[:14]}", f"bold {self.theme.accent}"),
                (" │ ", f"dim {self.theme.dim}"),
                (f"Papa: {papa_str}", f"bold {self.theme.warning if is_papa else self.theme.success}")
            )
            grid.add_row(t_left, t_right)
        else:
            grid.add_column(justify="left", ratio=1)
            grid.add_column(justify="center", ratio=1)
            grid.add_column(justify="right", ratio=1)

            t_title = Text.assemble(
                (" 🧠 DEVBRAIN ", f"bold {self.theme.primary}"),
                ("v3.0", f"bold {self.theme.secondary}"),
                (" │ ", f"dim {self.theme.dim}"),
                ("● ONLINE", f"bold {self.theme.success}")
            )
            t_center = Text.assemble(
                ("Host: ", f"dim {self.theme.dim}"),
                (f"{client}", f"bold {self.theme.secondary}"),
                (" │ Modelo: ", f"dim {self.theme.dim}"),
                (f"{model}", f"bold {self.theme.accent}")
            )
            t_right = Text.assemble(
                ("Tema: ", f"dim {self.theme.dim}"),
                (theme_name, f"bold {self.theme.secondary}"),
                (" │ Papa: ", f"dim {self.theme.dim}"),
                (papa_str, f"bold {self.theme.warning if is_papa else self.theme.success}"),
                (" ", "default")
            )
            grid.add_row(t_title, t_center, t_right)

        return Panel(grid, box=box.ROUNDED, border_style=self.theme.primary)

    def generate_metrics_panel(self, summary: dict, mode: dict | None = None) -> Panel:
        if mode is None:
            mode = self.get_layout_mode()
        in_tok = summary.get("total_in_tokens", 0)
        out_tok = summary.get("total_out_tokens", 0)
        tot_tok = summary.get("total_tokens", 0)
        cost = summary.get("total_cost_usd", 0.0)
        tps = summary.get("throughput_tps", 0.0)
        p50 = summary.get("p50_latency_ms", 0.0)
        p95 = summary.get("p95_latency_ms", 0.0)
        calls = summary.get("total_calls", 0)

        status_text = "ÓPTIMO (<50ms)" if p50 < 50 else ("BUENO" if p50 < 200 else "DEGRADADO")

        if mode["is_narrow"]:
            title = "[bold]⚡ Métricas & Tokens[/bold]"
            table = Table.grid(expand=True, padding=(0, 1))
            table.add_column(style=f"dim {self.theme.dim}", ratio=3)
            table.add_column(justify="right", style=f"bold {self.theme.text}", ratio=2)

            table.add_row(" In/Out:", f"[{self.theme.accent}]{in_tok:,}/{out_tok:,}[/]")
            table.add_row(" Total:", f"[bold {self.theme.primary}]{tot_tok:,}[/]")
            table.add_row(" Costo USD:", f"[bold {self.theme.success}]${cost:.5f}[/]")
            table.add_row(" Throughput:", f"{tps:.1f} t/s")
            table.add_row(" Consultas:", f"[{self.theme.secondary}]{calls} reqs[/]")
            table.add_row(" p50 / p95:", f"{p50:.0f}/{p95:.0f} ms")
            table.add_row(" Estado:", f"[bold {self.theme.success}]{status_text[:6]}[/]")

            t_counts = summary.get("tool_counts", {})
            if t_counts and not mode["is_compact_height"]:
                act_table = Table.grid(expand=True, padding=(0, 1))
                act_table.add_column(style=f"bold {self.theme.secondary}", ratio=3)
                act_table.add_column(justify="right", ratio=2)
                act_table.add_column(justify="right", style=f"dim {self.theme.dim}", ratio=1)

                max_count = max(t_counts.values()) if t_counts else 1
                for tool_name, count in sorted(t_counts.items(), key=lambda x: x[1], reverse=True)[:2]:
                    pct = count / max_count
                    bars = int(pct * 5)
                    bar_str = "█" * bars + "░" * (5 - bars)
                    act_table.add_row(
                        f" `{tool_name[:12]}`",
                        Text(bar_str, style=f"bold {self.theme.accent}"),
                        f"{count}x"
                    )
                content = Group(
                    table,
                    Text(" 📊 Herramientas:", style=f"bold {self.theme.secondary}"),
                    act_table
                )
            else:
                content = table
        else:
            title = "[bold]⚡ Métricas de Rendimiento & Consumo de Tokens[/bold]"
            table = Table.grid(expand=True, padding=(0, 1))
            table.add_column("Métrica", ratio=3, style=f"dim {self.theme.dim}")
            table.add_column("Valor", justify="right", ratio=2, style=f"bold {self.theme.text}")

            table.add_row(" 📥 Tokens In:", f"[{self.theme.accent}]{in_tok:,}[/{self.theme.accent}]")
            table.add_row(" 📤 Tokens Out:", f"[{self.theme.accent}]{out_tok:,}[/{self.theme.accent}]")
            table.add_row(" ⚡ Tokens Totales:", f"[bold {self.theme.primary}]{tot_tok:,}[/bold {self.theme.primary}]")
            table.add_row(" 💵 Costo USD:", f"[bold {self.theme.success}]${cost:.5f}[/bold {self.theme.success}]")
            table.add_row(" 🚀 Throughput:", f"{tps} tok/s")
            table.add_row(" 🔢 Consultas MCP:", f"[{self.theme.secondary}]{calls} reqs[/{self.theme.secondary}]")
            table.add_row(" ⏱️ Latencia (p50):", f"{p50} ms")
            table.add_row(" ⚠️ Latencia (p95):", f"[{self.theme.warning if p95 > 100 else self.theme.accent}]{p95} ms[/]")
            table.add_row(" 🟢 Canal:", f"[bold {self.theme.success}]{status_text}[/bold {self.theme.success}]")

            t_counts = summary.get("tool_counts", {})
            if t_counts:
                act_table = Table.grid(expand=True, padding=(0, 1))
                act_table.add_column(style=f"bold {self.theme.secondary}", ratio=3)
                act_table.add_column(justify="right", ratio=2)
                act_table.add_column(justify="right", style=f"dim {self.theme.dim}", ratio=1)

                max_count = max(t_counts.values()) if t_counts else 1
                limit_tools = 2 if mode["is_medium"] else 3
                bar_len = 6 if mode["is_medium"] else 8
                for tool_name, count in sorted(t_counts.items(), key=lambda x: x[1], reverse=True)[:limit_tools]:
                    pct = count / max_count
                    bars = int(pct * bar_len)
                    bar_str = "█" * bars + "░" * (bar_len - bars)
                    act_table.add_row(
                        f" `{tool_name}`",
                        Text(bar_str, style=f"bold {self.theme.accent}"),
                        f"{count}x"
                    )
                content = Group(
                    table,
                    Text("\n 📊 Distribución de Herramientas:", style=f"bold {self.theme.secondary}"),
                    act_table
                )
            else:
                content = table

        return Panel(content, title=title, box=box.ROUNDED, border_style=self.theme.secondary)

    def generate_cognitive_panel(self, summary: dict, mode: dict | None = None) -> Panel:
        if mode is None:
            mode = self.get_layout_mode()
        events = summary.get("recent_events", [])
        last_event = events[-1] if events else {}

        last_tool = last_event.get("tool", "ninguna (en espera)")
        last_route = last_event.get("plc_route", "LOCAL_FAST")
        last_thought = last_event.get("thought_trace", "Sistema listo para clasificar requerimientos o explorar el cerebro.")
        synapses = last_event.get("synapses_fired", [])

        if mode["is_narrow"]:
            title = "[bold]💡 ¿Cómo Piensa?[/bold]"
            header_line = Table.grid(expand=True)
            header_line.add_column(ratio=2)
            header_line.add_column(justify="right", ratio=1)

            short_tool = last_tool.split()[0] if " " in last_tool else last_tool[:10]
            short_route = last_route.replace("LOCAL_FAST", "LOCAL").replace("DELEGATABLE", "DELEG").replace("REQUIRES_ORCHESTRATOR", "ORCH")
            tool_part = Text.assemble(
                ("Acción: ", f"dim {self.theme.dim}"),
                (f"`{short_tool}`", f"bold {self.theme.accent}")
            )
            route_badge = Text.assemble(
                (f"[{short_route}]", f"bold {self.theme.success if 'LOCAL' in last_route else self.theme.warning}")
            )
            header_line.add_row(tool_part, route_badge)

            # Rastro de pensamiento conciso
            thought_text = f"\"{last_thought[:60]}...\"" if len(last_thought) > 60 else f"\"{last_thought}\""
            thought_box = Panel(
                Text(thought_text, style=f"italic {self.theme.text}"),
                title="[dim]Razonamiento[/dim]",
                box=box.ROUNDED,
                border_style=f"dim {self.theme.dim}",
                padding=(0, 1)
            )

            # Sinapsis compactas
            if synapses:
                syn_str = " ──⚡► ".join(f"`⬡ {s[:10]}`" for s in synapses[:2])
                syn_content = Text.assemble(
                    (" 🧬 ", f"bold {self.theme.primary}"),
                    (syn_str, f"bold {self.theme.secondary}")
                )
            else:
                syn_content = Text("   Sin axones disparados aún.", style=f"italic dim {self.theme.dim}")

            content = Group(header_line, thought_box, syn_content)
        else:
            title = "[bold]💡 ¿Cómo Piensa? (Cognición & Sinapsis)[/bold]"
            header_line = Table.grid(expand=True)
            header_line.add_column(ratio=1)
            header_line.add_column(justify="right", ratio=1)

            tool_part = Text.assemble(
                ("Última Acción: ", f"dim {self.theme.dim}"),
                (f"`{last_tool}`", f"bold {self.theme.accent}")
            )
            route_badge = Text.assemble(
                ("Decisión PLC: ", f"dim {self.theme.dim}"),
                (f" [ {last_route} ] ", f"bold {self.theme.success if 'LOCAL' in last_route else self.theme.warning}")
            )
            header_line.add_row(tool_part, route_badge)

            thought_box = Panel(
                Text(f"\"{last_thought}\"", style=f"italic {self.theme.text}"),
                title="[dim]Rastro de Razonamiento del Agente[/dim]",
                box=box.ROUNDED,
                border_style=f"dim {self.theme.dim}",
                padding=(0, 1)
            )

            syn_header = Text(" 🧬 Sinapsis Activas en la Sesión (Regla de Hebb):", style=f"bold {self.theme.primary}")
            if synapses:
                syn_grid = Table.grid(expand=True, padding=(0, 1))
                syn_grid.add_column()
                syn_grid.add_column()
                syn_items = []
                for s in synapses[:4]:
                    syn_items.append(Text.assemble(
                        ("  ⬡ ", f"bold {self.theme.accent}"),
                        (f"[[{s}]]", f"bold {self.theme.secondary}"),
                        (" ──⚡ ", f"dim {self.theme.dim}"),
                        ("(Co-activado)", f"dim {self.theme.success}")
                    ))
                for i in range(0, len(syn_items), 2):
                    if i + 1 < len(syn_items):
                        syn_grid.add_row(syn_items[i], syn_items[i+1])
                    else:
                        syn_grid.add_row(syn_items[i])
                syn_content = syn_grid
            else:
                syn_content = Text("   Sin axones disparados en la última interacción.", style=f"italic dim {self.theme.dim}")

            content = Group(header_line, Text(""), thought_box, Text(""), syn_header, syn_content)

        return Panel(content, title=title, box=box.ROUNDED, border_style=self.theme.primary)

    def generate_orchestration_panel(self, mode: dict | None = None) -> Panel:
        if mode is None:
            mode = self.get_layout_mode()
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)

        if mode["is_narrow"]:
            pipeline = Text.assemble(
                ("[ ⚙️ PLC ] ", f"bold {self.theme.primary}"),
                ("➔ ", f"{self.theme.secondary}"),
                ("[ 🏷️ ODD ] ", f"bold {self.theme.accent}"),
                ("➔ ", f"{self.theme.secondary}"),
                ("[ 🤖 Gentle-PI ] ", f"bold {self.theme.secondary}"),
                ("➔ ", f"{self.theme.secondary}"),
                ("[ 🛡️ Review: Fail-Safe ]", f"bold {self.theme.success}")
            )
            status_line = Text.assemble(
                ("Gentle-AI v3.5.0 ", f"bold {self.theme.text}"),
                ("│ ", f"dim {self.theme.dim}"),
                ("● engram v2.0 ", f"bold {self.theme.success}"),
                ("│ ", f"dim {self.theme.dim}"),
                ("● gentle-shell v3.4.0", f"bold {self.theme.accent}")
            )
            grid.add_row(pipeline)
            grid.add_row(status_line)
            title = "[bold]🔄 Orquestación[/bold]"
        else:
            pipeline = Text.assemble(
                (" [ Petición ] ", f"dim {self.theme.dim}"),
                ("──► ", f"{self.theme.secondary}"),
                ("[ ⚙️ PLC Router ] ", f"bold {self.theme.primary}"),
                ("──► ", f"{self.theme.secondary}"),
                ("[ 🏷️ ODD Classifier ] ", f"bold {self.theme.accent}"),
                ("──► ", f"{self.theme.secondary}"),
                ("[ 🤖 Gentle-PI (TDD Loop) ] ", f"bold {self.theme.secondary}"),
                ("──► ", f"{self.theme.secondary}"),
                ("[ 🛡️ Review Gate: Fail-Safe ]", f"bold {self.theme.success}")
            )
            status_line = Text.assemble(
                ("Ecosistema Gentle-AI: ", f"dim {self.theme.dim}"),
                ("gentle-ai v3.5.0 ", f"bold {self.theme.text}"),
                ("│ ", f"dim {self.theme.dim}"),
                ("● engram v2.0 (conectado) ", f"bold {self.theme.success}"),
                ("│ ", f"dim {self.theme.dim}"),
                ("● gentle-shell v3.4.0 ", f"bold {self.theme.accent}"),
                ("│ ", f"dim {self.theme.dim}"),
                ("● review: fail-safe activo", f"bold {self.theme.success}")
            )
            grid.add_row(pipeline)
            grid.add_row(Text(""))
            grid.add_row(status_line)
            title = "[bold]🔄 Carril de Orquestación en Vivo[/bold]"

        return Panel(grid, title=title, box=box.ROUNDED, border_style=self.theme.accent)

    def render_layout(self) -> Layout:
        summary = self.telemetry.get_summary()
        mode = self.get_layout_mode()

        layout = Layout()
        footer_size = 4 if mode["is_narrow"] or mode["is_compact_height"] else 5
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=footer_size)
        )

        if mode["width"] < 65:
            layout["main"].split_column(
                Layout(name="metrics", ratio=1),
                Layout(name="cognitive", ratio=1)
            )
        else:
            layout["main"].split_row(
                Layout(name="metrics", ratio=1),
                Layout(name="cognitive", ratio=1)
            )

        layout["header"].update(self.generate_header(summary, mode))
        layout["metrics"].update(self.generate_metrics_panel(summary, mode))
        layout["cognitive"].update(self.generate_cognitive_panel(summary, mode))
        layout["footer"].update(self.generate_orchestration_panel(mode))

        return layout

    def run_watch(self, refresh_rate: float = 1.0) -> None:
        """Modo observador pasivo continuo SIN parpadeo (actualiza ante cambios reales o resize)."""
        self.console.clear()
        self.console.print(self.render_layout())
        self.console.print(f"[{self.theme.dim}]👁️ Modo Observador Activo — Monitoreando bus de eventos y redimensionamiento... (Ctrl+C para salir)[/{self.theme.dim}]\n")
        
        last_calls = self.telemetry.total_calls
        last_tokens = self.telemetry.total_in_tokens + self.telemetry.total_out_tokens
        last_size = (self.console.size.width, self.console.size.height)

        try:
            while True:
                time.sleep(refresh_rate)
                # Forzar recarga ligera del snapshot de sesión
                self.telemetry._load_session_stats()
                curr_calls = self.telemetry.total_calls
                curr_tokens = self.telemetry.total_in_tokens + self.telemetry.total_out_tokens
                curr_size = (self.console.size.width, self.console.size.height)

                # Redibujar ante nuevo evento O ante cambio de tamaño de ventana
                if curr_calls != last_calls or curr_tokens != last_tokens or curr_size != last_size:
                    last_calls = curr_calls
                    last_tokens = curr_tokens
                    last_size = curr_size
                    self.console.clear()
                    self.console.print(self.render_layout())
                    self.console.print(f"[{self.theme.dim}]👁️ Actualizado ({datetime.now().strftime('%H:%M:%S')}) — Observador activo ({curr_size[0]}x{curr_size[1]})[/{self.theme.dim}]\n")
        except KeyboardInterrupt:
            self.console.print(f"\n[{self.theme.dim}]Observador detenido.[/{self.theme.dim}]")

    def run_interactive(self) -> None:
        """Modo Workspace interactivo por defecto: Renderiza el HUD estático y despliega el dock de comandos."""
        from cli_shell import DevBrainShell
        shell = DevBrainShell(self.console, config_mgr=self.config_mgr, hud=self)
        shell.run()

    def run_live(self, refresh_rate: float = 0.5, watch: bool = False) -> None:
        """Punto de entrada para devbrain live."""
        if watch:
            self.run_watch(refresh_rate=refresh_rate)
        else:
            self.run_interactive()
