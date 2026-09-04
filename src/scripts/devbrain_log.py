"""
DevBrain Daily Log: Genera entradas diarias interactivas en tu diario de desarrollo
capturando objetivos cumplidos, bugs resueltos y próximos pasos.
"""
import sys
from datetime import datetime
from pathlib import Path

VAULT_DIR = Path(os.getenv("VAULT_DIR", r"C:\Users\damm1\OneDrive\Documentos\Obsidian Vault"))
DIARY_DIR = VAULT_DIR / "07-DIARIO"
DIARY_DIR.mkdir(parents=True, exist_ok=True)

def create_daily_entry(project: str, done: str, blocker: str, next_step: str):
    today = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M")
    diary_file = DIARY_DIR / f"{today}.md"

    content = f"""---
tags: [diario, devlog, standup]
fecha: "{today}"
---

# 📅 Diario de Desarrollo: {today}

## 🎯 Foco Principal
- Proyecto activo: [[{project}]]
- Hora de registro: {now_time}

## ✅ Lo que se avanzó hoy
{done}

## ⚠️ Retos Técnicos o Bloqueos Encontrados
{blocker}

## 🚀 Próximos Pasos (Mañana)
{next_step}

## Enlaces con DevBrain
- [[mis-convenciones]]
- [[{project}]]
"""
    diary_file.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"[OK] Entrada del diario guardada en: {diary_file.relative_to(VAULT_DIR)}")

if __name__ == "__main__":
    if len(sys.argv) >= 5:
        create_daily_entry(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("=== DevBrain Daily Log ===")
        proj = input("Proyecto en el que trabajaste (ej: Chambita-Ecosystem, AliaLog-System): ") or "General"
        done = input("Que se avanzo hoy?: ") or "Avance en desarrollo."
        blocker = input("Algún bug o reto técnico que superaste?: ") or "Ninguno critico."
        next_step = input("Cual es el siguiente paso para mañana?: ") or "Continuar implementacion."
        create_daily_entry(proj, done, blocker, next_step)