"""
DevBrain FTS5 Local Indexer & Composite Reranker (Engram v2 / Gentle-AI Inspired)
Ultra-fast, in-process, zero-subprocess indexing for Obsidian Vault & DevBrain Standalone.
"""
import sqlite3
import os
import re
import time
from pathlib import Path
from datetime import datetime, timezone
import math

class DevBrainIndex:
    def __init__(self, vault_dir: Path, db_path: Path = None):
        self.vault_dir = Path(vault_dir).resolve()
        self._last_sync = 0.0
        self.sync_interval = 60.0 # Re-escaneo máximo cada 60s salvo force=True
        if db_path is None:
            db_dir = self.vault_dir / "06-SISTEMA" / "cache"
            try:
                db_dir.mkdir(parents=True, exist_ok=True)
            except Exception:
                db_dir = Path("./.devbrain_cache").resolve()
                db_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = db_dir / "devbrain_fts.db"
        else:
            self.db_path = Path(db_path).resolve()
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()
        self.sync_index(force=True)

    def _get_conn(self):
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS files_meta (
                    path TEXT PRIMARY KEY,
                    mtime REAL,
                    size INTEGER,
                    doc_type TEXT
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE,
                    title TEXT,
                    content TEXT,
                    project TEXT,
                    tags TEXT,
                    pinned INTEGER DEFAULT 0,
                    updated_at TEXT
                )
            """)
            cur.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
                    title, content, project, tags,
                    content='memories', content_rowid='id'
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE,
                    title TEXT,
                    content TEXT,
                    category TEXT,
                    updated_at TEXT
                )
            """)
            cur.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
                    title, content, category,
                    content='knowledge', content_rowid='id'
                )
            """)
            conn.commit()

    @staticmethod
    def _sanitize_fts_query(raw_query: str) -> str:
        """Escapa dobles comillas y caracteres especiales para evitar errores de sintaxis FTS5."""
        clean = re.sub(r'["\*\^\:\(\)]', ' ', raw_query)
        tokens = [t.strip() for t in clean.split() if len(t.strip()) > 1]
        if not tokens:
            return ""
        return " OR ".join(f'"{t}"' for t in tokens)

    @staticmethod
    def _parse_frontmatter(text: str):
        meta = {"tags": [], "project": "", "title": "", "pinned": 0, "date": ""}
        if not text.startswith("---"):
            return meta, text
        parts = text.split("---", 2)
        if len(parts) < 3:
            return meta, text
        fm_text = parts[1]
        body = parts[2].strip()

        for line in fm_text.splitlines():
            line = line.strip()
            if not line or ":" not in line:
                continue
            k, v = line.split(":", 1)
            k = k.strip().lower()
            v = v.strip().strip("'\"")
            if k == "tags":
                tags_match = re.findall(r"[\w\-]+", v)
                meta["tags"] = tags_match
                if any(t in ["pinned", "rule", "regla", "invariante"] for t in tags_match):
                    meta["pinned"] = 1
            elif k in ["proyecto", "project"]:
                meta["project"] = v.replace("[[", "").replace("]]", "").strip()
            elif k in ["fecha", "date", "created"]:
                meta["date"] = v
            elif k in ["title", "titulo"]:
                meta["title"] = v
            elif k == "pinned":
                meta["pinned"] = 1 if v.lower() in ["true", "1", "yes"] else 0

        return meta, body

    def sync_index(self, force: bool = False):
        """Sincronización incremental ultrarrápida: solo lee archivos modificados."""
        if not self.vault_dir.exists():
            return

        now = time.time()
        if not force and (now - self._last_sync) < self.sync_interval:
            return
        self._last_sync = now

        target_dirs = {
            "memory": [
                self.vault_dir / "04-APRENDIZAJES" / "decisiones",
                self.vault_dir / "04-APRENDIZAJES" / "errores"
            ],
            "knowledge": [
                self.vault_dir / "03-CONOCIMIENTO"
            ],
            "projects": [
                self.vault_dir / "02-PROYECTOS"
            ]
        }

        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT path, mtime, size FROM files_meta")
            existing_meta = {row["path"]: (row["mtime"], row["size"]) for row in cur.fetchall()}

            current_paths = set()

            for doc_type, dirs in target_dirs.items():
                for d in dirs:
                    if not d.exists():
                        continue
                    for f in d.rglob("*.md"):
                        try:
                            rel_path = f.relative_to(self.vault_dir).as_posix()
                            current_paths.add(rel_path)
                            stat = f.stat()
                            mtime = stat.st_mtime
                            size = stat.st_size

                            prev = existing_meta.get(rel_path)
                            if not force and prev and abs(prev[0] - mtime) < 0.001 and prev[1] == size:
                                continue  # Archivo sin cambios

                            content = f.read_text(encoding="utf-8", errors="ignore")
                            meta, body = self._parse_frontmatter(content)
                            title = meta["title"] or f.stem
                            title = title.replace("-", " ").strip()

                            cur.execute("""
                                INSERT INTO files_meta(path, mtime, size, doc_type)
                                VALUES(?, ?, ?, ?)
                                ON CONFLICT(path) DO UPDATE SET mtime=excluded.mtime, size=excluded.size, doc_type=excluded.doc_type
                            """, (rel_path, mtime, size, doc_type))

                            if doc_type == "memory":
                                cur.execute("DELETE FROM memories WHERE path = ?", (rel_path,))
                                cur.execute("""
                                    INSERT INTO memories (path, title, content, project, tags, pinned, updated_at)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    rel_path, title, body,
                                    meta["project"], " ".join(meta["tags"]),
                                    meta["pinned"], meta["date"] or datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
                                ))
                                row_id = cur.lastrowid
                                cur.execute("""
                                    INSERT INTO memories_fts(rowid, title, content, project, tags)
                                    VALUES(?, ?, ?, ?, ?)
                                """, (row_id, title, body, meta["project"], " ".join(meta["tags"])))

                            elif doc_type in ["knowledge", "projects"]:
                                cur.execute("DELETE FROM knowledge WHERE path = ?", (rel_path,))
                                category = rel_path.split("/")[1] if "/" in rel_path else "general"
                                cur.execute("""
                                    INSERT INTO knowledge (path, title, content, category, updated_at)
                                    VALUES (?, ?, ?, ?, ?)
                                """, (
                                    rel_path, title, body, category,
                                    meta["date"] or datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
                                ))
                                row_id = cur.lastrowid
                                cur.execute("""
                                    INSERT INTO knowledge_fts(rowid, title, content, category)
                                    VALUES(?, ?, ?, ?)
                                """, (row_id, title, body, category))

                        except Exception:
                            continue

            # Limpiar archivos borrados
            deleted = set(existing_meta.keys()) - current_paths
            for del_path in deleted:
                cur.execute("DELETE FROM files_meta WHERE path = ?", (del_path,))
                cur.execute("DELETE FROM memories WHERE path = ?", (del_path,))
                cur.execute("DELETE FROM knowledge WHERE path = ?", (del_path,))

            conn.commit()

    def search_memories(self, query: str, project_filter: str = "", limit: int = 6, max_chars: int = 3500):
        """Búsqueda con reranking compuesto determinista estilo Engram v2."""
        self.sync_index()
        fts_query = self._sanitize_fts_query(query)
        if not fts_query:
            return "Indique al menos un término válido para consultar la memoria."

        now_ts = datetime.now().timestamp()
        results = []

        with self._get_conn() as conn:
            cur = conn.cursor()
            sql = """
                SELECT m.id, m.path, m.title, m.content, m.project, m.tags, m.pinned, m.updated_at,
                       bm25(memories_fts) AS bm25_rank
                FROM memories_fts f
                JOIN memories m ON m.id = f.rowid
                WHERE memories_fts MATCH ?
            """
            params = [fts_query]
            if project_filter:
                sql += " AND (LOWER(m.project) LIKE ? OR LOWER(m.content) LIKE ?)"
                pf = f"%{project_filter.lower().strip()}%"
                params.extend([pf, pf])

            try:
                cur.execute(sql, params)
                rows = cur.fetchall()
            except Exception:
                rows = []

            for r in rows:
                # bm25() en SQLite devuelve valores negativos (menor = mejor)
                base_score = -r["bm25_rank"] if r["bm25_rank"] is not None else 1.0

                # 1. Pinned Bonus (+15.0)
                pinned_bonus = 15.0 if r["pinned"] else 0.0

                # 2. Recency Bonus (decaimiento exponencial suave)
                recency_bonus = 0.0
                if r["updated_at"]:
                    try:
                        dt = datetime.strptime(r["updated_at"][:10], "%Y-%m-%d")
                        days_diff = max(0, (now_ts - dt.timestamp()) / 86400)
                        recency_bonus = 5.0 / (1.0 + (days_diff / 45.0))
                    except Exception:
                        pass

                # 3. Exact Title Bonus (+10.0)
                exact_title = 10.0 if query.lower() in r["title"].lower() else 0.0

                composite_score = base_score + pinned_bonus + recency_bonus + exact_title
                results.append((composite_score, r))

        results.sort(key=lambda x: x[0], reverse=True)

        if not results:
            return f"No se encontraron memorias previas relacionadas con '{query}'."

        output_lines = []
        total_len = 0

        for score, r in results[:limit]:
            snippet = re.sub(r"\s+", " ", r["content"][:300]).strip()
            item = f"- **[[{r['title']}]]** (Score: {score:.1f}, Proyecto: {r['project'] or 'General'})\n  {snippet}..."
            if total_len + len(item) > max_chars:
                break
            output_lines.append(item)
            total_len += len(item)

        header = f"🧠 Memorias recuperadas para '{query}'"
        if project_filter:
            header += f" [Filtro: {project_filter}]"
        return f"### {header}:\n" + "\n\n".join(output_lines)

    def search_knowledge(self, query: str, limit: int = 5, max_chars: int = 3500):
        """Búsqueda instantánea FTS5 sobre notas técnicas y patrones arquitectónicos."""
        self.sync_index()
        fts_query = self._sanitize_fts_query(query)
        if not fts_query:
            return f"No se encontraron notas sobre '{query}'."

        results = []
        with self._get_conn() as conn:
            cur = conn.cursor()
            sql = """
                SELECT k.id, k.path, k.title, k.content, k.category,
                       bm25(knowledge_fts) AS bm25_rank
                FROM knowledge_fts f
                JOIN knowledge k ON k.id = f.rowid
                WHERE knowledge_fts MATCH ?
                ORDER BY bm25_rank ASC
                LIMIT ?
            """
            try:
                cur.execute(sql, [fts_query, limit * 2])
                rows = cur.fetchall()
            except Exception:
                rows = []

            for r in rows:
                score = -r["bm25_rank"] if r["bm25_rank"] is not None else 1.0
                if query.lower() in r["title"].lower():
                    score += 10.0
                results.append((score, r))

        results.sort(key=lambda x: x[0], reverse=True)

        if not results:
            return f"No se encontraron notas sobre '{query}'."

        output_blocks = []
        total_len = 0

        for score, r in results[:limit]:
            snippet = r["content"][:350].strip()
            block = f"### [[{r['title']}]] ({r['category']})\n{snippet}..."
            if total_len + len(block) > max_chars:
                break
            output_blocks.append(block)
            total_len += len(block)

        return "\n\n".join(output_blocks)

    def search_vault(self, query: str, max_results: int = 8, max_chars: int = 5000):
        """Búsqueda transversal en todo el Vault acotada por presupuesto de contexto."""
        self.sync_index()
        fts_query = self._sanitize_fts_query(query)
        if not fts_query:
            return f"No se encontraron notas relacionadas con '{query}'."

        matches = []
        with self._get_conn() as conn:
            cur = conn.cursor()
            # Buscar en knowledge y en memories
            cur.execute("""
                SELECT k.path, k.title, k.content, bm25(knowledge_fts) as rank
                FROM knowledge_fts f
                JOIN knowledge k ON k.id = f.rowid
                WHERE knowledge_fts MATCH ?
                ORDER BY rank ASC LIMIT ?
            """, (fts_query, max_results))
            for r in cur.fetchall():
                matches.append((-r["rank"], r["path"], r["title"], r["content"][:400]))

            cur.execute("""
                SELECT m.path, m.title, m.content, bm25(memories_fts) as rank
                FROM memories_fts f
                JOIN memories m ON m.id = f.rowid
                WHERE memories_fts MATCH ?
                ORDER BY rank ASC LIMIT ?
            """, (fts_query, max_results))
            for r in cur.fetchall():
                matches.append((-r["rank"] + 5.0, r["path"], r["title"], r["content"][:400]))

        matches.sort(key=lambda x: x[0], reverse=True)
        if not matches:
            return f"No se encontraron notas del Vault relacionadas con '{query}'."

        lines = [f"Resultados transversales del Vault para '{query}':"]
        total_len = len(lines[0])

        for score, path, title, snippet in matches[:max_results]:
            clean_snip = re.sub(r"\s+", " ", snippet).strip()
            item = f"\n### {path} (Score: {score:.1f})\n**{title}**: {clean_snip}..."
            if total_len + len(item) > max_chars:
                break
            lines.append(item)
            total_len += len(item)

        return "\n".join(lines)
