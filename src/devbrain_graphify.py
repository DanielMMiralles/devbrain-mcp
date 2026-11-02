"""DevBrain Code Graph Engine v2.0 — Indexador AST + Bridge Nativo con Graphify & Deep Modules
Construye y consulta grafos de dependencias, símbolos de código, aristas (EXTRACTED/INFERRED)
y métricas de profundidad modular (Ousterhout / Matt Pocock Deep Modules) sin depender de LLM.
Se integra automáticamente con `graphify-out/graph.json` (Graphify-Labs) cuando existe.
"""

from __future__ import annotations

import ast
import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Any

IGNORED_DIRS = {
    ".git", "node_modules", "dist", "build", ".devbrain", "__pycache__",
    ".pytest_cache", ".venv", "venv", "env", ".next", ".turbo", "graphify-out"
}


def _get_db_path(root: Path) -> Path:
    devbrain_dir = root / ".devbrain"
    devbrain_dir.mkdir(parents=True, exist_ok=True)
    return devbrain_dir / "code_graph.db"


def _get_conn(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path), timeout=10.0)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA temp_store = MEMORY")
    except Exception:
        pass
    return conn


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
        community TEXT DEFAULT '',
        depth_hint TEXT DEFAULT '',
        UNIQUE(file_path, name, kind, parent)
    );
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS edges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,
        target TEXT NOT NULL,
        relation TEXT DEFAULT 'EXTRACTED',
        weight REAL DEFAULT 1.0,
        UNIQUE(source, target, relation)
    );
    """)
    # Migración suave si la tabla symbols era v1.0
    try:
        conn.execute("ALTER TABLE symbols ADD COLUMN community TEXT DEFAULT '';")
    except Exception:
        pass
    try:
        conn.execute("ALTER TABLE symbols ADD COLUMN depth_hint TEXT DEFAULT '';")
    except Exception:
        pass

    conn.execute("CREATE INDEX IF NOT EXISTS idx_sym_name ON symbols(name COLLATE NOCASE);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sym_file ON symbols(file_path);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_src ON edges(source COLLATE NOCASE);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_tgt ON edges(target COLLATE NOCASE);")
    conn.commit()


def _ingest_graphify_json(root: Path, conn: sqlite3.Connection) -> tuple[int, int]:
    """Si existe graphify-out/graph.json (de Graphify CLI), fusiona sus nodos, comunidades y aristas."""
    graph_json_path = root / "graphify-out" / "graph.json"
    if not graph_json_path.exists():
        return 0, 0

    nodes_merged = 0
    edges_merged = 0
    try:
        data = json.loads(graph_json_path.read_text(encoding="utf-8", errors="replace"))
        nodes = data.get("nodes", [])
        links = data.get("links", data.get("edges", []))

        for n in nodes:
            node_id = str(n.get("id") or n.get("label") or "").strip()
            if not node_id:
                continue
            file_p = str(n.get("file") or n.get("source_file") or "graphify-out/graph.json")
            kind = str(n.get("type") or n.get("kind") or "concept")
            community = str(n.get("community") or n.get("cluster") or "")
            conn.execute(
                """INSERT OR REPLACE INTO symbols
                   (file_path, name, kind, parent, signature, line_no, community, depth_hint)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (file_p, node_id, kind, "", f"[{kind}] {node_id}", int(n.get("line", 1) or 1), community, "graphify-node")
            )
            nodes_merged += 1

        for e in links:
            src = str(e.get("source") or "").strip()
            tgt = str(e.get("target") or "").strip()
            rel = str(e.get("relation") or e.get("confidence") or "EXTRACTED").upper()
            also_seen = e.get("also_seen", [])
            weight = float(e.get("weight", 1.0) or 1.0)
            # Soporte Graphify 0.9.100: Si la arista fusionada tiene 'also_seen', sumar evidencia sin duplicar
            if also_seen and isinstance(also_seen, list):
                weight += min(len(also_seen) * 0.25, 1.5)
            if src and tgt:
                conn.execute(
                    "INSERT OR REPLACE INTO edges (source, target, relation, weight) VALUES (?, ?, ?, ?)",
                    (src, tgt, rel, weight)
                )
                edges_merged += 1
    except Exception:
        pass

    return nodes_merged, edges_merged


