"""
DevBrain Web Clipper: Captura documentacion tecnica, articulos de ingenieria
o issues de GitHub y los transforma en notas markdown limpias enlazadas al Grafo.
"""
import sys
import re
import urllib.request
from datetime import datetime
from pathlib import Path
from html.parser import HTMLParser

VAULT_DIR = Path(os.getenv("VAULT_DIR", r"C:\Users\damm1\OneDrive\Documentos\Obsidian Vault"))
INBOX_DIR = VAULT_DIR / "00-INBOX" / "clips"
INBOX_DIR.mkdir(parents=True, exist_ok=True)

class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.text = []
        self.in_title = False
        self.title = ""
        self.ignore = False

    def handle_starttag(self, tag, attrs):
        if tag in ["script", "style", "nav", "footer", "header"]:
            self.ignore = True
        elif tag == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag in ["script", "style", "nav", "footer", "header"]:
            self.ignore = False
        elif tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif not self.ignore:
            cleaned = data.strip()
            if cleaned:
                self.text.append(cleaned)

def clip_url(url: str, tags=None):
    if not tags:
        tags = ["web-clip", "referencia"]

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (DevBrain Clipper)"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Error descargando URL {url}: {e}")
        return

    parser = HTMLTextExtractor()
    parser.feed(html)

    title = parser.title.strip() or "Web Article Clip"
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title)[:40].strip()
    safe_slug = re.sub(r"\s+", "-", safe_title).lower()
    today = datetime.now().strftime("%Y-%m-%d")

    note_name = f"clip-{today}-{safe_slug}.md"
    target_path = INBOX_DIR / note_name

    body_preview = "\n\n".join(parser.text[:40])

    tags_str = ", ".join(tags)
    content = f"""---
tags: [{tags_str}]
url_origen: "{url}"
fecha_captura: "{today}"
---

# 🌐 {title}

## Origen
- Enlace original: [{url}]({url})

## Extracto del Contenido
{body_preview}

## Conexiones en DevBrain
- ¿A qué tecnología o proyecto aplica? (Ej: [[FastAPI]], [[NestJS]], [[LangGraph]])
"""

    target_path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"[OK] Web Clip guardado con exito en: {target_path.relative_to(VAULT_DIR)}")
    return target_path

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url_arg = sys.argv[1]
        tags_arg = sys.argv[2:] if len(sys.argv) > 2 else ["web-clip"]
        clip_url(url_arg, tags_arg)
    else:
        print("Uso: py devbrain_clipper.py <URL> [tag1 tag2 ...]")