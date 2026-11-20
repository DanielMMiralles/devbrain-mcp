"""
DevBrain Hybrid Indexer v4.0 (SQLite FTS5 BM25 + Embedded Vector Search RRF + Bi-Temporal Memory)
Ultra-fast, in-process, outside OneDrive (~/.devbrain/cortex_fts.db) with OneDrive placeholder guard.
"""
from __future__ import annotations

import atexit
import hashlib
import math
import os
import re
import sqlite3
import sys
import time
import unicodedata
import weakref
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import numpy as np  # type: ignore
    _HAS_NUMPY = True
except Exception:
    np = None  # type: ignore
    _HAS_NUMPY = False

from decision_ledger import devbrain_home


# Clústeres semánticos bilingües ES/EN para que búsquedas conceptuales conecten sinónimos sin LLM
_SEMANTIC_CLUSTERS: List[Tuple[str, ...]] = [
    ("auth", "oauth", "oauth2", "jwt", "token", "login", "sesion", "session", "rbac", "permiso", "permisos", "credencial", "sso"),
    ("database", "db", "postgres", "postgresql", "supabase", "sqlite", "sql", "migracion", "migration", "esquema", "schema", "tabla", "rls", "indice", "index"),
    ("cache", "redis", "memcached", "latencia", "latency", "rendimiento", "performance", "velocidad", "speed", "bottleneck", "cuello"),
    ("ui", "ux", "frontend", "react", "tailwind", "shadcn", "css", "diseno", "design", "interfaz", "dashboard", "componente", "tipografia"),
    ("agent", "agente", "agentes", "mcp", "odd", "dodd", "memoria", "memory", "sinapsis", "synapse", "vault", "engram", "antigravity", "subagente"),
    ("queue", "cola", "colas", "worker", "workers", "kafka", "rabbitmq", "job", "jobs", "evento", "events", "bus", "async", "asincrono"),
    ("test", "tests", "testing", "qa", "playwright", "pytest", "unittest", "vitest", "e2e", "bug", "error", "fallo", "regression"),
    ("docker", "k8s", "kubernetes", "helm", "terraform", "deploy", "despliegue", "ci", "cd", "pipeline", "container", "contenedor"),
    ("api", "rest", "graphql", "grpc", "endpoint", "webhook", "backend", "nestjs", "fastapi", "contrato", "pydantic"),
    ("security", "seguridad", "secret", "secreto", "secrets", "xss", "csrf", "injection", "vulnerabilidad", "hardening"),
]
_TOKEN_TO_CLUSTER: Dict[str, str] = {}
for _cid, _terms in enumerate(_SEMANTIC_CLUSTERS):
    _cname = f"__cluster_{_cid}__"
    for _t in _terms:
        _TOKEN_TO_CLUSTER[_t] = _cname


def _is_cloud_placeholder(path: Path) -> bool:
    """Evita hidratar archivos 'solo en la nube' de OneDrive (Files On-Demand)."""
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
        if attrs == -1:
            return False
        # FILE_ATTRIBUTE_OFFLINE (0x1000) o FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS (0x00400000)
        return bool((attrs & 0x00400000) or (attrs & 0x1000))
    except Exception:
        return False