def sync_project_graph(project_path: str | Path | None = None) -> str:
    """Escanea el proyecto (AST + imports + Deep-Module ratio) y fusiona graphify-out/graph.json si existe."""
    root = Path(project_path) if project_path else Path.cwd()
    if not root.is_dir():
        return f"Error: La ruta del proyecto '{root}' no existe."

    db_path = _get_db_path(root)
    conn = _get_conn(db_path)
    _init_db(conn)

    conn.execute("DELETE FROM symbols;")
    conn.execute("DELETE FROM edges;")

    symbols_count = 0
    edges_count = 0
    files_indexed = 0
    shallow_warnings = []

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
                    total_lines = max(1, content.count("\n") + 1)
                    public_defs = 0

                    for node in tree.body:
                        # Registrar imports como aristas EXTRACTED
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                conn.execute(
                                    "INSERT OR REPLACE INTO edges (source, target, relation, weight) VALUES (?, ?, 'EXTRACTED', 1.0)",
                                    (rel_path, alias.name)
                                )
                                edges_count += 1
                        elif isinstance(node, ast.ImportFrom) and node.module:
                            conn.execute(
                                "INSERT OR REPLACE INTO edges (source, target, relation, weight) VALUES (?, ?, 'EXTRACTED', 1.0)",
                                (rel_path, node.module)
                            )
                            edges_count += 1

                        elif isinstance(node, ast.ClassDef):
                            if not node.name.startswith("_"):
                                public_defs += 1
                            methods = [
                                item for item in node.body
                                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                            ]
                            public_methods = [m for m in methods if not m.name.startswith("_")]
                            class_lines = max(1, (getattr(node, "end_lineno", node.lineno) or node.lineno) - node.lineno)
                            # Heurística Ousterhout / Matt Pocock (Deep vs Shallow module)
                            depth_tag = "deep-module" if (class_lines >= 35 and len(public_methods) <= 4) else (
                                "shallow-interface-warning" if (len(public_methods) > 6 and class_lines < len(public_methods) * 6) else "balanced"
                            )
                            args_sig = f"class {node.name} ({len(public_methods)} pub / {class_lines} LOC)"
                            conn.execute(
                                """INSERT OR REPLACE INTO symbols
                                   (file_path, name, kind, parent, signature, line_no, community, depth_hint)
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                                (rel_path, node.name, "class", "", args_sig, getattr(node, "lineno", 1), Path(rel_path).parent.as_posix(), depth_tag)
                            )
                            symbols_count += 1

                            for item in methods:
                                prefix = "async def " if isinstance(item, ast.AsyncFunctionDef) else "def "
                                arg_names = [a.arg for a in item.args.args if a.arg != "self"][:4]
                                sig_str = f"{prefix}{item.name}({', '.join(arg_names)})"
                                conn.execute(
                                    """INSERT OR REPLACE INTO symbols
                                       (file_path, name, kind, parent, signature, line_no, community, depth_hint)
                                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                                    (rel_path, item.name, "method", node.name, sig_str, getattr(item, "lineno", 1), Path(rel_path).parent.as_posix(), "")
                                )
                                symbols_count += 1

                        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            if not node.name.startswith("_"):
                                public_defs += 1
                            prefix = "async def " if isinstance(node, ast.AsyncFunctionDef) else "def "
                            arg_names = [a.arg for a in node.args.args][:4]
                            fn_lines = max(1, (getattr(node, "end_lineno", node.lineno) or node.lineno) - node.lineno)
                            depth_tag = "deep-fn" if fn_lines >= 25 and len(arg_names) <= 3 else "standard"
                            conn.execute(
                                """INSERT OR REPLACE INTO symbols
                                   (file_path, name, kind, parent, signature, line_no, community, depth_hint)
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                                (rel_path, node.name, "function", "", f"{prefix}{node.name}({', '.join(arg_names)})", getattr(node, "lineno", 1), Path(rel_path).parent.as_posix(), depth_tag)
                            )
                            symbols_count += 1

                    if public_defs > 8 and (total_lines / max(1, public_defs)) < 8:
                        shallow_warnings.append(f"`{rel_path}` ({public_defs} exports públicos para solo {total_lines} LOC)")
                except Exception:
                    pass

            elif ext in (".ts", ".tsx", ".js", ".jsx"):
                try:
                    content = p.read_text(encoding="utf-8", errors="replace")
                    files_indexed += 1

                    # Imports TS/JS
                    for imp in re.finditer(r"from\s+['\"]([^'\"]+)['\"]", content):
                        conn.execute(
                            "INSERT OR REPLACE INTO edges (source, target, relation, weight) VALUES (?, ?, 'EXTRACTED', 1.0)",
                            (rel_path, imp.group(1))
                        )
                        edges_count += 1

                    for match in re.finditer(r"(?:export\s+)?(?:default\s+)?(class|interface|type|function|const)\s+([A-Za-z0-9_$]+)", content):
                        kind = match.group(1)
                        name = match.group(2)
                        line_no = content[:match.start()].count("\n") + 1
                        conn.execute(
                            """INSERT OR REPLACE INTO symbols
                               (file_path, name, kind, parent, signature, line_no, community, depth_hint)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                            (rel_path, name, kind, "", f"{kind} {name}", line_no, Path(rel_path).parent.as_posix(), "")
                        )
                        symbols_count += 1
                except Exception:
                    pass

    g_nodes, g_edges = _ingest_graphify_json(root, conn)
    conn.commit()
    conn.close()

    report = [
        f"### 🌐 DevBrain Code Graph v2.0 Sincronizado (AST + Deep-Modules + Graphify)",
        f"- **Archivos Indexados**: {files_indexed}",
        f"- **Símbolos Registrados**: {symbols_count} (+ {g_nodes} nodos de `graphify-out`)",
        f"- **Aristas / Dependencias (`EXTRACTED`/`INFERRED`)**: {edges_count + g_edges}",
        f"- **Ubicación Base de Datos (WAL)**: `{db_path.as_posix()}`",
        f"- **Tokens Consumidos**: 0 (100% determinista local)"
    ]
    if shallow_warnings:
        report.append(f"- ⚠️ **Candidatos a Deepening (`codebase-design`)**: {', '.join(shallow_warnings[:3])}")
    return "\n".join(report)


