"""DevBrain Project Packager v1.0 — Empaquetador de Contexto de Ultra-Bajo Token
Genera bundles de contexto estructural podados mediante AST slicing y minificación sintáctica.
Escribe el bundle completo en disco (.devbrain/context_bundle.md) y retorna solo un
resumen compacto (< 80 tokens) para evitar contaminar la ventana de contexto del LLM.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from token_optimizer import TokenOptimizer, estimate_tokens

IGNORED_DIRS = {
    ".git", "node_modules", "dist", "build", ".devbrain", "__pycache__",
    ".pytest_cache", ".venv", "venv", "env", ".next", ".turbo", ".idea", ".vscode"
}

SOURCE_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".kt", ".sql"
}


def find_project_root(project_name: str = "", start_path: Path | None = None) -> Path:
    """Localiza la raíz del proyecto actual."""
    if start_path and start_path.exists():
        return start_path

    # Buscar en el directorio actual
    cwd = Path.cwd()
    if project_name and (cwd / project_name).is_dir():
        return cwd / project_name

    return cwd


def package_project(
    project_name: str = "General",
    project_path: str | Path | None = None,
    max_tokens_per_file: int = 250,
    max_total_tokens: int = 1200
) -> dict[str, Any]:
    """Escanea el proyecto, extrae esqueletos AST y guarda .devbrain/context_bundle.md."""
    root = Path(project_path) if project_path else find_project_root(project_name)
    optimizer = TokenOptimizer()

    file_summaries = []
    total_orig_tokens = 0
    total_opt_tokens = 0
    processed_files = 0

    # 1. Recorrer archivos de código fuente
    for root_dir, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for f in files:
            p = Path(root_dir) / f
            ext = p.suffix.lower()
            if ext not in SOURCE_EXTENSIONS:
                continue

            try:
                content = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            if not content.strip():
                continue

            rel_path = p.relative_to(root).as_posix()
            res = optimizer.optimize_code_context(
                code_text=content,
                language="auto",
                max_tokens=max_tokens_per_file
            )

            total_orig_tokens += res["original_tokens"]
            total_opt_tokens += res["optimized_tokens"]
            processed_files += 1

            file_summaries.append({
                "path": rel_path,
                "skeleton": res["optimized_code"],
                "tokens": res["optimized_tokens"]
            })

            # Límite de seguridad para no sobrecargar el escaneo
            if processed_files >= 60:
                break
        if processed_files >= 60:
            break

    # 2. Generar el documento Markdown de contexto
    bundle_content = [
        f"# 🧠 DevBrain Context Bundle: [[{project_name}]]",
        f"> Raíz: `{root.as_posix()}` | Archivos analizados: {processed_files}",
        f"> Estrategia: AST Signature Slicing & Token Minification",
        "",
        "## 📐 Esqueleto Arquitectónico del Código",
        ""
    ]

    for item in file_summaries:
        bundle_content.append(f"### `{item['path']}` (~{item['tokens']} t)")
        bundle_content.append("```text")
        bundle_content.append(item["skeleton"].strip())
        bundle_content.append("```")
        bundle_content.append("")

    final_bundle_text = "\n".join(bundle_content)
    final_tokens = estimate_tokens(final_bundle_text)
    savings_pct = round(((total_orig_tokens - final_tokens) / total_orig_tokens * 100), 1) if total_orig_tokens > 0 else 0.0

    # 3. Guardar en disco local (.devbrain/context_bundle.md)
    devbrain_dir = root / ".devbrain"
    devbrain_dir.mkdir(parents=True, exist_ok=True)
    bundle_file = devbrain_dir / "context_bundle.md"
    bundle_file.write_text(final_bundle_text, encoding="utf-8")

    return {
        "status": "success",
        "project": project_name,
        "bundle_path": bundle_file.as_posix(),
        "files_analyzed": processed_files,
        "original_tokens": total_orig_tokens,
        "bundle_tokens": final_tokens,
        "savings_tokens": max(0, total_orig_tokens - final_tokens),
        "savings_percent": savings_pct
    }