class HybridVectorizer:
    """Vectorizador local de 256 dimensiones (ES/EN semantic clusters + tokens + char n-grams)."""

    DIMS = 256

    @staticmethod
    def _normalize(text: str) -> str:
        t = unicodedata.normalize("NFKD", (text or "").lower()).encode("ascii", "ignore").decode("ascii")
        return re.sub(r"[^a-z0-9_\-\s]", " ", t)

    @classmethod
    def _feature_hashes(cls, text: str) -> List[Tuple[int, float]]:
        norm = cls._normalize(text)
        tokens = [tok for tok in norm.split() if len(tok) >= 2]
        feats: List[Tuple[str, float]] = []

        for tok in tokens[:220]:
            feats.append((f"w:{tok}", 1.5))
            cluster = _TOKEN_TO_CLUSTER.get(tok)
            if cluster:
                feats.append((cluster, 2.2))
            if len(tok) >= 4:
                for i in range(len(tok) - 2):
                    feats.append((f"g:{tok[i:i+3]}", 0.45))

        out: List[Tuple[int, float]] = []
        for fkey, weight in feats:
            digest = hashlib.blake2b(fkey.encode("utf-8"), digest_size=4).digest()
            val = int.from_bytes(digest, "little")
            idx = val % cls.DIMS
            sign = 1.0 if ((val >> 31) & 1) == 0 else -1.0
            out.append((idx, sign * weight))
        return out

    @classmethod
    def encode(cls, text: str):
        pairs = cls._feature_hashes(text)
        if _HAS_NUMPY:
            vec = np.zeros(cls.DIMS, dtype=np.float32)
            for idx, w in pairs:
                vec[idx] += w
            norm = float(np.linalg.norm(vec))
            if norm > 1e-9:
                vec /= norm
            return vec.astype(np.float16)

        vec_py = [0.0] * cls.DIMS
        for idx, w in pairs:
            vec_py[idx] += w
        norm = math.sqrt(sum(v * v for v in vec_py))
        if norm > 1e-9:
            vec_py = [v / norm for v in vec_py]
        return vec_py

    @classmethod
    def to_blob(cls, text: str) -> bytes:
        vec = cls.encode(text)
        if _HAS_NUMPY:
            return vec.tobytes()
        import array
        return array.array("f", vec).tobytes()

    @classmethod
    def from_blob(cls, blob: bytes):
        if _HAS_NUMPY:
            if len(blob) == cls.DIMS * 2:
                return np.frombuffer(blob, dtype=np.float16).astype(np.float32)
            if len(blob) == cls.DIMS * 4:
                return np.frombuffer(blob, dtype=np.float32)
            return np.zeros(cls.DIMS, dtype=np.float32)
        import array
        arr = array.array("f")
        if len(blob) == cls.DIMS * 4:
            arr.frombytes(blob)
            return list(arr)
        return [0.0] * cls.DIMS

    @classmethod
    def cosine_batch(cls, query_text: str, blobs: List[bytes]) -> List[float]:
        if not blobs:
            return []
        if _HAS_NUMPY:
            q = cls.encode(query_text).astype(np.float32)
            mat = np.vstack([cls.from_blob(b) for b in blobs])
            scores = mat @ q
            return [float(x) for x in scores]
        q_py = cls.encode(query_text)
        res = []
        for b in blobs:
            v = cls.from_blob(b)
            res.append(sum(a * c for a, c in zip(q_py, v)))
        return res


EPISTEMIC_LENSES: Dict[str, Dict[str, Any]] = {
    "antithesis": {
        "allow_vault_memory": False,
        "blocked_tags": {"*"},
    },
    "ui": {
        "allow_vault_memory": True,
        "blocked_tags": {"sql", "rls", "migration", "scada-dense", "backend"},
    },
    "backend": {
        "allow_vault_memory": True,
        "blocked_tags": {"ui", "ux", "css", "typography", "palette", "tokens", "density", "scada-dense"},
    },
    "data": {
        "allow_vault_memory": True,
        "blocked_tags": {"ui", "ux", "css", "typography", "palette", "tokens", "density", "scada-dense"},
    },
    "qa": {
        "allow_vault_memory": True,
        "blocked_tags": {"palette", "typography"},
    },
}

_ROLE_ALIASES: Dict[str, str] = {
    "odd-antithesis": "antithesis",
    "antithesis": "antithesis",
    "odd-ui-crafter": "ui",
    "ui": "ui",
    "odd-backend-architect": "backend",
    "backend": "backend",
    "odd-data-guardian": "data",
    "data": "data",
    "odd-qa-sentinel": "qa",
    "qa": "qa",
}


def normalize_agent_role(role: str) -> str:
    return _ROLE_ALIASES.get((role or "").strip().lower(), "")


