"""
Ecosystem Scout: Monitorea fuentes para sugerir nuevas herramientas
que potencien la arquitectura agentica y el stack del usuario.
"""
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

VAULT = Path(r"C:\Users\damm1\OneDrive\Documentos\Obsidian Vault")
OUT_DIR = VAULT / "00-INBOX" / "auto" / "ecosystem-scout"

KEYWORDS = [
    "agent", "agents", "langgraph", "fastapi", "docker", "kubernetes", 
    "nestjs", "tailwind", "postgres", "supabase", "devops", "mcp", "rag"
]

def run():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    feed_url = "https://news.ycombinator.com/rss"
    headers = {"User-Agent": "DevBrain-Scout"}
    
    matches = []
    try:
        req = urllib.request.Request(feed_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml_data = resp.read()
            root = ET.fromstring(xml_data)
            
            for item in root.findall(".//item"):
                title = item.find("title").text or ""
                link = item.find("link").text or ""
                
                title_lower = title.lower()
                if any(kw in title_lower for kw in KEYWORDS):
                    matches.append((title, link))
    except Exception as e:
        print(f"Error consultando feed: {e}")

    if matches:
        date_str = datetime.now().strftime('%Y-%m-%d')
        out_file = OUT_DIR / f"{date_str}-scout-findings.md"
        
        items_md = "\n".join([f"- **[{t}]({l})**" for t, l in matches])
        content = f"""---
tags: [inbox, ecosystem-scout, radar]
fecha: {date_str}
total_hallazgos: {len(matches)}
---

# 📡 Radar de Ecosistema & Herramientas ({date_str})

Herramientas y tendencias detectadas que pueden nutrir tu cerebro de desarrollo:

{items_md}

## Acción Sugerida
- Evaluar si alguna herramienta amerita una nota en `03-CONOCIMIENTO/` o incorporarla al stack.
"""
        out_file.write_text(content.strip() + "\n", encoding="utf-8")
        print(f"  -> {len(matches)} herramientas/artículos relevantes detectados y registrados.")

if __name__ == "__main__":
    run()