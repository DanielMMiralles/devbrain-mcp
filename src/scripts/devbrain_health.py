"""
DevBrain Health Checker: Inspecciona las dependencias y estado de salud
de tus proyectos insignia en el Escritorio y genera un informe en el Vault.
"""
import os
import json
from pathlib import Path

VAULT_DIR = Path(os.getenv("VAULT_DIR", str(Path.home() / "ObsidianVault")))
OUTPUT_REPORT = VAULT_DIR / "04-APRENDIZAJES" / "salud-proyectos.md"

DESKTOP_DIR = Path(os.getenv("DESKTOP_DIR", str(Path.home() / "Projects")))
MAYAN_DIR = Path(os.getenv("MAYAN_DIR", r"C:\Users\damm1\mayan-edms"))

PROJECTS = [
    ("AliaLog (NestJS API)", DESKTOP_DIR / "alia-log-api" / "alia-log-api"),
    ("Chambita (NestJS API)", DESKTOP_DIR / "Chambita" / "chambita-api"),
    ("Chambita (Mobile Expo)", DESKTOP_DIR / "Chambita App" / "chambita-mobile-app"),
    ("Narval-SGN (Django REST)", DESKTOP_DIR / "Narval-SGN" / "backend"),
    ("Alia/IMA LangGraph", DESKTOP_DIR / "Alia_LangGraph"),
    ("Mayan-EDMS", MAYAN_DIR)
]

def check_all_projects():
    results = []
    print("Iniciando auditoria de salud de dependencias...")

    for label, path in PROJECTS:
        status = {"name": label, "pkg_count": 0, "type": "Desconocido", "has_docker": False, "details": []}
        if not path.exists():
            status["status"] = "Directorio no encontrado"
            results.append(status)
            continue

        pkg = path / "package.json"
        req = path / "requirements.txt"
        dkr = (path / "Dockerfile").exists() or (path / "docker-compose.yml").exists()
        status["has_docker"] = dkr

        if pkg.exists():
            status["type"] = "Node.js / TypeScript"
            try:
                d = json.loads(pkg.read_text(encoding="utf-8", errors="ignore"))
                deps = d.get("dependencies", {})
                status["pkg_count"] = len(deps)
                status["details"] = list(deps.keys())[:5]
            except Exception:
                pass
        elif req.exists():
            status["type"] = "Python"
            try:
                lines = [l.strip() for l in req.read_text(encoding="utf-8", errors="ignore").splitlines() if l.strip() and not l.startswith("#")]
                status["pkg_count"] = len(lines)
                status["details"] = [l.split("==")[0] for l in lines[:5]]
            except Exception:
                pass

        results.append(status)

    report_lines = [
        "---",
        "tags: [salud, proyectos, dependencias, auditoria]",
        "---",
        "# 🩺 Informe de Salud y Dependencias de Proyectos Insignia\n",
        "| Proyecto | Ecosistema | Dependencias Directas | Contenerizado (Docker) | Muestra de Librerías |",
        "|---|---|---|---|---|"
    ]

    for r in results:
        dk_badge = "✅ Sí" if r.get("has_docker") else "⚠️ No"
        sample = ", ".join(r.get("details", []))
        report_lines.append(f"| **{r['name']}** | {r['type']} | {r['pkg_count']} librerías | {dk_badge} | {sample} |")

    report_lines.append("\n## 💡 Recomendaciones de Mantenimiento")
    report_lines.append("- Mantener sincronizadas las versiones menores para evitar roturas.")
    report_lines.append("- Considerar agregar `Dockerfile` a proyectos que aun carecen de empaquetado aislado.")

    OUTPUT_REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"[OK] Reporte de salud guardado en: {OUTPUT_REPORT.relative_to(VAULT_DIR)}")

if __name__ == "__main__":
    check_all_projects()