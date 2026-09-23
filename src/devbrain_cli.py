"""
DevBrain Unified Native CLI (v1.0)
Entry point principal para DevBrain: HUD en vivo, Shell interactivo, estadísticas y doctor.
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

import argparse
from pathlib import Path

# Añadir src al path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from cli_theme import ConfigManager
from telemetry import TelemetryEngine

def main():
    console = Console(legacy_windows=False)
    config_mgr = ConfigManager()

    parser = argparse.ArgumentParser(
        prog="devbrain",
        description="🧠 DevBrain Native CLI — Controlador PLC, Neuroplasticidad & Telemetría en Vivo"
    )
    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")

    # devbrain live / hud
    live_parser = subparsers.add_parser("live", aliases=["hud"], help="Inicia el HUD de telemetría y observación en tiempo real a 60fps")
    live_parser.add_argument("--rate", type=float, default=0.5, help="Frecuencia de refresco en segundos (default: 0.5s)")
    live_parser.add_argument("--papa", action="store_true", help="Forzar Modo Papa (ahorro de batería / sin animaciones)")
    live_parser.add_argument("--once", action="store_true", help="Renderizar una sola captura del HUD y salir")

    # devbrain shell
    subparsers.add_parser("shell", help="Inicia la terminal interactiva de DevBrain con prompt visual")

    # devbrain stats
    subparsers.add_parser("stats", help="Muestra el resumen de consumo de tokens, costo USD y latencias")

    # devbrain doctor
    subparsers.add_parser("doctor", help="Ejecuta diagnóstico de salud unificado (DevBrain + Gentle-AI + Engram)")

    # devbrain search
    search_parser = subparsers.add_parser("search", help="Búsqueda rápida en el Vault y base de conocimiento")
    search_parser.add_argument("query", help="Término o concepto a buscar")

    # devbrain memory
    mem_parser = subparsers.add_parser("memory", help="Búsqueda rápida de decisiones y reglas en memoria persistente")
    mem_parser.add_argument("query", help="Término o proyecto a buscar")

    # devbrain odd
    odd_parser = subparsers.add_parser("odd", help="Clasificación determinista de requerimientos bajo protocolo ODD")
    odd_parser.add_argument("description", help="Descripción de la tarea a evaluar")

    # devbrain theme
    theme_parser = subparsers.add_parser("theme", help="Cambia o consulta el tema visual del CLI")
    theme_parser.add_argument("name", nargs="?", help="Nombre del tema (gentleman, cyberpunk, obsidian, monokai, papa)")

    # devbrain papa
    subparsers.add_parser("papa", help="Alterna el Modo Papa de bajo consumo")

    # devbrain help
    help_parser = subparsers.add_parser("help", help="Muestra la guía completa de comandos, tópicos y arquitectura")
    help_parser.add_argument("topic", nargs="?", default=None, help="Tópico específico (live, odd, mcp, hosts, neuro, shell)")

    def custom_print_help():
        from cli_help import render_help_overview
        theme = config_mgr.get_theme()
        render_help_overview(console, theme)

    parser.print_help = custom_print_help

    args = parser.parse_args()

    # Si se invoca sin argumentos, abrir shell por defecto
    if not args.command or args.command == "shell":
        from cli_shell import DevBrainShell
        shell = DevBrainShell(console)
        shell.run()
        return

    if args.command in ["live", "hud"]:
        from cli_hud import DevBrainHUD
        if getattr(args, "papa", False):
            config_mgr.config["papa_mode"] = True
        hud = DevBrainHUD(console, config_mgr)
        if getattr(args, "once", False):
            console.print(hud.render_layout())
        else:
            hud.run_live(refresh_rate=args.rate)

    elif args.command == "stats":
        telemetry = TelemetryEngine.get_instance()
        summary = telemetry.get_summary()
        theme = config_mgr.get_theme()
        
        table = Table(title="⚡ Resumen de Métricas de DevBrain", box=None, header_style=f"bold {theme.secondary}")
        table.add_column("Métrica", style=f"bold {theme.accent}")
        table.add_column("Valor", style=f"{theme.text}")

        table.add_row("Cliente Activo", summary["active_client"])
        table.add_row("Modelo Predeterminado", summary["active_model"])
        table.add_row("Llamadas MCP Registradas", str(summary["total_calls"]))
        table.add_row("Tokens Entrada (In)", f"{summary['total_in_tokens']:,}")
        table.add_row("Tokens Salida (Out)", f"{summary['total_out_tokens']:,}")
        table.add_row("Tokens Totales", f"{summary['total_tokens']:,}")
        table.add_row("Costo Estimado en Sesión", f"${summary['total_cost_usd']:.5f} USD")
        table.add_row("Throughput", f"{summary['throughput_tps']} tokens/seg")
        table.add_row("Latencia p50 (Media)", f"{summary['p50_latency_ms']} ms")
        table.add_row("Latencia p95 (Cola)", f"{summary['p95_latency_ms']} ms")

        console.print(Panel(table, border_style=theme.primary))

    elif args.command == "doctor":
        theme = config_mgr.get_theme()
        console.print(f"[{theme.secondary}]Ejecutando diagnóstico del ecosistema DevBrain + Gentle-AI...[/{theme.secondary}]")
        from devbrain_mcp import handle_audit_project_health
        report = handle_audit_project_health({})
        console.print(Panel(report, title="[bold]🩺 Diagnóstico Oficial del Ecosistema[/bold]", border_style=theme.primary))

    elif args.command == "search":
        from devbrain_mcp import handle_search_knowledge
        res = handle_search_knowledge({"query": args.query})
        console.print(Panel(Markdown(res), title=f"💡 Búsqueda: '{args.query}'", border_style="cyan"))

    elif args.command == "memory":
        from devbrain_mcp import handle_recall_memory
        res = handle_recall_memory({"query": args.query})
        console.print(Panel(Markdown(res), title=f"🧠 Memoria: '{args.query}'", border_style="magenta"))

    elif args.command == "odd":
        from devbrain_mcp import handle_classify_odd_task
        res = handle_classify_odd_task({"request_description": args.description})
        console.print(Panel(Markdown(res), title="🏷️ Clasificación ODD", border_style="yellow"))

    elif args.command == "theme":
        if args.name:
            if config_mgr.set_theme(args.name):
                theme = config_mgr.get_theme()
                console.print(f"[green]✓ Tema cambiado a '{theme.name}'.[/green]")
            else:
                console.print("[red]Tema desconocido. Opciones: gentleman, cyberpunk, obsidian, monokai, papa[/red]")
        else:
            theme = config_mgr.get_theme()
            console.print(f"Tema actual: [bold]{theme.name}[/bold]. Usa `devbrain theme <nombre>` para cambiar.")

    elif args.command == "papa":
        is_papa = config_mgr.toggle_papa_mode()
        state = "ENCENDIDO (ahorro de batería / sin animaciones)" if is_papa else "APAGADO (animaciones completas)"
        console.print(f"[yellow]Modo Papa: {state}[/yellow]")

    elif args.command == "help":
        from cli_help import render_help_overview, render_topic_help
        theme = config_mgr.get_theme()
        if getattr(args, "topic", None):
            render_topic_help(console, theme, args.topic)
        else:
            render_help_overview(console, theme)

if __name__ == "__main__":
    main()
