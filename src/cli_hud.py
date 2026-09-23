"""
DevBrain Live HUD (v1.0)
Dashboard interactivo de telemetría a 60fps con Rich:
- Indicadores de tokens, latencia, throughput y costo USD en vivo.
- "Cómo Piensa": Trazas cognitivas y decisiones del PLC Router.
- Corteza Sináptica: Mapa de conexiones Hebbianas disparadas.
- Carril de Orquestación Gentle-PI & Review Gate.
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
from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.align import Align

from telemetry import TelemetryEngine
from cli_theme import ConfigManager, ThemeColors

class DevBrainHUD:
    """Dashboard de monitoreo en tiempo real estilo Gentle-Shell para DevBrain."""

    def __init__(self, console: Console | None = None, config_mgr: ConfigManager | None = None):
        self.console = console or Console(legacy_windows=False)
        self.config_mgr = config_mgr or ConfigManager()
        self.telemetry = TelemetryEngine.get_instance()
        self.theme = self.config_mgr.get_theme()

    def generate_header(self, summary: dict) -> Panel:
        client = summary.get("active_client", "Standalone")
        model = summary.get("active_model", "gemini-3.8-flash")
        papa = "ENCENDIDO" if self.config_mgr.config.get("papa_mode") else "APAGADO"
        theme_name = self.theme.name

        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right", ratio=1)

        t_title = Text("🧠 DEVBRAIN v3.0 // NEUROPLASTIC COGNITIVE HUD", style=f"bold {self.theme.primary}")
        t_center = Text.assemble(
            ("HOST: ", f"dim {self.theme.dim}"),
            (client, f"bold {self.theme.secondary}"),
            ("  •  MODELO: ", f"dim {self.theme.dim}"),
            (model, f"bold {self.theme.accent}")
        )
        t_right = Text.assemble(
            ("TEMA: ", f"dim {self.theme.dim}"),
            (theme_name, f"bold {self.theme.secondary}"),
            ("  •  MODO PAPA: ", f"dim {self.theme.dim}"),
            (papa, f"bold {self.theme.warning if papa == 'ENCENDIDO' else self.theme.success}")
        )

        grid.add_row(t_title, t_center, t_right)
        return Panel(grid, style=f"{self.theme.primary}", border_style=self.theme.primary)

    def generate_metrics_panel(self, summary: dict) -> Panel:
        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(justify="left", style=f"bold {self.theme.text}")
        table.add_column(justify="right", style=f"bold {self.theme.accent}")

        in_tok = summary.get("total_in_tokens", 0)
        out_tok = summary.get("total_out_tokens", 0)
        tot_tok = summary.get("total_tokens", 0)
        cost = summary.get("total_cost_usd", 0.0)
        tps = summary.get("throughput_tps", 0.0)
        p50 = summary.get("p50_latency_ms", 0.0)
        p95 = summary.get("p95_latency_ms", 0.0)
        calls = summary.get("total_calls", 0)

        table.add_row("🔢 Llamadas Totales MCP:", f"{calls}")
        table.add_row("📥 Tokens Entrada (In):", f"{in_tok:,}")
        table.add_row("📤 Tokens Salida (Out):", f"{out_tok:,}")
        table.add_row("⚡ Tokens Totales:", f"{tot_tok:,}")
        table.add_row("💵 Costo Estimado (USD):", f"${cost:.5f}")
        table.add_row("🚀 Throughput:", f"{tps} tok/s")
        table.add_row("⏱️ Latencia Media (p50):", f"{p50} ms")
        table.add_row("⚠️ Latencia Cola (p95):", f"{p95} ms")

        # Desglose de herramientas top
        t_counts = summary.get("tool_counts", {})
        if t_counts:
            tool_subtable = Table(box=None, expand=True, show_header=True, header_style=f"bold {self.theme.secondary}")
            tool_subtable.add_column("Herramienta Top", ratio=2)
            tool_subtable.add_column("Uso", justify="right", ratio=1)
            sorted_tools = sorted(t_counts.items(), key=lambda x: x[1], reverse=True)[:4]
            for tool_name, count in sorted_tools:
                tool_subtable.add_row(f"`{tool_name}`", str(count))
            content = Group(table, Text("\n📊 Actividad de Herramientas:", style=f"bold {self.theme.secondary}"), tool_subtable)
        else:
            content = table

        return Panel(content, title="[bold]⚡ Métricas de Rendimiento & Tokens[/bold]", border_style=self.theme.secondary)

    def generate_cognitive_panel(self, summary: dict) -> Panel:
        events = summary.get("recent_events", [])
        last_event = events[-1] if events else {}

        last_tool = last_event.get("tool", "ninguna")
        last_route = last_event.get("plc_route", "LOCAL_FAST")
        last_thought = last_event.get("thought_trace", "Sistema en espera de peticiones del agente.")
        synapses = last_event.get("synapses_fired", [])

        thought_text = Text()
        thought_text.append("Última Acción: ", style=f"dim {self.theme.dim}")
        thought_text.append(f"{last_tool}\n", style=f"bold {self.theme.accent}")

        thought_text.append("Decisión PLC: ", style=f"dim {self.theme.dim}")
        thought_text.append(f"[{last_route}]\n", style=f"bold {self.theme.success if 'LOCAL' in last_route else self.theme.warning}")

        thought_text.append("Rastro de Razonamiento: ", style=f"dim {self.theme.dim}")
        thought_text.append(f"{last_thought}\n\n", style=f"{self.theme.text}")

        # Visualización sináptica
        syn_header = Text("🧬 Sinapsis Activas en la Sesión:\n", style=f"bold {self.theme.primary}")
        if synapses:
            syn_body = Text()
            for s in synapses[:5]:
                syn_body.append(f"  • [[{s}]] ", style=f"bold {self.theme.secondary}")
                syn_body.append("⚡ (Co-activado Hebb)\n", style=f"dim {self.theme.dim}")
        else:
            syn_body = Text("  Sin sinapsis disparadas en la última consulta.", style=f"italic {self.theme.dim}")

        content = Group(thought_text, syn_header, syn_body)
        return Panel(content, title="[bold]💡 ¿Cómo Piensa? (Cognición & Sinapsis)[/bold]", border_style=self.theme.primary)

    def generate_orchestration_panel(self) -> Panel:
        lane = Table.grid(expand=True)
        lane.add_column(justify="center", ratio=1)

        pipeline = Text.assemble(
            ("Petición ", f"dim {self.theme.dim}"),
            ("──► ", f"{self.theme.secondary}"),
            ("[PLC Router] ", f"bold {self.theme.primary}"),
            ("──► ", f"{self.theme.secondary}"),
            ("[ODD Classifier] ", f"bold {self.theme.accent}"),
            ("──► ", f"{self.theme.secondary}"),
            ("[Gentle-PI: explore ──► worker(TDD) ──► verify] ", f"bold {self.theme.secondary}"),
            ("──► ", f"{self.theme.secondary}"),
            ("[Review Gate: fail-safe] ", f"bold {self.theme.success}")
        )

        status_line = Text.assemble(
            ("Ecosistema Gentle-AI: ", f"dim {self.theme.dim}"),
            ("gentle-ai v3.1.0 ", f"bold {self.theme.text}"),
            ("• ", f"{self.theme.dim}"),
            ("engram v2.0.0 (conectado) ", f"bold {self.theme.success}"),
            ("• ", f"{self.theme.dim}"),
            ("gentle-shell v3.4.0 (dock questions listo)", f"bold {self.theme.accent}")
        )

        lane.add_row(pipeline)
        lane.add_row(Text(""))
        lane.add_row(status_line)

        return Panel(lane, title="[bold]🔄 Carril de Orquestación en Vivo[/bold]", border_style=self.theme.accent)

    def render_layout(self) -> Layout:
        summary = self.telemetry.get_summary()

        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=5)
        )
        layout["main"].split_row(
            Layout(name="metrics", ratio=1),
            Layout(name="cognitive", ratio=1)
        )

        layout["header"].update(self.generate_header(summary))
        layout["metrics"].update(self.generate_metrics_panel(summary))
        layout["cognitive"].update(self.generate_cognitive_panel(summary))
        layout["footer"].update(self.generate_orchestration_panel())

        return layout

    def run_live(self, refresh_rate: float = 0.5) -> None:
        """Bucle interactivo del HUD en vivo."""
        self.console.clear()
        with Live(self.render_layout(), console=self.console, refresh_per_second=int(1.0 / refresh_rate), screen=True) as live:
            try:
                while True:
                    time.sleep(refresh_rate)
                    live.update(self.render_layout())
            except KeyboardInterrupt:
                pass
