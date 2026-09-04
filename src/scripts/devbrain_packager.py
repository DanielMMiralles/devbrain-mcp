"""
DevBrain Code Context Packager: Empaqueta de forma compacta el arbol de archivos
y modulos clave de cualquier proyecto del Escritorio para entregarselo al agente de IA
con un ahorro de tokens de hasta el 80%.
"""
import sys
import os
from pathlib import Path

VAULT_DIR = Path(os.getenv("VAULT_DIR", str(Path.home() / "ObsidianVault")))
OUTPUT_DIR = VAULT_DIR / "02-PROYECTOS" / "context-bundles"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DESKTOP_DIR = Path(os.getenv("DESKTOP_DIR", str(Path.home() / "Projects")))
MAYAN_DIR = Path(os.getenv("MAYAN_DIR", r"C:\Users\damm1\mayan-edms"))

IGNORE_DIRS = {".git", "node_modules", "dist", "build", "venv", "__pycache__", ".pytest_cache", ".next", ".expo"}
ALLOWED_EXTS = {".ts", ".tsx", ".py", ".json", ".yml", ".yaml", ".sql", ".prisma", ".dart"}

def package_project(project_name: str, max_files: int = 25):
    # Buscar ruta local en DESKTOP_DIR o en el vault (02-PROYECTOS)
    target = None
    search_dirs = [DESKTOP_DIR, VAULT_DIR / "02-PROYECTOS"]
    for base in search_dirs:
        if base.exists():
            for p in base.iterdir():
                if p.is_dir() and project_name.lower() in p.name.lower() and p.name not in ["specs", "_templates", "context-bundles"]:
                    target = p
                    break
        if target:
            break

    if not target and "mayan" in project_name.lower() and MAYAN_DIR.exists():
        target = MAYAN_DIR

    if not target or not target.exists():
        return f"No se encontro ningun proyecto que coincida con '{project_name}'. Verifica que el directorio exista en PROJECTS_DIR o 02-PROYECTOS."

    print(f"Empaquetando contexto inteligente para: {target.name}...")
    bundle_name = f"context-{target.name.lower().replace(' ', '-')}.md"
    bundle_path = OUTPUT_DIR / bundle_name

    tree_lines = []
    file_contents = []
    collected_count = 0

    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        rel_root = os.path.relpath(root, target)
        depth = rel_root.count(os.sep)
        if depth < 3:
            indent = "  " * depth
            folder_name = os.path.basename(root)
            if folder_name != target.name:
                tree_lines.append(f"{indent}📁 {folder_name}/")

        for f in files:
            ext = os.path.splitext(f)[1]
            if ext in ALLOWED_EXTS:
                file_rel = os.path.join(rel_root, f) if rel_root != "." else f
                if depth < 3:
                    tree_lines.append(f"{'  ' * (depth + 1)}📄 {f}")
                
                # Leer archivos estrategicos
                if collected_count < max_files and (f.endswith((".json", ".yml", ".yaml", "prisma")) or "main" in f or "app" in f or "service" in f or "controller" in f or "router" in f):
                    try:
                        p_file = Path(root) / f
                        txt = p_file.read_text(encoding="utf-8", errors="ignore")[:1500]
                        file_contents.append(f"### Archivo: `{file_rel}`\n```\n{txt}\n```\n")
                        collected_count += 1
                    except Exception:
                        pass

    md_output = f"""---
tags: [context-bundle, ai-ready, {target.name.lower()}]
proyecto: "[[{target.name}]]"
archivos_incluidos: {collected_count}
---

# 📦 Bundle de Contexto para IA: {target.name}

## Árbol de Módulos
```
{chr(10).join(tree_lines[:45])}
```

## Contenidos Estratégicos Seleccionados
{"".join(file_contents)}
"""
    bundle_path.write_text(md_output.strip() + "\n", encoding="utf-8")
    print(f"[OK] Bundle generado exitosamente en: {bundle_path.relative_to(VAULT_DIR)}")
    print(f"Total de modulos empaquetados: {collected_count}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        package_project(sys.argv[1])
    else:
        print("Uso: py devbrain_packager.py <nombre_proyecto>")