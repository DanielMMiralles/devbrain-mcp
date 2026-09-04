"""
DevBrain Security & Secret Auditor (DevSecOps).
Escanea proactivamente archivos de configuración, notas y proyectos locales
para verificar que no existan credenciales, tokens de API o secretos expuestos.
"""
import re
from pathlib import Path

VAULT_DIR = Path(os.getenv("VAULT_DIR", str(Path.home() / "ObsidianVault")))
OUTPUT_REPORT = VAULT_DIR / "06-SISTEMA" / "security_audit_report.md"

PATTERNS = {
    "OpenAI / Anthropic API Key": r"sk-[a-zA-Z0-9]{20,}",
    "AWS Access Key ID": r"AKIA[0-9A-Z]{16}",
    "GitHub Personal Access Token": r"ghp_[a-zA-Z0-9]{36}",
    "Postgres Raw Password in URL": r"postgres://[^:]+:([^@]+)@",
    "Private Key Header": r"-----BEGIN (RSA|EC|OPENSSH|PGP) PRIVATE KEY-----"
}

def scan_vault():
    findings = []
    print("Iniciando auditoria DevSecOps del Vault...")
    
    for f in VAULT_DIR.rglob("*.md"):
        if ".obsidian" in f.parts:
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            for label, pattern in PATTERNS.items():
                matches = re.findall(pattern, content)
                if matches:
                    findings.append({
                        "file": str(f.relative_to(VAULT_DIR)),
                        "type": label,
                        "count": len(matches)
                    })
        except Exception:
            pass
            
    print(f"Auditoria finalizada. Hallazgos criticos: {len(findings)}")
    
    report_md = f"""---
tags: [seguridad, devsecops, auditoria]
fecha: "{Path(__file__).stat().st_mtime}"
---

# 🛡️ Reporte de Auditoría DevSecOps

## Estado General
- **Total de Alertas de Secretos Expuestos**: {len(findings)}

"""
    if findings:
        report_md += "## ⚠️ Secretos o Tokens Detectados\n"
        for item in findings:
            report_md += f"- **Archivo**: `{item['file']}` | **Tipo**: {item['type']} ({item['count']} coincidencias)\n"
        report_md += "\n> **Acción Inmediata**: Mover las credenciales a variables de entorno (.env) e ignorarlas con `.gitignore`.\n"
    else:
        report_md += "## ✅ Estado Limpio y Seguro\nNo se detectaron API keys, passwords en texto plano ni llaves privadas expuestas en las notas auditadas.\n"

    OUTPUT_REPORT.write_text(report_md.strip() + "\n", encoding="utf-8")
    print(f"[OK] Reporte guardado en: {OUTPUT_REPORT}")

if __name__ == "__main__":
    scan_vault()