"""DevBrain Code Graph Engine v1.0 — Indexador Semántico-Sintáctico Local
Construye y consulta grafos de dependencias y símbolos de código sin depender de LLM.
Almacena clases, funciones, métodos e imports en una base SQLite local (.devbrain/code_graph.db).
"""

from __future__ import annotations

import ast
import os
import re
import sqlite3
from pathlib import Path
from typing import Any

IGNORED_DIRS = {
    ".git", "node_modules", "dist", "build", ".devbrain", "__pycache__",
    ".pytest_cache", ".venv", "venv", "env", ".next", ".turbo"
}


def _get_db_path(root: Path) -> Path:
    devbrain_dir = root / ".devbrain"
    devbrain_dir.mkdir(parents=True, exist_ok=True)
    return devbrain_dir / "code_graph.db"


def _init_db(conn: sqlite3.Connection) -> None:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS symbols (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT NOT NULL,
        name TEXT NOT NULL,
        kind TEXT NOT NULL,
        parent TEXT DEFAULT '',
        signature TEXT DEFAULT '',
        line_no INTEGER DEFAULT 1,
        UNIQUE(file_path, name, kind, parent)
    );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sym_name ON symbols(name COLLATE NOCASE);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sym_file ON symbols(file_path);")
    conn.commit()


def sync_project_graph(project_path: str | Path | None = None) -> str:
    """Escanea el proyecto e indexa todos los símbolos sintácticos en SQLite."""
    root = Path(project_path) if project_path else Path.cwd()
    if not root.is_dir():
        return f"Error: La ruta del proyecto '{root}' no existe."

    db_path = _get_db_path(root)
    conn = sqlite3.connect(str(db_path))
    _init_db(conn)

    # Limpiar índice previo
    conn.execute("DELETE FROM symbols;")

    symbols_count = 0
    files_indexed = 0

    for root_dir, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for f in files:
            p = Path(root_dir) / f
            ext = p.suffix.lower()
            rel_path = p.relative_to(root).as_posix()

            if ext == ".py":
                try:
                    content = p.read_text(encoding="utf-8", errors="replace")
                    tree = ast.parse(content)
                    files_indexed += 1

                    for node in tree.body:
                        if isinstance(node, ast.ClassDef):
                            conn.execute(
                                "INSERT OR REPLACE INTO symbols (file_path, name, kind, parent, signature, line_no) VALUES (?, ?, ?, ?, ?, ?)",
                                (rel_path, node.name, "class", "", f"class {node.name}", getattr(node, "lineno", 1))
                            )
                            symbols_count += 1

                            for item in node.body:
                                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                    prefix = "async def " if isinstance(item, ast.AsyncFunctionDef) else "def "
                                    conn.execute(
                                        "INSERT OR REPLACE INTO symbols (file_path, name, kind, parent, signature, line_no) VALUES (?, ?, ?, ?, ?, ?)",
                                        (rel_path, item.name, "method", node.name, f"{prefix}{item.name}(...)", getattr(item, "lineno", 1))
                                    )
                                    symbols_count += 1

                        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            prefix = "async def " if isinstance(node, ast.AsyncFunctionDef) else "def "
                            conn.execute(
                                "INSERT OR REPLACE INTO symbols (file_path, name, kind, parent, signature, line_no) VALUES (?, ?, ?, ?, ?, ?)",
                                (rel_path, node.name, "function", "", f"{prefix}{node.name}(...)", getattr(node, "lineno", 1))
                            )
                            symbols_count += 1

                except Exception:
                    pass

            elif ext in (".ts", ".tsx", ".js", ".jsx"):
                try:
                    content = p.read_text(encoding="utf-8", errors="replace")
                    files_indexed += 1

                    # Regex para clases, interfaces, funciones y exports
                    for match in re.finditer(r"(?:export\s+)?(?:default\s+)?(class|interface|type|function|const)\s+([A-Za-z0-9_$]+)", content):
                        kind = match.group(1)
                        name = match.group(2)
                        line_no = content[:match.start()].count("\n") + 1
                        conn.execute(
                            "INSERT OR REPLACE INTO symbols (file_path, name, kind, parent, signature, line_no) VALUES (?, ?, ?, ?, ?, ?)",
                            (rel_path, name, kind, "", f"{kind} {name}", line_no)
                        )
                        symbols_count += 1
                except Exception:
                    pass

    conn.commit()
    conn.close()

    return (
        f"### 🌐 DevBrain Code Graph Sincronizado\n"
        f"- **Archivos Indexados**: {files_indexed}\n"
        f"- **Símbolos Registrados**: {symbols_count}\n"
        f"- **Ubicación Base de Datos**: `{db_path.as_posix()}`\n"
        f"- **Tokens Consumidos en Indexación**: 0 (AST nativo local)"
    )


def query_symbol(project_path: str = "", symbol: str = "") -> str:
    """Busca un símbolo (clase, función, método) y retorna su signatura y ubicación exacta."""
    if not symbol.strip():
        return "Error: Se requiere 'symbol' para consultar el grafo de código."

    root = Path(project_path) if project_path else Path.cwd()
    db_path = _get_db_path(root)

    if not db_path.exists():
        # Auto-sincronizar si no existe la base
        sync_project_graph(root)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT file_path, name, kind, parent, signature, line_no
        FROM symbols
        WHERE name LIKE ?
        ORDER BY CASE WHEN LOWER(name) = LOWER(?) THEN 0 ELSE 1 END, kind ASC
        LIMIT 10
    """, (f"%{symbol.strip()}%", symbol.strip()))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return f"No se encontró el símbolo '{symbol}' en el grafo de código de `{root.name}`."

    out = [f"### 🔍 Símbolo: `{symbol}` en [[{root.name}]]"]
    for r in rows:
        parent_str = f" (en `{r['parent']}`)" if r["parent"] else ""
        out.append(
            f"- **`{r['name']}`** [{r['kind']}]{parent_str}\n"
            f"  - Archivo: `{r['file_path']}:{r['line_no']}`\n"
            f"  - Signatura: `{r['signature']}`"
        )

    return "\n".join(out)