class DevBrainIndex:
    def __init__(self, vault_dir: Path, db_path: Path = None):
        self.vault_dir = Path(vault_dir).resolve()
        self._last_sync = 0.0
        self.sync_interval = 300.0
        self._conn = None
        self._cache = {}
        self._vec_cache: Dict[str, Tuple[List[int], Any]] = {}
        if db_path is None:
            local_db = devbrain_home() / "cortex_fts.db"
            legacy_db = self.vault_dir / "06-SISTEMA" / "cache" / "devbrain_fts.db"
            skip_mig = os.environ.get("DEVBRAIN_SKIP_LEGACY_MIGRATION") == "1"
            # Migración única automática de OneDrive -> ~/.devbrain/cortex_fts.db usando SQLite backup API
            if not skip_mig and not local_db.exists() and legacy_db.exists():
                try:
                    local_db.parent.mkdir(parents=True, exist_ok=True)
                    src = sqlite3.connect(str(legacy_db), timeout=5.0)
                    dst = sqlite3.connect(str(local_db), timeout=5.0)
                    src.backup(dst)
                    dst.close()
                    src.close()
                except Exception:
                    pass
            self.db_path = local_db
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            self.db_path = Path(db_path).resolve()
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.synapse_engine = None
        try:
            from neuroplasticity import SynapticEngine
            self.synapse_engine = SynapticEngine(self.db_path)
        except Exception:
            pass

        self._init_db()
        is_empty = True
        try:
            with self._get_conn() as conn:
                row = conn.execute("SELECT count(*) as cnt FROM files_meta").fetchone()
                if row and row["cnt"] > 0:
                    is_empty = False
        except Exception:
            pass

        skip_mig = os.environ.get("DEVBRAIN_SKIP_LEGACY_MIGRATION") == "1"
        if is_empty and not (db_path is None and skip_mig):
            self.sync_index(force=True, fast_only=False)
        else:
            self._last_sync = time.time()

        _ref = weakref.ref(self)
        atexit.register(lambda r=_ref: (obj := r()) and obj.close())

    def close(self):
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    def __del__(self):
        self.close()

    def _get_conn(self):
        if self._conn is not None:
            return self._conn
        conn = sqlite3.connect(str(self.db_path), timeout=10.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA cache_size = -64000")
            conn.execute("PRAGMA temp_store = MEMORY")
            conn.execute("PRAGMA mmap_size = 268435456")
            conn.execute("PRAGMA busy_timeout = 4000")
        except Exception:
            pass
        self._conn = conn
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
                    updated_at TEXT,
                    valid_from TEXT DEFAULT '',
                    valid_until TEXT DEFAULT '',
                    superseded_by TEXT DEFAULT ''
                )
            """)
            for col_def in (
                "ALTER TABLE memories ADD COLUMN valid_from TEXT DEFAULT ''",
                "ALTER TABLE memories ADD COLUMN valid_until TEXT DEFAULT ''",
                "ALTER TABLE memories ADD COLUMN superseded_by TEXT DEFAULT ''",
            ):
                try:
                    cur.execute(col_def)
                except Exception:
                    pass

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
            cur.execute("""
                CREATE TABLE IF NOT EXISTS doc_vectors (
                    doc_type TEXT NOT NULL,
                    doc_id INTEGER NOT NULL,
                    vec BLOB NOT NULL,
                    PRIMARY KEY (doc_type, doc_id)
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
        meta = {
            "tags": [], "project": "", "title": "", "pinned": 0, "date": "",
            "valid_from": "", "valid_until": "", "superseded_by": ""
        }
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
                raw_proj = v.replace("[[", "").replace("]]", "").strip()
                try:
                    from ontology_engine import resolve_project
                    meta["project"] = resolve_project(raw_proj)
                except Exception:
                    meta["project"] = raw_proj
            elif k in ["fecha", "date", "created"]:
                meta["date"] = v
            elif k in ["title", "titulo"]:
                meta["title"] = v
            elif k == "pinned":
                meta["pinned"] = 1 if v.lower() in ["true", "1", "yes"] else 0
            elif k in ["valid_from", "valid_until", "superseded_by"]:
                meta[k] = v

        if not meta["valid_from"] and meta["date"]:
            meta["valid_from"] = meta["date"]
        return meta, body

    def _upsert_vector(self, cur: sqlite3.Cursor, doc_type: str, doc_id: int, text: str) -> None:
        blob = HybridVectorizer.to_blob(text[:2000])
        cur.execute(
            "INSERT INTO doc_vectors(doc_type, doc_id, vec) VALUES(?, ?, ?) "
            "ON CONFLICT(doc_type, doc_id) DO UPDATE SET vec=excluded.vec",
            (doc_type, doc_id, blob),
        )

    def ensure_vectors(self, doc_type: str = "memory", limit: int = 500) -> int:
        """Vectoriza filas existentes sin vector (idempotente y acotado)."""
        table = "memories" if doc_type == "memory" else "knowledge"
        created = 0
        with self._get_conn() as conn:
            cur = conn.cursor()
            rows = cur.execute(
                f"""
                SELECT t.id, t.title, t.content
                FROM {table} t
                LEFT JOIN doc_vectors v ON v.doc_type = ? AND v.doc_id = t.id
                WHERE v.doc_id IS NULL
                LIMIT ?
                """,
                (doc_type, limit),
            ).fetchall()
            for r in rows:
                self._upsert_vector(cur, doc_type, int(r["id"]), f"{r['title']} {r['content']}")
                created += 1
            if created:
                conn.commit()
                self._vec_cache.pop(doc_type, None)
        return created

    def _top_vector_ids(self, doc_type: str, query: str, top_k: int, min_score: float) -> List[Tuple[int, float]]:
        """Calcula top-k por similitud coseno usando matriz cacheada en RAM (sin leer content)."""
        cached = self._vec_cache.get(doc_type)
        if cached is None:
            with self._get_conn() as conn:
                rows = conn.execute(
                    "SELECT doc_id, vec FROM doc_vectors WHERE doc_type = ?",
                    (doc_type,),
                ).fetchall()
            if not rows:
                return []
            ids = [int(r["doc_id"]) for r in rows]
            if _HAS_NUMPY:
                mat = np.vstack([HybridVectorizer.from_blob(r["vec"]) for r in rows])
                cached = (ids, mat)
            else:
                cached = (ids, [r["vec"] for r in rows])
            self._vec_cache[doc_type] = cached

        ids, payload = cached
        if not ids:
            return []
        if _HAS_NUMPY:
            q = HybridVectorizer.encode(query).astype(np.float32)
            scores = payload @ q
            k = min(top_k, len(ids))
            if k < len(ids):
                part = np.argpartition(scores, -k)[-k:]
                top_idx = part[np.argsort(scores[part])[::-1]]
            else:
                top_idx = np.argsort(scores)[::-1]
            return [(ids[int(i)], float(scores[int(i)])) for i in top_idx if float(scores[int(i)]) > min_score]

        cos_scores = HybridVectorizer.cosine_batch(query, payload)
        scored = sorted(zip(ids, cos_scores), key=lambda x: x[1], reverse=True)
        return [(did, cs) for did, cs in scored[:top_k] if cs > min_score]

    def sync_index(self, force: bool = False, fast_only: bool = True):
        """Sincronización incremental ultrarrápida; con fast_only=True evita recorrer 6k notas en OneDrive."""
        if not self.vault_dir.exists():
            return

        now = time.time()
        if not force and (now - self._last_sync) < self.sync_interval:
            return
        self._last_sync = now

        with self._get_conn() as conn:
            cur = conn.cursor()
            has_data = cur.execute("SELECT count(*) FROM files_meta").fetchone()[0] > 0

        if force or not has_data or not fast_only:
            target_dirs = {
                "memory": [
                    self.vault_dir / "04-APRENDIZAJES" / "decisiones",
                    self.vault_dir / "04-APRENDIZAJES" / "errores",
                ],
                "knowledge": [self.vault_dir / "03-CONOCIMIENTO"],
                "projects": [self.vault_dir / "02-PROYECTOS"],
            }
            track_deletions_for = {"memory", "knowledge", "projects"}
        else:
            target_dirs = {
                "memory": [
                    self.vault_dir / "04-APRENDIZAJES" / "decisiones",
                    self.vault_dir / "04-APRENDIZAJES" / "errores",
                ],
            }
            track_deletions_for = {"memory"}

        with self._get_conn() as conn:
            cur = conn.cursor()
            existing_meta = {
                row["path"]: (row["mtime"], row["size"], row["doc_type"])
                for row in cur.execute("SELECT path, mtime, size, doc_type FROM files_meta").fetchall()
            }
            seen_by_type: Dict[str, set] = {dt: set() for dt in track_deletions_for}

            for doc_type, dirs in target_dirs.items():
                for d in dirs:
                    if not d.exists():
                        continue
                    for f in d.rglob("*.md"):
                        try:
                            if _is_cloud_placeholder(f):
                                continue
                            rel_path = f.relative_to(self.vault_dir).as_posix()
                            if doc_type in seen_by_type:
                                seen_by_type[doc_type].add(rel_path)
                            stat = f.stat()
                            mtime = stat.st_mtime
                            size = stat.st_size

                            prev = existing_meta.get(rel_path)
                            if not force and prev and abs(prev[0] - mtime) < 0.001 and prev[1] == size:
                                continue

                            content = f.read_text(encoding="utf-8", errors="ignore")
                            meta, body = self._parse_frontmatter(content)
                            title = (meta["title"] or f.stem).replace("-", " ").strip()

                            cur.execute(
                                """
                                INSERT INTO files_meta(path, mtime, size, doc_type)
                                VALUES(?, ?, ?, ?)
                                ON CONFLICT(path) DO UPDATE SET mtime=excluded.mtime, size=excluded.size, doc_type=excluded.doc_type
                                """,
                                (rel_path, mtime, size, doc_type),
                            )

                            if doc_type == "memory":
                                old_row = cur.execute("SELECT id FROM memories WHERE path = ?", (rel_path,)).fetchone()
                                if old_row:
                                    cur.execute("DELETE FROM doc_vectors WHERE doc_type = 'memory' AND doc_id = ?", (old_row["id"],))
                                    cur.execute("DELETE FROM memories WHERE id = ?", (old_row["id"],))
                                cur.execute(
                                    """
                                    INSERT INTO memories (path, title, content, project, tags, pinned, updated_at, valid_from, valid_until, superseded_by)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    """,
                                    (
                                        rel_path, title, body,
                                        meta["project"], " ".join(meta["tags"]),
                                        meta["pinned"], meta["date"] or datetime.fromtimestamp(mtime).strftime("%Y-%m-%d"),
                                        meta["valid_from"], meta["valid_until"], meta["superseded_by"],
                                    ),
                                )
                                row_id = cur.lastrowid
                                cur.execute(
                                    "INSERT INTO memories_fts(rowid, title, content, project, tags) VALUES(?, ?, ?, ?, ?)",
                                    (row_id, title, body, meta["project"], " ".join(meta["tags"])),
                                )
                                self._upsert_vector(cur, "memory", int(row_id), f"{title} {body}")

                            elif doc_type in ["knowledge", "projects"]:
                                old_row = cur.execute("SELECT id FROM knowledge WHERE path = ?", (rel_path,)).fetchone()
                                if old_row:
                                    cur.execute("DELETE FROM doc_vectors WHERE doc_type = 'knowledge' AND doc_id = ?", (old_row["id"],))
                                    cur.execute("DELETE FROM knowledge WHERE id = ?", (old_row["id"],))
                                category = rel_path.split("/")[1] if "/" in rel_path else "general"
                                cur.execute(
                                    "INSERT INTO knowledge (path, title, content, category, updated_at) VALUES (?, ?, ?, ?, ?)",
                                    (rel_path, title, body, category, meta["date"] or datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")),
                                )
                                row_id = cur.lastrowid
                                cur.execute(
                                    "INSERT INTO knowledge_fts(rowid, title, content, category) VALUES(?, ?, ?, ?)",
                                    (row_id, title, body, category),
                                )
                                self._upsert_vector(cur, "knowledge", int(row_id), f"{title} {body}")

                        except Exception:
                            continue

            for path_str, (_, _, dt) in existing_meta.items():
                if dt in track_deletions_for and path_str not in seen_by_type[dt]:
                    cur.execute("DELETE FROM files_meta WHERE path = ?", (path_str,))
                    if dt == "memory":
                        cur.execute("DELETE FROM memories WHERE path = ?", (path_str,))
                    else:
                        cur.execute("DELETE FROM knowledge WHERE path = ?", (path_str,))

            conn.commit()
        self._cache.clear()
        self._vec_cache.clear()

        if self.synapse_engine and force:
            try:
                self.synapse_engine.decay_synapses(half_life_days=30.0)
                self.synapse_engine.prune_synapses(min_weight=0.05)
            except Exception:
                pass

    def supersede_memory(self, query_or_title: str, new_title: str) -> int:
        """Marca memorias previas coincidentes como reemplazadas bi-temporalmente."""
        q = (query_or_title or "").strip().lower()
        if not q:
            return 0
        today = datetime.now().strftime("%Y-%m-%d")
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE memories
                SET valid_until = ?, superseded_by = ?
                WHERE (LOWER(title) LIKE ? OR LOWER(content) LIKE ?)
                  AND (valid_until IS NULL OR valid_until = '')
                  AND LOWER(title) != ?
                """,
                (today, new_title, f"%{q}%", f"%{q}%", new_title.lower()),
            )
            conn.commit()
            self._cache.clear()
            return cur.rowcount

    def search_memories(self, query: str, project_filter: str = "", limit: int = 6,
                        max_chars: int = 3500, session_nodes: list = None,
                        include_historical: bool = False,
                        agent_role: str = "", quarantine: bool = False):
        """Búsqueda híbrida (FTS5 BM25 + Vector Cos + RRF + Pinned + Recency + Sinapsis) con lente epistémico y filtro bi-temporal."""
        role_key = normalize_agent_role(agent_role)
        if role_key == "antithesis":
            return "Aislamiento D-ODD (`antithesis`): 0 memorias del Vault inyectadas."

        cache_key = (
            f"m_{query.strip().lower()}_{project_filter}_{limit}_{max_chars}_"
            f"{tuple(session_nodes or [])}_{include_historical}_{role_key}_{quarantine}"
        )
        if cache_key in self._cache:
            res, t_cached = self._cache[cache_key]
            if time.time() - t_cached < 120.0:
                return res

        self.sync_index(fast_only=True)
        self.ensure_vectors("memory", limit=500)
        fts_query = self._sanitize_fts_query(query)
        if not query.strip():
            return "Indique al menos un término válido para consultar la memoria."

        now_ts = datetime.now().timestamp()
        pf = project_filter.lower().strip()
        try:
            from ontology_engine import resolve_project
            pf_canon = resolve_project(project_filter).lower() if pf else ""
        except Exception:
            pf_canon = pf

        temporal_clause = "" if include_historical else " AND (m.valid_until IS NULL OR m.valid_until = '') AND (m.superseded_by IS NULL OR m.superseded_by = '')"
        strict_proj = bool(quarantine and pf)

        bm25_ranks: Dict[int, int] = {}
        vec_ranks: Dict[int, int] = {}
        rows_by_id: Dict[int, sqlite3.Row] = {}

        with self._get_conn() as conn:
            cur = conn.cursor()
            if fts_query:
                sql = (
                    "SELECT m.id, m.path, m.title, m.content, m.project, m.tags, m.pinned, m.updated_at, "
                    "m.valid_until, m.superseded_by, bm25(memories_fts) AS bm25_rank "
                    "FROM memories_fts f JOIN memories m ON m.id = f.rowid "
                    "WHERE memories_fts MATCH ?" + temporal_clause
                )
                params: List[object] = [fts_query]
                if pf:
                    if strict_proj:
                        sql += " AND (LOWER(m.project) LIKE ? OR LOWER(m.project) = ?)"
                        params.extend([f"%{pf}%", pf_canon])
                    else:
                        sql += " AND (LOWER(m.project) LIKE ? OR LOWER(m.project) = ? OR LOWER(m.content) LIKE ?)"
                        params.extend([f"%{pf}%", pf_canon, f"%{pf}%"])
                sql += " ORDER BY bm25_rank ASC LIMIT 30"
                try:
                    for rank_idx, r in enumerate(cur.execute(sql, params).fetchall()):
                        mid = int(r["id"])
                        bm25_ranks[mid] = rank_idx
                        rows_by_id[mid] = r
                except Exception:
                    pass

            # Rama Vectorial (encuentra sinónimos aunque no haya coincidencia exacta en FTS5)
            vec_sql = (
                "SELECT m.id, m.path, m.title, m.content, m.project, m.tags, m.pinned, m.updated_at, "
                "m.valid_until, m.superseded_by, v.vec "
                "FROM memories m JOIN doc_vectors v ON v.doc_type = 'memory' AND v.doc_id = m.id "
                "WHERE 1=1" + temporal_clause
            )
            vec_params: List[object] = []
            if pf:
                if strict_proj:
                    vec_sql += " AND (LOWER(m.project) LIKE ? OR LOWER(m.project) = ?)"
                    vec_params.extend([f"%{pf}%", pf_canon])
                else:
                    vec_sql += " AND (LOWER(m.project) LIKE ? OR LOWER(m.project) = ? OR LOWER(m.content) LIKE ?)"
                    vec_params.extend([f"%{pf}%", pf_canon, f"%{pf}%"])
            vrows = cur.execute(vec_sql, vec_params).fetchall()
            if vrows:
                cos_scores = HybridVectorizer.cosine_batch(query, [r["vec"] for r in vrows])
                scored_vecs = sorted(zip(cos_scores, vrows), key=lambda x: x[0], reverse=True)
                for rank_idx, (cs, r) in enumerate(scored_vecs[:30]):
                    if cs > 0.12:
                        mid = int(r["id"])
                        vec_ranks[mid] = rank_idx
                        if mid not in rows_by_id:
                            rows_by_id[mid] = r

        lens = EPISTEMIC_LENSES.get(role_key) if role_key else None
        if lens:
            blocked_tags = lens["blocked_tags"]
            filtered_rows: Dict[int, sqlite3.Row] = {}
            for mid, r in rows_by_id.items():
                mem_tags = set(re.findall(r"[\w\-]+", (r["tags"] or "").lower()))
                if blocked_tags & mem_tags:
                    continue
                if quarantine and pf_canon:
                    row_proj = (r["project"] or "").strip().lower()
                    if row_proj != pf_canon and pf not in row_proj:
                        continue
                filtered_rows[mid] = r
            rows_by_id = filtered_rows

        results = []
        for mid, r in rows_by_id.items():
            rrf = 0.0
            if mid in bm25_ranks:
                rrf += 1.0 / (60.0 + bm25_ranks[mid])
            if mid in vec_ranks:
                rrf += 1.0 / (60.0 + vec_ranks[mid])
            base_score = rrf * 600.0
            pinned_bonus = 15.0 if r["pinned"] else 0.0
            recency_bonus = 0.0
            if r["updated_at"]:
                try:
                    dt = datetime.strptime(r["updated_at"][:10], "%Y-%m-%d")
                    days_diff = max(0, (now_ts - dt.timestamp()) / 86400)
                    recency_bonus = 5.0 / (1.0 + (days_diff / 45.0))
                except Exception:
                    pass
            exact_title = 10.0 if query.lower() in r["title"].lower() else 0.0
            synaptic_bonus = 0.0
            if self.synapse_engine and session_nodes:
                node_key = r["title"].lower().replace(" ", "-")
                synaptic_bonus = self.synapse_engine.compute_synaptic_bonus(node_key, session_nodes, scale=0.5)
            composite_score = base_score + pinned_bonus + recency_bonus + exact_title + synaptic_bonus
            results.append((composite_score, r))

        results.sort(key=lambda x: x[0], reverse=True)
        if not results:
            return f"No se encontraron memorias previas relacionadas con '{query}'."

        output_lines = []
        total_len = 0
        for score, r in results[:limit]:
            snippet = re.sub(r"\s+", " ", r["content"][:300]).strip()
            sup = f" *(obsoleta por [[{r['superseded_by']}]])*" if r["superseded_by"] else ""
            item = f"- **[[{r['title']}]]**{sup} (Score: {score:.1f}, Proyecto: {r['project'] or 'General'})\n  {snippet}..."
            if total_len + len(item) > max_chars:
                break
            output_lines.append(item)
            total_len += len(item)

        header = f"🧠 Memorias recuperadas para '{query}'"
        if project_filter:
            header += f" [Filtro: {project_filter}]"
        final_output = f"### {header}:\n" + "\n\n".join(output_lines)
        self._cache[cache_key] = (final_output, time.time())
        return final_output

    def search_knowledge(self, query: str, limit: int = 5, max_chars: int = 3500, session_nodes: list = None):
        """Búsqueda híbrida instantánea FTS5 + Vector RRF enriquecida con conexiones sinápticas."""
        cache_key = f"k_{query.strip().lower()}_{limit}_{max_chars}_{tuple(session_nodes or [])}"
        if cache_key in self._cache:
            res, t_cached = self._cache[cache_key]
            if time.time() - t_cached < 120.0:
                return res

        self.sync_index(fast_only=True)
        self.ensure_vectors("knowledge", limit=350)
        fts_query = self._sanitize_fts_query(query)
        if not query.strip():
            return f"No se encontraron notas sobre '{query}'."

        bm25_ranks: Dict[int, int] = {}
        vec_ranks: Dict[int, int] = {}
        rows_by_id: Dict[int, sqlite3.Row] = {}

        with self._get_conn() as conn:
            cur = conn.cursor()
            if fts_query:
                try:
                    rows = cur.execute(
                        """
                        SELECT k.id, k.path, k.title, k.content, k.category, bm25(knowledge_fts) AS bm25_rank
                        FROM knowledge_fts f JOIN knowledge k ON k.id = f.rowid
                        WHERE knowledge_fts MATCH ? ORDER BY bm25_rank ASC LIMIT ?
                        """,
                        [fts_query, limit * 3],
                    ).fetchall()
                    for idx, r in enumerate(rows):
                        kid = int(r["id"])
                        bm25_ranks[kid] = idx
                        rows_by_id[kid] = r
                except Exception:
                    pass

            vec_hits = self._top_vector_ids("knowledge", query, limit * 3, 0.14)
            missing_ids = [kid for kid, _ in vec_hits if kid not in rows_by_id]
            if missing_ids:
                placeholders = ",".join("?" for _ in missing_ids)
                fetched = cur.execute(
                    f"SELECT id, path, title, content, category FROM knowledge WHERE id IN ({placeholders})",
                    missing_ids,
                ).fetchall()
                for r in fetched:
                    rows_by_id[int(r["id"])] = r
            for idx, (kid, _) in enumerate(vec_hits):
                if kid in rows_by_id:
                    vec_ranks[kid] = idx

        results = []
        for kid, r in rows_by_id.items():
            rrf = 0.0
            if kid in bm25_ranks:
                rrf += 1.0 / (60.0 + bm25_ranks[kid])
            if kid in vec_ranks:
                rrf += 1.0 / (60.0 + vec_ranks[kid])
            score = rrf * 600.0
            if query.lower() in r["title"].lower():
                score += 10.0
            if self.synapse_engine and session_nodes:
                node_key = r["title"].lower().replace(" ", "-")
                score += self.synapse_engine.compute_synaptic_bonus(node_key, session_nodes, scale=0.5)
            results.append((score, r))

        results.sort(key=lambda x: x[0], reverse=True)
        if not results:
            return f"No se encontraron notas sobre '{query}'."

        output_blocks = []
        total_len = 0
        for score, r in results[:limit]:
            snippet = r["content"][:350].strip()
            block = f"### [[{r['title']}]] ({r['category']})\n{snippet}..."
            if self.synapse_engine:
                node_key = r["title"].lower().replace(" ", "-")
                associated = self.synapse_engine.get_associated_nodes(node_key, limit=3)
                if associated:
                    conn_str = ", ".join(f"[[{a['key']}]]" for a in associated)
                    block += f"\n  🔗 *Sinapsis activas:* {conn_str}"
            if total_len + len(block) > max_chars:
                break
            output_blocks.append(block)
            total_len += len(block)

        final_res = "\n\n".join(output_blocks)
        self._cache[cache_key] = (final_res, time.time())
        return final_res

    def search_vault(self, query: str, max_results: int = 8, max_chars: int = 5000):
        """Búsqueda transversal en todo el Vault acotada por presupuesto de contexto."""
        self.sync_index(fast_only=True)
        fts_query = self._sanitize_fts_query(query)
        if not fts_query:
            return f"No se encontraron notas relacionadas con '{query}'."

        matches = []
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT k.path, k.title, k.content, bm25(knowledge_fts) as rank
                FROM knowledge_fts f JOIN knowledge k ON k.id = f.rowid
                WHERE knowledge_fts MATCH ? ORDER BY rank ASC LIMIT ?
                """,
                (fts_query, max_results),
            )
            for r in cur.fetchall():
                matches.append((-r["rank"], r["path"], r["title"], r["content"][:400]))

            cur.execute(
                """
                SELECT m.path, m.title, m.content, bm25(memories_fts) as rank
                FROM memories_fts f JOIN memories m ON m.id = f.rowid
                WHERE memories_fts MATCH ?
                  AND (m.valid_until IS NULL OR m.valid_until = '')
                ORDER BY rank ASC LIMIT ?
                """,
                (fts_query, max_results),
            )
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
