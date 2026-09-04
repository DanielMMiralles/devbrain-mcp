"""
DevBrain Observer Daemon: Monitorea en segundo plano tus proyectos insignia reales.
Aprende de ti detectando nuevos commits, cambios de arquitectura y resoluciones de bugs.
"""
import time
import subprocess
import json
import os
import sys
from datetime import datetime
from pathlib import Path

VAULT_DIR = Path(os.getenv("VAULT_DIR", r"C:\Users\damm1\OneDrive\Documentos\Obsidian Vault"))
LEARNING_DIR = VAULT_DIR / "04-APRENDIZAJES" / "experimentos"
CACHE_FILE = VAULT_DIR / "06-SISTEMA" / "daemon_git_cache.json"

# Proyectos Insignia Reales (configurables via PROJECTS_CONFIG o escaneo)
DEFAULT_WATCHED_DIRS = [
    Path(r"C:\Users\damm1\OneDrive\Escritorio\alia-log-api"),
    Path(r"C:\Users\damm1\OneDrive\Escritorio\alia-log-frontend"),
    Path(r"C:\Users\damm1\OneDrive\Escritorio\Alia_LangGraph"),
    Path(r"C:\Users\damm1\OneDrive\Escritorio\Chambita"),
    Path(r"C:\Users\damm1\OneDrive\Escritorio\Chambita App"),
    Path(r"C:\Users\damm1\OneDrive\Escritorio\Demo LandingPageChambita"),
    Path(r"C:\Users\damm1\OneDrive\Escritorio\Narval-SGN"),
    Path(r"C:\Users\damm1\OneDrive\Escritorio\Odysseus"),
    Path(r"C:\Users\damm1\OneDrive\Escritorio\alaorden_web"),
    Path(r"C:\Users\damm1\OneDrive\Escritorio\IMA_Landgraph"),
    Path(r"C:\Users\damm1\mayan-edms")
]

def load_watched_dirs():
    config_env = os.getenv("PROJECTS_CONFIG")
    candidates = []
    if config_env and Path(config_env).exists():
        candidates.append(Path(config_env))
    candidates.extend([
        Path(__file__).resolve().parent.parent.parent / "config" / "projects.json",
        VAULT_DIR / "06-SISTEMA" / "config" / "projects.json",
    ])
    for cfg in candidates:
        if cfg.exists():
            try:
                with open(cfg, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    dirs = [Path(p["path"]) for p in data.get("projects", []) if "path" in p]
                    if dirs:
                        return dirs
            except Exception:
                pass
    # Si PROJECTS_DIR esta montado (e.g. en Docker), escanear sus subdirectorios
    projects_env = os.getenv("PROJECTS_DIR")
    if projects_env and Path(projects_env).exists():
        found = [p for p in Path(projects_env).iterdir() if p.is_dir() and (p / ".git").exists()]
        if found:
            return found
    return [p for p in DEFAULT_WATCHED_DIRS if p.exists()] or DEFAULT_WATCHED_DIRS

WATCHED_DIRS = load_watched_dirs()

def get_git_head(repo_path: Path):
    try:
        res = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5
        )
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return None

def get_last_commit_info(repo_path: Path):
    try:
        res = subprocess.run(
            ["git", "-C", str(repo_path), "log", "-1", "--pretty=format:%h|%an|%s|%cI"],
            capture_output=True, text=True, timeout=5
        )
        if res.returncode == 0 and res.stdout:
            parts = res.stdout.strip().split("|")
            return {
                "hash": parts[0],
                "author": parts[1],
                "message": parts[2],
                "date": parts[3]
            }
    except Exception:
        pass
    return None

def process_new_commit(repo_name: str, info: dict):
    LEARNING_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    note_name = f"learning-{today}-{repo_name}-{info['hash']}.md"
    note_path = LEARNING_DIR / note_name

    msg = info["message"]
    tipo = "General"
    if msg.startswith("feat"): tipo = "Nueva Característica"
    elif msg.startswith("fix"): tipo = "Corrección de Error"
    elif msg.startswith("refactor"): tipo = "Refactorización de Arquitectura"

    content = f"""---
tags: [aprendizaje, autodiscovered, commit]
proyecto: "[[{repo_name}]]"
fecha: {today}
commit_hash: "{info['hash']}"
tipo_cambio: "{tipo}"
---

# 💡 Aprendizaje de Sesión: {repo_name} ({info['hash']})

## Mensaje Registrado
> **{msg}**

## Contexto de Trabajo
- **Proyecto**: [[{repo_name}]]
- **Tipo Detectado**: {tipo}
- **Fecha**: {info['date']}
- **Autor**: {info['author']}

## Notas de Evolución Personal
- ¿Qué patrón, técnica o convención se aplicó en este commit?
- ¿Afecta a alguna especificación en [[specs]]?
"""
    note_path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Aprendizaje capturado de {repo_name}: {msg}")

def scan_all_repos():
    cache = {}
    if CACHE_FILE.exists():
        try:
            cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            cache = {}

    updated = False
    for candidate in WATCHED_DIRS:
        if not candidate.exists():
            continue
        
        repos = []
        if (candidate / ".git").exists():
            repos.append(candidate)
        else:
            try:
                for sub in candidate.iterdir():
                    if sub.is_dir() and (sub / ".git").exists():
                        repos.append(sub)
            except Exception:
                pass

        for r in repos:
            head = get_git_head(r)
            if head:
                old_head = cache.get(str(r))
                if old_head and old_head != head:
                    info = get_last_commit_info(r)
                    if info:
                        process_new_commit(r.name, info)
                cache[str(r)] = head
                updated = True

    if updated:
        CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding="utf-8")

def main():
    if "--once" in sys.argv:
        scan_all_repos()
        return

    print("DevBrain Observer Daemon iniciado en segundo plano (Monitoreo cada 60s)...")
    while True:
        try:
            scan_all_repos()
        except Exception as e:
            pass
        time.sleep(60)

if __name__ == "__main__":
    main()