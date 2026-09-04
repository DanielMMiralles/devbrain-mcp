"""
Scanner de Proyectos Locales para DevBrain.
Busca proyectos en carpetas clave de desarrollo, detecta dependencias
y crea/actualiza notas en 02-PROYECTOS enlazadas a las herramientas del Grafo.
"""
import os
import json
from pathlib import Path

VAULT_DIR = Path(os.getenv("VAULT_DIR", r"C:\Users\damm1\OneDrive\Documentos\Obsidian Vault"))
PROYECTOS_DIR = VAULT_DIR / "02-PROYECTOS"

# Directorios de desarrollo reales en la máquina
CANDIDATE_ROOTS = [
    Path(r"C:\Users\damm1\source\repos"),
    Path(r"C:\Users\damm1\PycharmProjects"),
    Path(r"C:\Users\damm1\Desktop"),
    Path(r"C:\Users\damm1\Documents"),
    Path(r"C:\Users\damm1\source"),
    Path(r"C:\Users\damm1\Proyecto1"),
    Path(r"C:\Users\damm1\Teamwork-bookstore"),
    Path(r"C:\Users\damm1\mayan-edms"),
    Path(r"C:\Users\damm1\simpy"),
]

TOOL_SIGNATURES = {
    "react": "[[React]]",
    "tailwindcss": "[[Tailwind CSS]]",
    "@tailwindcss": "[[Tailwind CSS]]",
    "shadcn": "[[shadcn-ui]]",
    "@radix-ui": "[[shadcn-ui]]",
    "@nestjs/core": "[[NestJS]]",
    "fastapi": "[[FastAPI]]",
    "django": "[[Django]]",
    "flask": "[[Flask]]",
    "pg": "[[PostgreSQL]]",
    "postgres": "[[PostgreSQL]]",
    "psycopg2": "[[PostgreSQL]]",
    "asyncpg": "[[PostgreSQL]]",
    "@supabase/supabase-js": "[[Supabase]]",
    "supabase": "[[Supabase]]",
    "langgraph": "[[LangGraph]]",
    "docker": "[[Docker]]",
    "terraform": "[[Terraform]]"
}

def analyze_directory(dir_path: Path) -> dict:
    detected_tools = set()
    has_git = (dir_path / ".git").exists()
    
    # Check Docker
    if (dir_path / "Dockerfile").exists() or (dir_path / "docker-compose.yml").exists() or (dir_path / "docker-compose.yaml").exists():
        detected_tools.add("[[Docker]]")

    # Check Terraform
    if list(dir_path.glob("*.tf")):
        detected_tools.add("[[Terraform]]")

    # Check CI/CD
    if (dir_path / ".github" / "workflows").exists():
        detected_tools.add("[[CI-CD Pipelines]]")

    # Check package.json (Node/TS/React/Nest)
    pkg_file = dir_path / "package.json"
    if pkg_file.exists():
        try:
            with open(pkg_file, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                for dep in deps:
                    dep_lower = dep.lower()
                    for sig, tag in TOOL_SIGNATURES.items():
                        if sig in dep_lower:
                            detected_tools.add(tag)
        except Exception:
            pass

    # Check requirements.txt or pyproject.toml (Python)
    req_file = dir_path / "requirements.txt"
    if req_file.exists():
        try:
            content = req_file.read_text(encoding="utf-8", errors="ignore").lower()
            for sig, tag in TOOL_SIGNATURES.items():
                if sig in content:
                    detected_tools.add(tag)
        except Exception:
            pass

    pyproj_file = dir_path / "pyproject.toml"
    if pyproj_file.exists():
        try:
            content = pyproj_file.read_text(encoding="utf-8", errors="ignore").lower()
            for sig, tag in TOOL_SIGNATURES.items():
                if sig in content:
                    detected_tools.add(tag)
        except Exception:
            pass

    return {
        "path": dir_path,
        "name": dir_path.name,
        "is_project": has_git or bool(detected_tools),
        "tools": sorted(list(detected_tools))
    }

def scan():
    PROYECTOS_DIR.mkdir(parents=True, exist_ok=True)
    found_projects = []
    
    for candidate in CANDIDATE_ROOTS:
        if not candidate.exists():
            continue
        # Check if candidate itself is a project
        if (candidate / ".git").exists() or (candidate / "package.json").exists() or (candidate / "requirements.txt").exists():
            res = analyze_directory(candidate)
            if res["is_project"]:
                found_projects.append(res)
                continue
        # Otherwise search immediate children
        try:
            for item in candidate.iterdir():
                if item.is_dir() and not item.name.startswith("."):
                    res = analyze_directory(item)
                    if res["is_project"]:
                        found_projects.append(res)
        except Exception:
            pass

    # Deduplicate by path
    unique_projects = {str(p["path"]): p for p in found_projects}.values()
    print(f"Proyectos detectados: {len(unique_projects)}")
    
    for p in unique_projects:
        proj_dir = PROYECTOS_DIR / p["name"]
        proj_dir.mkdir(parents=True, exist_ok=True)
        readme = proj_dir / "README.md"
        
        stack_links = ", ".join(p["tools"]) if p["tools"] else "Sin dependencias directas catalogadas"
        content = f"""---
tags: [proyecto, autodiscovered]
nombre: "{p['name']}"
estado: en-desarrollo
path_local: "{str(p['path']).replace('\\', '/')}"
stack: {json.dumps(p['tools'], ensure_ascii=False)}
---

# {p['name']}

## Stack Detectado y Conectado en el Grafo
{stack_links}

## Ubicación en Disco
`{p['path']}`

## Notas de Desarrollo & Contexto
- 
"""
        readme.write_text(content.strip() + "\n", encoding="utf-8")
        print(f"  -> Proyecto indexado en el Grafo: {p['name']} ({stack_links})")

if __name__ == "__main__":
    scan()