"""
DevBrain Interactive Terminal Shell (v2.0)
Workspace interactivo estilo Gentle-Shell con prompt visual, autocompletado y HUD integrado:
- Visualización estática de alta fidelidad del Cognitive HUD.
- Dock interactivo para ejecutar comandos sin salir de la vista de métricas.
- Soporte para dock questions interactivas, autocompletado y cambio de temas en caliente.
"""
from __future__ import annotations
import sys
import os

if sys.platform == "win32":
    try:
        if hasattr(sys.stdin, "reconfigure"): sys.stdin.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"): sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from pathlib import Path
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.styles import Style
    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False

from cli_theme import ConfigManager, ThemeColors
from telemetry import TelemetryEngine

COMMANDS = [
    "/search", "/memory", "/remember", "/odd", "/feature",
    "/stats", "/doctor", "/theme", "/papa", "/help", "/live", "/refresh", "/exit", "/quit"
]

class DevBrainShell:
    """Shell interactivo para DevBrain."""

    def __init__(self, console: Console | None = None, config_mgr: ConfigManager | None = None, hud = None):
        self.console = console or Console(legacy_windows=False)
        self.config_mgr = config_mgr or ConfigManager()
        self.theme = self.config_mgr.get_theme()
        self.telemetry = TelemetryEngine.get_instance()
        if hud is None:
            from cli_hud import DevBrainHUD
            self.hud = DevBrainHUD(self.console, self.config_mgr)
        else:
            self.hud = hud
        self.running = True

    def render_workspace(self) -> None:
        """Renderiza el HUD completo estático y el dock interactivo sin parpadeo."""
        self.console.clear()
        if self.hud:
            self.hud.theme = self.theme
            self.console.print(self.hud.render_layout())

        dock_grid = Table.grid(expand=True)
        dock_grid.add_column(justify="left", ratio=1)
        dock_text = Text.assemble(
            (" 💬 WORKSPACE DOCK ", f"bold {self.theme.primary}"),
            ("│ ", f"dim {self.theme.dim}"),
            ("Comandos: ", f"dim {self.theme.dim}"),
            ("/search <query>", f"bold {self.theme.accent}"),
            (" • ", f"dim {self.theme.dim}"),
            ("/odd <tarea>", f"bold {self.theme.accent}"),
            (" • ", f"dim {self.theme.dim}"),
            ("/memory <query>", f"bold {self.theme.accent}"),
            (" • ", f"dim {self.theme.dim}"),
            ("/theme <nombre>", f"bold {self.theme.accent}"),
            (" • ", f"dim {self.theme.dim}"),
            ("/help", f"bold {self.theme.accent}"),
            (" │ ", f"dim {self.theme.dim}"),
            ("[Enter vacío = refrescar HUD]", f"italic dim {self.theme.dim}")
        )
        dock_grid.add_row(dock_text)
        self.console.print(Panel(dock_grid, box=box.ROUNDED, border_style=f"dim {self.theme.dim}"))

    def print_banner(self) -> None:
        self.render_workspace()

    def print_help(self) -> None:
        table = Table(title="📖 Comandos Disponibles en DevBrain Shell", box=box.ROUNDED, header_style=f"bold {self.theme.secondary}")
        table.add_column("Comando", style=f"bold {self.theme.accent}", ratio=2)
        table.add_column("Descripción", style=f"{self.theme.text}", ratio=4)

        table.add_row("/search <query>", "Busca notas técnicas en el Vault y base embebida con reranking sináptico.")
        table.add_row("/memory <query>", "Consulta decisiones arquitectónicas en Vault y Engram.")
        table.add_row("/remember <título> | <detalle>", "Guarda una directriz en Vault y sincroniza automáticamente con Engram.")
        table.add_row("/odd <descripción>", "Clasifica una petición bajo el protocolo ODD determinista.")
        table.add_row("/feature <nombre> | <objetivo>", "Genera documento ODD 'odd/tasks/<feature>.md' y espejo Engram.")
        table.add_row("/stats", "Muestra métricas en vivo de tokens consumidos, costo USD y latencias.")
        table.add_row("/doctor", "Ejecuta chequeos de salud de DevBrain, Gentle-AI y Engram.")
        table.add_row("/theme <gentleman|cyberpunk|obsidian|monokai|papa>", "Cambia la paleta de colores de la interfaz.")
        table.add_row("/papa", "Activa/Desactiva el Modo Papa (ahorro de batería y rendimiento).")
        table.add_row("/live, /refresh", "Limpia y redibuja el HUD con las métricas actualizadas.")
        table.add_row("/help [tema]", "Muestra este resumen o ayuda profunda (/help live, odd, mcp, hosts, neuro).")
        table.add_row("/exit, /quit", "Cierra el shell interactivo.")

        self.console.print(table)
        self.console.print(f"[{self.theme.dim}]Tip: Escribe [bold {self.theme.accent}]/help <live|odd|mcp|hosts|neuro>[/bold {self.theme.accent}] para manuales especializados.[/{self.theme.dim}]\n")

    def ask_dock_question(self, question: str, options: list[str]) -> str:
        """Emula el sistema interactivo de preguntas en el dock de Gentle Shell."""
        self.console.print(f"\n[bold {self.theme.accent}]❓ {question}[/bold {self.theme.accent}]")
        for i, opt in enumerate(options, 1):
            self.console.print(f"  [bold {self.theme.secondary}]{i})[/bold {self.theme.secondary}] {opt}")
        self.console.print(f"  [bold {self.theme.dim}]0)[/bold {self.theme.dim}] Escribir respuesta libre...")
        
        choice = input("Selecciona una opción [1-4 / texto]: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        elif choice == "0":
            return input("Tu respuesta personalizada: ").strip()
        return choice or (options[0] if options else "")

    def handle_command(self, raw_input: str) -> None:
        cmd_str = raw_input.strip()
        if not cmd_str:
            self.render_workspace()
            return

        parts = cmd_str.split(" ", 1)
        cmd = parts[0].lower()
        args = parts[1].strip() if len(parts) > 1 else ""

        if cmd in ["/exit", "/quit", "exit", "quit"]:
            self.running = False
            self.console.print(f"[{self.theme.dim}]Cerrando DevBrain Workspace. ¡Hasta la próxima![/{self.theme.dim}]")
            return

        elif cmd in ["/live", "/hud", "/refresh"]:
            self.render_workspace()

        elif cmd == "/help":
            if args:
                from cli_help import render_topic_help
                render_topic_help(self.console, self.theme, args)
            else:
                self.print_help()

        elif cmd == "/stats":
            summary = self.telemetry.get_summary()
            self.console.print(Panel(
                f"• Llamadas totales: [bold]{summary['total_calls']}[/bold]\n"
                f"• Tokens In/Out: [bold]{summary['total_in_tokens']:,}[/bold] / [bold]{summary['total_out_tokens']:,}[/bold]\n"
                f"• Costo acumulado: [bold]${summary['total_cost_usd']:.5f} USD[/bold]\n"
                f"• Latencia p50 / p95: [bold]{summary['p50_latency_ms']} ms[/bold] / [bold]{summary['p95_latency_ms']} ms[/bold]\n"
                f"• Throughput: [bold]{summary['throughput_tps']} tok/s[/bold]\n"
                f"• Cliente activo: [bold]{summary['active_client']}[/bold]",
                title="[bold]⚡ Métricas de Rendimiento[/bold]",
                box=box.ROUNDED,
                border_style=self.theme.secondary
            ))

        elif cmd == "/theme":
            if args:
                if self.config_mgr.set_theme(args):
                    self.theme = self.config_mgr.get_theme()
                    self.console.print(f"[{self.theme.success}]✓ Tema cambiado con éxito a '{self.theme.name}'.[/{self.theme.success}]")
                    self.render_workspace()
                else:
                    self.console.print(f"[{self.theme.danger}]Tema desconocido. Disponibles: gentleman, cyberpunk, obsidian, monokai, papa[/{self.theme.danger}]")
            else:
                self.console.print(f"Tema actual: [bold]{self.theme.name}[/bold]. Usa `/theme <nombre>` para cambiarlo.")

        elif cmd == "/papa":
            is_papa = self.config_mgr.toggle_papa_mode()
            self.theme = self.config_mgr.get_theme()
            state_str = "ENCENDIDO (Modo bajo consumo / sin animaciones)" if is_papa else "APAGADO (Animaciones completas)"
            self.console.print(f"[{self.theme.warning}]Modo Papa: {state_str}[/{self.theme.warning}]")
            self.render_workspace()

        elif cmd == "/doctor":
            self.console.print(f"[{self.theme.secondary}]Ejecutando diagnóstico del ecosistema...[/{self.theme.secondary}]")
            try:
                from devbrain_mcp import handle_audit_project_health
                report = handle_audit_project_health({})
                self.console.print(Panel(report, title="[bold]🩺 Reporte de Salud del Ecosistema[/bold]", box=box.ROUNDED, border_style=self.theme.primary))
            except Exception as e:
                self.console.print(f"[{self.theme.danger}]Error ejecutando doctor: {e}[/{self.theme.danger}]")

        elif cmd == "/search":
            if not args:
                self.console.print(f"[{self.theme.warning}]Uso: /search <concepto o patrón>[/{self.theme.warning}]")
                return
            try:
                from devbrain_mcp import handle_search_knowledge
                res = handle_search_knowledge({"query": args})
                self.console.print(Panel(Markdown(res), title=f"[bold]💡 Búsqueda: '{args}'[/bold]", box=box.ROUNDED, border_style=self.theme.primary))
            except Exception as e:
                self.console.print(f"[{self.theme.danger}]Error en búsqueda: {e}[/{self.theme.danger}]")

        elif cmd == "/memory":
            if not args:
                self.console.print(f"[{self.theme.warning}]Uso: /memory <término>[/{self.theme.warning}]")
                return
            try:
                from devbrain_mcp import handle_recall_memory
                res = handle_recall_memory({"query": args})
                self.console.print(Panel(Markdown(res), title=f"[bold]🧠 Memoria: '{args}'[/bold]", box=box.ROUNDED, border_style=self.theme.secondary))
            except Exception as e:
                self.console.print(f"[{self.theme.danger}]Error en memoria: {e}[/{self.theme.danger}]")

        elif cmd == "/odd":
            if not args:
                self.console.print(f"[{self.theme.warning}]Uso: /odd <descripción de la tarea>[/{self.theme.warning}]")
                return
            try:
                from devbrain_mcp import handle_classify_odd_task
                res = handle_classify_odd_task({"request_description": args})
                self.console.print(Panel(Markdown(res), title="[bold]🏷️ Clasificación ODD[/bold]", box=box.ROUNDED, border_style=self.theme.accent))
            except Exception as e:
                self.console.print(f"[{self.theme.danger}]Error al clasificar ODD: {e}[/{self.theme.danger}]")

        elif cmd == "/remember":
            if "|" not in args:
                self.console.print(f"[{self.theme.warning}]Uso: /remember <título> | <detalle>[/{self.theme.warning}]")
                return
            t_parts = args.split("|", 1)
            title = t_parts[0].strip()
            details = t_parts[1].strip()
            try:
                from devbrain_mcp import handle_remember_decision
                res = handle_remember_decision({"title": title, "details": details})
                self.console.print(f"[{self.theme.success}]✓ {res}[/{self.theme.success}]")
            except Exception as e:
                self.console.print(f"[{self.theme.danger}]Error al guardar memoria: {e}[/{self.theme.danger}]")

        elif cmd == "/feature":
            feature_name = args.split("|")[0].strip() if "|" in args else args
            obj = args.split("|")[1].strip() if "|" in args else "Implementación guiada por ODD"
            if not feature_name:
                self.console.print(f"[{self.theme.warning}]Uso: /feature <nombre> | [objetivo][/{self.theme.warning}]")
                return
            try:
                from devbrain_mcp import handle_prepare_odd_task
                res = handle_prepare_odd_task({"feature_name": feature_name, "objective": obj, "write_to_disk": True})
                self.console.print(Panel(Markdown(res), title=f"[bold]📋 Feature ODD: {feature_name}[/bold]", box=box.ROUNDED, border_style=self.theme.accent))
            except Exception as e:
                self.console.print(f"[{self.theme.danger}]Error preparando feature: {e}[/{self.theme.danger}]")

        else:
            self.console.print(f"[{self.theme.dim}]Comando no reconocido: '{cmd}'. Escribe /help para ver las opciones disponibles.[/{self.theme.dim}]")

    def run(self) -> None:
        self.render_workspace()

        if HAS_PROMPT_TOOLKIT:
            completer = WordCompleter(COMMANDS, ignore_case=True)
            session = PromptSession(completer=completer)
            while self.running:
                try:
                    prompt_str = f"devbrain ❯ "
                    user_input = session.prompt(prompt_str)
                    self.handle_command(user_input)
                except (KeyboardInterrupt, EOFError):
                    break
        else:
            while self.running:
                try:
                    user_input = input("devbrain ❯ ")
                    self.handle_command(user_input)
                except (KeyboardInterrupt, EOFError):
                    break
