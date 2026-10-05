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

from rich import box
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
    live_parser = subparsers.add_parser("live", aliases=["hud"], help="Inicia el Cognitive HUD en vivo (Workspace interactivo o --watch)")
    live_parser.add_argument("--rate", type=float, default=1.0, help="Frecuencia de sondeo en segundos (default: 1.0s)")
    live_parser.add_argument("--papa", action="store_true", help="Forzar Modo Papa (ahorro de batería / sin animaciones)")
    live_parser.add_argument("--once", action="store_true", help="Renderizar una sola captura del HUD y salir")
    live_parser.add_argument("--watch", "-w", action="store_true", help="Modo observador pasivo continuo sin prompt interactivo")

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

    # devbrain brain
    brain_parser = subparsers.add_parser("brain", help="Inicia el servidor WebGL 3D Cortex (19,000 neuronas a 60fps) y abre el navegador")
    brain_parser.add_argument("--port", type=int, default=8765, help="Puerto HTTP local (default: 8765)")
    brain_parser.add_argument("--no-open", action="store_true", help="No abrir automáticamente el navegador")

    # devbrain cortex / health
    cortex_parser = subparsers.add_parser("cortex", aliases=["health"], help="Audita la salud del cortex: enlaces rotos, duplicados y notas viejas (LTD)")
    cortex_parser.add_argument("--prune", action="store_true", help="Podar automáticamente sinapsis residuales débiles (<0.1)")

    # devbrain sleep / dream
    subparsers.add_parser("sleep", aliases=["dream"], help="Ejecuta el ciclo de sueño y consolidación sináptica de DevBrain")

    # devbrain compress / tokens / optimize
    comp_parser = subparsers.add_parser("compress", aliases=["tokens", "optimize"], help="Optimiza y comprime contexto (AST slicing, chunking sináptico o deduplicación)")
    comp_parser.add_argument("target", help="Ruta al archivo o texto a optimizar")
    comp_parser.add_argument("--mode", choices=["code", "knowledge", "session", "auto"], default="auto", help="Estrategia de compresión")
    comp_parser.add_argument("--tokens", type=int, default=800, help="Presupuesto máximo de tokens objetivo")
    comp_parser.add_argument("--focus", default="", help="Símbolo o concepto clave prioritario")

    # devbrain theme
    theme_parser = subparsers.add_parser("theme", help="Cambia o consulta el tema visual del CLI")
    theme_parser.add_argument("name", nargs="?", help="Nombre del tema (gentleman, cyberpunk, obsidian, monokai, papa)")

    # devbrain papa
    subparsers.add_parser("papa", help="Alterna el Modo Papa de bajo consumo")

    # devbrain help
    help_parser = subparsers.add_parser("help", help="Muestra la guía completa de comandos, tópicos y arquitectura")
    help_parser.add_argument("topic", nargs="?", default=None, help="Tópico específico (live, odd, mcp, hosts, neuro, shell, brain, tokens)")

    # devbrain ask / agente directo
    ask_parser = subparsers.add_parser("ask", help="Consulta en lenguaje natural al Agente Cognitivo DevBrain")
    ask_parser.add_argument("prompt", nargs="+", help="Pregunta, requerimiento o instrucción")

    # devbrain snapshot / foto
    snap_parser = subparsers.add_parser("snapshot", aliases=["foto"], help="Captura el snapshot semanal (Foto de los Viernes) y actualiza Portada.md")
    snap_parser.add_argument("--verdict", "-v", default="", help="Veredicto o síntesis opcional del Editor en Jefe")
    snap_parser.add_argument("--json", action="store_true", help="Salida en formato JSON crudo")

    def custom_print_help():
        from cli_help import render_help_overview
        theme = config_mgr.get_theme()
        render_help_overview(console, theme)

    parser.print_help = custom_print_help

    # Si se pasa texto libre que no es subcomando, auto-enrutar a 'ask'
    known_commands = list(subparsers.choices.keys()) + [
        "-h", "--help", "-v", "--version", "hud", "health", "dream", "tokens", "optimize"
    ]
    if len(sys.argv) > 1 and sys.argv[1] not in known_commands and not sys.argv[1].startswith("-"):
        sys.argv.insert(1, "ask")

    args = parser.parse_args()

    # Si se invoca sin argumentos, abrir shell por defecto
    if not args.command or args.command == "shell":
        from cli_shell import DevBrainShell
        shell = DevBrainShell(console)
        shell.run()
        return

    if args.command == "ask":
        from agentic_engine import DevBrainAgent
        agent = DevBrainAgent(config_mgr)
        prompt_text = " ".join(args.prompt)
        theme = config_mgr.get_theme()
        with console.status(f"[bold {theme.accent}]🧠 DevBrain procesando con neuroplasticidad...[/bold {theme.accent}]"):
            res = agent.process_prompt(prompt_text)

        route_badge = f"[bold {theme.primary}][Ruta PLC: {res.plc_route}][/bold {theme.primary}]"
        intent_badge = f"[dim {theme.dim}][{res.intent}][/dim {theme.dim}]"
        title = f"🤖 [bold]DevBrain Agent[/bold] {route_badge} {intent_badge}"
        footer_text = f"⚡ {res.latency_ms:.0f} ms │ Tokens: {res.tokens_in}/{res.tokens_out} │ Sinapsis: {len(res.synapses_fired)} │ {res.provider_used}"

        console.print(Panel(
            Markdown(res.content),
            title=title,
            subtitle=footer_text,
            box=box.ROUNDED,
            border_style=theme.secondary,
            padding=(1, 2)
        ))
        return

    if args.command in ["live", "hud"]:
        from cli_hud import DevBrainHUD
        if getattr(args, "papa", False):
            config_mgr.config["papa_mode"] = True
        hud = DevBrainHUD(console, config_mgr)
        if getattr(args, "once", False):
            console.print(hud.render_layout())
        elif getattr(args, "watch", False):
            hud.run_watch(refresh_rate=args.rate)
        else:
            hud.run_interactive()

    elif args.command == "stats":
        telemetry = TelemetryEngine.get_instance()
        summary = telemetry.get_summary()
        theme = config_mgr.get_theme()
        
        table = Table(title="⚡ Resumen de Métricas de DevBrain", box=box.ROUNDED, header_style=f"bold {theme.secondary}")
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

        console.print(Panel(table, box=box.ROUNDED, border_style=theme.primary))

    elif args.command == "doctor":
        theme = config_mgr.get_theme()
        console.print(f"[{theme.secondary}]Ejecutando diagnóstico del ecosistema DevBrain + Gentle-AI...[/{theme.secondary}]")
        from devbrain_mcp import handle_audit_project_health
        report = handle_audit_project_health({})
        console.print(Panel(report, title="[bold]🩺 Diagnóstico Oficial del Ecosistema[/bold]", box=box.ROUNDED, border_style=theme.primary))

    elif args.command == "search":
        from devbrain_mcp import handle_search_knowledge
        res = handle_search_knowledge({"query": args.query})
        console.print(Panel(Markdown(res), title=f"💡 Búsqueda: '{args.query}'", box=box.ROUNDED, border_style="cyan"))

    elif args.command == "memory":
        from devbrain_mcp import handle_recall_memory
        res = handle_recall_memory({"query": args.query})
        console.print(Panel(Markdown(res), title=f"🧠 Memoria: '{args.query}'", box=box.ROUNDED, border_style="magenta"))

    elif args.command == "odd":
        from devbrain_mcp import handle_classify_odd_task
        res = handle_classify_odd_task({"request_description": args.description})
        console.print(Panel(Markdown(res), title="🏷️ Clasificación ODD", box=box.ROUNDED, border_style="yellow"))

    elif args.command == "brain":
        theme = config_mgr.get_theme()
        port = getattr(args, "port", 8765)
        no_open = getattr(args, "no_open", False)
        console.print(Panel(
            f"🧠 [bold {theme.primary}]DevBrain 3D Cortex Server[/bold {theme.primary}]\n\n"
            f"• Visualizador WebGL 3D: [bold cyan]http://localhost:{port}[/bold cyan]\n"
            f"• Neuronas en Grafo: [bold]19,000[/bold] a 60 FPS\n"
            f"• Event Bus SSE: [dim]~/.devbrain/live_events.jsonl[/dim]\n"
            f"• Presiona [bold red]Ctrl+C[/bold red] para detener el servidor.",
            box=box.ROUNDED,
            border_style=theme.secondary,
            title="🌌 [bold]3D Cortex Engine[/bold]"
        ))
        from cortex_server import run_server
        try:
            run_server(port=port, open_browser=not no_open)
        except KeyboardInterrupt:
            console.print(f"\n[{theme.dim}]Servidor 3D Cortex detenido.[/{theme.dim}]")

    elif args.command in ["cortex", "health"]:
        from devbrain_mcp import handle_audit_cortex_health
        theme = config_mgr.get_theme()
        with console.status(f"[{theme.secondary}]Auditando enlaces rotos, duplicados y salud del Cortex...[/{theme.secondary}]"):
            res = handle_audit_cortex_health({"auto_prune": getattr(args, "prune", False)})
        console.print(Panel(Markdown(res), title="🧠 [bold]Auditoría de Salud del Cortex[/bold]", box=box.ROUNDED, border_style=theme.primary))

    elif args.command in ["sleep", "dream"]:
        theme = config_mgr.get_theme()
        from devbrain_mcp import VAULT_DIR, INDEXER
        from cortex_housekeeper import CortexHousekeeper
        hk = CortexHousekeeper(VAULT_DIR, db_path=INDEXER.db_path if INDEXER else None)
        with console.status(f"[{theme.accent}]Consolidando sinapsis y optimizando memoria (Modo Sueño)...[/{theme.accent}]"):
            res = hk.consolidate_dream_cycle()

        table = Table(box=box.ROUNDED, header_style=f"bold {theme.secondary}")
        table.add_column("Métrica de Reposo", style=f"bold {theme.accent}")
        table.add_column("Resultado", style=f"{theme.text}")
        table.add_row("Estado", f"[green]{res.get('status')}[/green]")
        table.add_row("Sinapsis Decaídas (LTD)", str(res.get("decayed_synapses", 0)))
        table.add_row("Optimización SQLite / FTS", "Completada" if res.get("optimized_sqlite") else "Omitida")
        table.add_row("Tiempo de Consolidación", f"{res.get('elapsed_ms', 0)} ms")
        table.add_row("Diagnóstico", res.get("message", ""))
        console.print(Panel(table, title="🌙 [bold]DevBrain — Ciclo de Consolidación & Sueño[/bold]", box=box.ROUNDED, border_style=theme.secondary))

    elif args.command in ["compress", "tokens", "optimize"]:
        theme = config_mgr.get_theme()
        from devbrain_mcp import handle_optimize_token_budget
        target = args.target
        target_p = Path(target)
        if target_p.exists() and target_p.is_file():
            try:
                target_text = target_p.read_text(encoding="utf-8", errors="replace")
                lang = "python" if target.endswith(".py") else ("typescript" if target.endswith((".ts", ".tsx")) else "auto")
            except Exception as e:
                console.print(f"[red]Error leyendo archivo: {e}[/red]")
                return
        else:
            target_text = target
            lang = "auto"

        mode = args.mode
        if mode == "auto":
            mode = "code" if (target.endswith((".py", ".ts", ".js", ".tsx")) or "def " in target_text or "class " in target_text or "function" in target_text) else "knowledge"

        with console.status(f"[{theme.accent}]Optimizando contexto mediante AST slicing & token budget...[/{theme.accent}]"):
            res = handle_optimize_token_budget({
                "target_text": target_text,
                "context_type": mode,
                "max_tokens": args.tokens,
                "language": lang,
                "focus_symbol": args.focus
            })
        console.print(Panel(Markdown(res), title="⚡ [bold]Compresión & Optimización de Tokens[/bold]", box=box.ROUNDED, border_style=theme.accent))

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

    elif args.command in ["snapshot", "foto"]:
        theme = config_mgr.get_theme()
        from weekly_snapshot import WeeklySnapshotEngine
        from devbrain_mcp import VAULT_DIR
        with console.status(f"[{theme.accent}]Capturando snapshot semanal y actualizando Portada.md...[/{theme.accent}]"):
            engine = WeeklySnapshotEngine(VAULT_DIR)
            res = engine.capture_snapshot(custom_verdict=args.verdict)
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            console.print(Panel(Markdown(res["markdown_snippet"]), title=f"📸 [bold]Snapshot Semanal {res['snapshot_id']}[/bold]", box=box.ROUNDED, border_style=theme.accent))
            console.print(f"[{theme.dim}]✓ Archivado en: {res['archive_path']}[/{theme.dim}]")

    elif args.command == "help":
        from cli_help import render_help_overview, render_topic_help
        theme = config_mgr.get_theme()
        if getattr(args, "topic", None):
            render_topic_help(console, theme, args.topic)
        else:
            render_help_overview(console, theme)

if __name__ == "__main__":
    main()