def query_symbol(project_path: str = "", symbol: str = "") -> str:
    """Busca un símbolo, sus conexiones EXTRACTED/INFERRED y su diagnóstico de profundidad modular."""
    if not symbol.strip():
        return "Error: Se requiere 'symbol' para consultar el grafo de código."

    root = Path(project_path) if project_path else Path.cwd()
    db_path = _get_db_path(root)

    if not db_path.exists():
        sync_project_graph(root)

    conn = _get_conn(db_path)
    cursor = conn.cursor()

    q = symbol.strip()
    cursor.execute("""
        SELECT file_path, name, kind, parent, signature, line_no, community, depth_hint
        FROM symbols
        WHERE name LIKE ? OR file_path LIKE ?
        ORDER BY CASE WHEN LOWER(name) = LOWER(?) THEN 0 ELSE 1 END, kind ASC
        LIMIT 10
    """, (f"%{q}%", f"%{q}%", q))
    rows = cursor.fetchall()

    cursor.execute("""
        SELECT source, target, relation
        FROM edges
        WHERE source LIKE ? OR target LIKE ?
        LIMIT 8
    """, (f"%{q}%", f"%{q}%"))
    edge_rows = cursor.fetchall()
    conn.close()

    if not rows and not edge_rows:
        return f"No se encontró el símbolo o módulo '{symbol}' en el grafo de código de `{root.name}`."

    out = [f"### 🔍 Grafo de Código: `{symbol}` en [[{root.name}]]"]
    for r in rows:
        parent_str = f" (en `{r['parent']}`)" if r["parent"] else ""
        depth_badge = f" · 📐 `{r['depth_hint']}`" if r["depth_hint"] and r["depth_hint"] not in ("standard", "balanced") else ""
        comm_badge = f" · 🧩 `{r['community']}`" if r["community"] else ""
        out.append(
            f"- **`{r['name']}`** [{r['kind']}]{parent_str}{depth_badge}{comm_badge}\n"
            f"  - Archivo: `{r['file_path']}:{r['line_no']}` | Signatura: `{r['signature']}`"
        )

    if edge_rows:
        out.append("\n#### 🔗 Aristas y Dependencias Detectadas:")
        for e in edge_rows:
            out.append(f"- `{e['source']}` ──[{e['relation']}]──▶ `{e['target']}`")

    return "\n".join(out)
