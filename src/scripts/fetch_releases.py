"""
Monitorea releases en GitHub de herramientas clave del stack.
Genera notas en 00-INBOX/auto/releases/ para alertar de cambios y nuevas versiones.
"""
import urllib.request
import json
from datetime import datetime, timedelta
from pathlib import Path

REPOS = [
    "tiangolo/fastapi",
    "nestjs/nest",
    "langchain-ai/langgraph",
    "n8n-io/n8n",
    "tailwindlabs/tailwindcss",
    "shadcn-ui/ui",
    "docker/compose"
]

VAULT = Path(str(Path.home() / "ObsidianVault"))
OUT_DIR = VAULT / "00-INBOX" / "auto" / "releases"

def run():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": "DevBrain-Agent-Updater", "Accept": "application/vnd.github.v3+json"}
    
    print("Verificando releases de repositorios...")
    for repo in REPOS:
        url = f"https://api.github.com/repos/{repo}/releases/latest"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                tag = data.get("tag_name", "")
                name = repo.split("/")[1]
                body = (data.get("body", "") or "")[:1500]
                html_url = data.get("html_url", "")
                
                fname = f"release-{name}-{tag}.md".replace("/", "-").replace(":", "-")
                note_file = OUT_DIR / fname
                
                content = f"""---
tags: [inbox, release, {name}]
herramienta: "[[{name}]]"
version: "{tag}"
fecha: {datetime.now().strftime('%Y-%m-%d')}
---

# 🚀 Nueva Versión: {name} {tag}

## Enlace Oficial
- [Ver Release en GitHub]({html_url})

## Resumen de Cambios
{body}

## Tareas Relacionadas
- [ ] Evaluar si introduce breaking changes para mis proyectos activos.
"""
                note_file.write_text(content.strip() + "\n", encoding="utf-8")
                print(f"  -> Release registrado: {name} {tag}")
        except Exception as e:
            print(f"  x Error al consultar {repo}: {e}")

if __name__ == "__main__":
    run()