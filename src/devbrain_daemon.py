"""
DevBrain Observer Daemon v4.0:
- Vigila dinámicamente todos los repositorios definidos en `06-SISTEMA/ontologia.yaml` (via ontology_engine).
- Registra commits como Actividades cerradas en Nivel 4 (`cortex.db`) sin crear notas basura en `experimentos/`.
- Escucha cambios incrementales en `ontologia.yaml` y `04-APRENDIZAJES/` con `watchdog` (debounce 2s).
- Regenera `Portada.md` atómicamente y dispara el Snapshot semanal automático cuando han pasado >7 días.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

VAULT_DIR = Path(r"C:\Users\damm1\OneDrive\Documentos\Obsidian Vault")
MCP_DIR = VAULT_DIR / "06-SISTEMA" / "mcp"
SRC_DIR = Path(__file__).resolve().parent
for p in (str(SRC_DIR), str(MCP_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

CACHE_FILE = VAULT_DIR / "06-SISTEMA" / "daemon_git_cache.json"
LOG_FILE = VAULT_DIR / "06-SISTEMA" / "daemon.log"


def _log(msg: str) -> None:
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass


def get_git_head(repo_path: Path):
    try:
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        res = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5, creationflags=flags,
        )
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return None


def get_last_commit_info(repo_path: Path):
    try:
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        res = subprocess.run(
            ["git", "-C", str(repo_path), "log", "-1", "--pretty=format:%h|%an|%s|%cI"],
            capture_output=True, text=True, timeout=5, creationflags=flags,
        )
        if res.returncode == 0 and res.stdout:
            parts = res.stdout.strip().split("|")
            if len(parts) >= 4:
                return {"hash": parts[0], "author": parts[1], "message": parts[2], "date": parts[3]}
    except Exception:
        pass
    return None


def _maybe_weekly_snapshot() -> None:
    try:
        snap_dir = VAULT_DIR / "04-APRENDIZAJES" / "snapshots"
        snap_dir.mkdir(parents=True, exist_ok=True)
        latest_mtime = 0.0
        for f in snap_dir.glob("snapshot-*.md"):
            latest_mtime = max(latest_mtime, f.stat().st_mtime)
        now_ts = time.time()
        age_days = (now_ts - latest_mtime) / 86400.0 if latest_mtime > 0 else 999.0
        is_friday = datetime.now().weekday() == 4
        if age_days >= 7.0 or (is_friday and age_days >= 1.5):
            from weekly_snapshot import WeeklySnapshotEngine
            res = WeeklySnapshotEngine(VAULT_DIR).capture_snapshot()
            _log(f"Snapshot semanal automático generado: {res.get('snapshot_id')}")
    except Exception as e:
        _log(f"Error en weekly snapshot automático: {e}")


def scan_all_repos(vault_dir: Path = VAULT_DIR) -> int:
    """Escanea los repositorios de ontologia.yaml y registra nuevos commits en cortex.db."""
    import ontology_engine as ont
    ont.sync_ontology_yaml(vault_dir=vault_dir)
    repos = ont.list_watched_repos()

    cache = {}
    if CACHE_FILE.exists():
        try:
            cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            cache = {}

    updated_cache = False
    new_commits = 0

    for item in repos:
        rp = Path(item["repo_path"])
        if not (rp / ".git").exists():
            continue
        head = get_git_head(rp)
        if not head:
            continue
        old_head = cache.get(str(rp))
        if old_head and old_head != head:
            info = get_last_commit_info(rp)
            if info:
                ont.manage_activity(
                    action="create",
                    project=item["id"],
                    title=f"Commit {info['hash']}: {info['message'][:120]}",
                    status="done",
                    source="git-commit",
                )
                new_commits += 1
                _log(f"Commit registrado en {item['id']}: {info['hash']} - {info['message'][:80]}")
        if old_head != head:
            cache[str(rp)] = head
            updated_cache = True

    if updated_cache:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")

    if new_commits > 0 or not (vault_dir / "Portada.md").exists():
        ont.render_live_portada(vault_dir)

    return new_commits


def _start_watchdog():
    """Watcher incremental con debounce de 2s sobre ontologia.yaml y 04-APRENDIZAJES/."""
    try:
        from watchdog.events import FileSystemEventHandler  # type: ignore
        from watchdog.observers import Observer  # type: ignore
    except Exception:
        return None

    timer_lock = threading.Lock()
    pending_timer: list = [None]

    def _refresh():
        try:
            import ontology_engine as ont
            from devbrain_index import DevBrainIndex
            ont.sync_ontology_yaml(vault_dir=VAULT_DIR, force=True)
            DevBrainIndex(VAULT_DIR).sync_index(force=False, fast_only=True)
            ont.render_live_portada(VAULT_DIR)
            _log("Watchdog: índice y Portada.md actualizados tras cambio en Vault.")
        except Exception as exc:
            _log(f"Watchdog refresh error: {exc}")

    class _Handler(FileSystemEventHandler):
        def on_any_event(self, event):
            if event.is_directory:
                return
            src = str(getattr(event, "src_path", ""))
            if not (src.endswith(".md") or src.endswith(".yaml")):
                return
            if src.endswith("Portada.md") or src.endswith(".tmp"):
                return
            with timer_lock:
                if pending_timer[0] is not None:
                    pending_timer[0].cancel()
                t = threading.Timer(2.0, _refresh)
                t.daemon = True
                pending_timer[0] = t
                t.start()

    obs = Observer()
    handler = _Handler()
    for target in (VAULT_DIR / "06-SISTEMA", VAULT_DIR / "04-APRENDIZAJES"):
        if target.exists():
            obs.schedule(handler, str(target), recursive=True)
    obs.start()
    return obs


def main():
    _log(f"Daemon v4.0 iniciado (PID {os.getpid()})")
    if "--once" in sys.argv:
        scan_all_repos()
        _maybe_weekly_snapshot()
        return

    observer = _start_watchdog()
    try:
        while True:
            try:
                scan_all_repos()
                _maybe_weekly_snapshot()
            except Exception as e:
                _log(f"Error en ciclo daemon: {e}")
            time.sleep(300)
    finally:
        if observer is not None:
            observer.stop()
            observer.join(timeout=2)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        _log(f"Excepcion fatal: {e}")
