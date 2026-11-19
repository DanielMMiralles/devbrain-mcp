"""
ontology_engine.py: Ontología jerárquica de 4 niveles (Dimensiones -> Áreas -> Proyectos -> Actividades),
Instintos tipo ECC (project-scoping + auto-promoción), Session Lifecycle y Portada Viva materializada.

La base de datos `cortex.db` vive fuera de OneDrive (`devbrain_home() / "cortex.db"`) en SQLite WAL
para garantizar latencias < 15ms sin bloqueos ni escaneos recursivos en discos sincronizados.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from decision_ledger import devbrain_home, open_decisions, stats as ledger_stats

DEFAULT_VAULT = Path(r"C:\Users\damm1\OneDrive\Documentos\Obsidian Vault")
AUTO_START = "<!-- DEVBRAIN:AUTO:START -->"
AUTO_END = "<!-- DEVBRAIN:AUTO:END -->"
_ACTIVE_YAML_PATH: Optional[Path] = None


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _short_id(prefix: str, seed: str) -> str:
    h = hashlib.sha1(seed.encode("utf-8", errors="ignore")).hexdigest()[:8]
    return f"{prefix}-{h}"


def _resolve_vault_dir(vault_dir: Optional[Path] = None) -> Path:
    if vault_dir is not None:
        return Path(vault_dir)
    env_v = os.environ.get("VAULT_DIR") or os.environ.get("VAULT_PATH")
    if env_v:
        return Path(env_v)
    return DEFAULT_VAULT


def cortex_db_path() -> Path:
    return devbrain_home() / "cortex.db"


@contextlib.contextmanager
def _conn(db_path: Optional[Path] = None):
    path = db_path or cortex_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(path), timeout=5.0)
    con.row_factory = sqlite3.Row
    try:
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=NORMAL")
        con.execute("PRAGMA busy_timeout=4000")
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS ontology_meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS dimensions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                sort_order INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS areas (
                id TEXT PRIMARY KEY,
                dimension_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                area_id TEXT NOT NULL,
                name TEXT NOT NULL,
                repo_path TEXT DEFAULT '',
                status TEXT DEFAULT 'active',
                updated_at TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS project_aliases (
                alias_lower TEXT PRIMARY KEY,
                project_id TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS activities (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                title TEXT NOT NULL,
                status TEXT DEFAULT 'ready',
                blocked_by TEXT DEFAULT '',
                priority INTEGER DEFAULT 2,
                source TEXT DEFAULT 'manual',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS instincts (
                id TEXT PRIMARY KEY,
                scope_type TEXT NOT NULL,
                scope_id TEXT NOT NULL,
                trigger TEXT NOT NULL,
                pattern TEXT NOT NULL,
                confidence REAL DEFAULT 0.40,
                confirmations INTEGER DEFAULT 1,
                promoted_to TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS session_states (
                conversation_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                summary TEXT DEFAULT '',
                open_activities_json TEXT DEFAULT '[]',
                updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_activities_proj ON activities(project_id, status);
            CREATE INDEX IF NOT EXISTS idx_instincts_scope ON instincts(scope_type, scope_id, confidence DESC);
            CREATE INDEX IF NOT EXISTS idx_projects_area ON projects(area_id, status);
            """
        )
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def _parse_yaml_fallback(text: str) -> Dict[str, Any]:
    """Parser ligero de respaldo para ontologia.yaml cuando PyYAML no está disponible."""
    data: Dict[str, Any] = {"dimensions": []}
    cur_dim: Optional[Dict[str, Any]] = None
    cur_area: Optional[Dict[str, Any]] = None
    cur_proj: Optional[Dict[str, Any]] = None

    for raw in text.splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()

        if line.startswith("- id:") and indent <= 4:
            cur_dim = {"id": line.split(":", 1)[1].strip().strip("'\""), "areas": []}
            data["dimensions"].append(cur_dim)
            cur_area = None
            cur_proj = None
        elif cur_dim is not None and indent <= 6 and ":" in line and not line.startswith("- "):
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip().strip("'\"")
            if k == "order":
                try:
                    cur_dim[k] = int(v)
                except ValueError:
                    cur_dim[k] = 0
            elif k != "areas":
                cur_dim[k] = v
        elif line.startswith("- id:") and indent <= 8 and cur_dim is not None:
            cur_area = {"id": line.split(":", 1)[1].strip().strip("'\""), "projects": []}
            cur_dim["areas"].append(cur_area)
            cur_proj = None
        elif cur_area is not None and indent <= 10 and ":" in line and not line.startswith("- ") and cur_proj is None:
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip().strip("'\"")
            if k != "projects":
                cur_area[k] = v
        elif line.startswith("- id:") and indent >= 10 and cur_area is not None:
            cur_proj = {"id": line.split(":", 1)[1].strip().strip("'\""), "aliases": []}
            cur_area["projects"].append(cur_proj)
        elif cur_proj is not None and ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip()
            if k == "aliases" and v.startswith("[") and v.endswith("]"):
                cur_proj["aliases"] = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
            else:
                cur_proj[k] = v.strip("'\"").replace("\\\\", "\\")
    return data


def _load_ontology_yaml(yaml_path: Path) -> Dict[str, Any]:
    raw = yaml_path.read_text(encoding="utf-8", errors="replace")
    try:
        import yaml  # type: ignore
        parsed = yaml.safe_load(raw)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass
    return _parse_yaml_fallback(raw)


def sync_ontology_yaml(yaml_path: Optional[Path] = None, force: bool = False,
                       vault_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Carga ontologia.yaml y realiza upsert idempotente en cortex.db."""
    global _ACTIVE_YAML_PATH
    if yaml_path is not None:
        _ACTIVE_YAML_PATH = yaml_path
    vdir = _resolve_vault_dir(vault_dir)
    ypath = yaml_path or _ACTIVE_YAML_PATH or (vdir / "06-SISTEMA" / "ontologia.yaml")
    if not ypath.exists():
        return {"synced": False, "reason": f"No existe {ypath}", "dimensions": 0, "areas": 0, "projects": 0}

    try:
        mtime_str = f"{ypath.resolve()}:{ypath.stat().st_mtime:.3f}"
    except Exception:
        mtime_str = str(ypath)

    with _conn() as c:
        if not force:
            row = c.execute("SELECT value FROM ontology_meta WHERE key = 'yaml_mtime'").fetchone()
            if row and row["value"] == mtime_str:
                counts = {
                    "dimensions": c.execute("SELECT COUNT(*) FROM dimensions").fetchone()[0],
                    "areas": c.execute("SELECT COUNT(*) FROM areas").fetchone()[0],
                    "projects": c.execute("SELECT COUNT(*) FROM projects").fetchone()[0],
                }
                return {"synced": False, "cached": True, **counts}

        data = _load_ontology_yaml(ypath)
        dims = data.get("dimensions") or []
        now = _now_iso()
        n_dims = n_areas = n_projs = 0

        for idx, d in enumerate(dims, 1):
            did = str(d.get("id") or f"D{idx}").strip()
            c.execute(
                """
                INSERT INTO dimensions(id, name, description, sort_order) VALUES(?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET name=excluded.name, description=excluded.description, sort_order=excluded.sort_order
                """,
                (did, str(d.get("name") or did), str(d.get("description") or ""), int(d.get("order") or idx)),
            )
            n_dims += 1

            for a in d.get("areas") or []:
                aid = str(a.get("id") or "").strip()
                if not aid:
                    continue
                c.execute(
                    """
                    INSERT INTO areas(id, dimension_id, name, description) VALUES(?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET dimension_id=excluded.dimension_id, name=excluded.name, description=excluded.description
                    """,
                    (aid, did, str(a.get("name") or aid), str(a.get("description") or "")),
                )
                n_areas += 1

                for p in a.get("projects") or []:
                    pid = str(p.get("id") or "").strip()
                    if not pid:
                        continue
                    pname = str(p.get("name") or pid)
                    rpath = str(p.get("repo_path") or "").strip()
                    pstatus = str(p.get("status") or "active").strip()
                    c.execute(
                        """
                        INSERT INTO projects(id, area_id, name, repo_path, status, updated_at)
                        VALUES(?, ?, ?, ?, ?, ?)
                        ON CONFLICT(id) DO UPDATE SET
                            area_id=excluded.area_id, name=excluded.name,
                            repo_path=excluded.repo_path, status=excluded.status, updated_at=excluded.updated_at
                        """,
                        (pid, aid, pname, rpath, pstatus, now),
                    )
                    n_projs += 1

                    aliases = set(str(al).strip().lower() for al in (p.get("aliases") or []) if str(al).strip())
                    aliases.add(pid.lower())
                    aliases.add(pname.lower())
                    for al in aliases:
                        c.execute(
                            "INSERT INTO project_aliases(alias_lower, project_id) VALUES(?, ?) "
                            "ON CONFLICT(alias_lower) DO UPDATE SET project_id=excluded.project_id",
                            (al, pid),
                        )

        c.execute(
            "INSERT INTO ontology_meta(key, value) VALUES('yaml_mtime', ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (mtime_str,),
        )
        return {"synced": True, "cached": False, "dimensions": n_dims, "areas": n_areas, "projects": n_projs}


def _ensure_synced() -> None:
    try:
        sync_ontology_yaml(force=False)
    except Exception:
        pass


def resolve_project(name_or_path: str) -> str:
    """Resuelve un nombre, alias o ruta de disco al project_id canónico."""
    raw = (name_or_path or "").strip()
    if not raw:
        return "General"
    _ensure_synced()
    norm = raw.lower().rstrip("\\/")

    with _conn() as c:
        row = c.execute("SELECT project_id FROM project_aliases WHERE alias_lower = ?", (norm,)).fetchone()
        if row:
            return row["project_id"]

        # Intentar por basename si parece ruta
        base = Path(raw).name.lower()
        if base and base != norm:
            row = c.execute("SELECT project_id FROM project_aliases WHERE alias_lower = ?", (base,)).fetchone()
            if row:
                return row["project_id"]

        # Intentar coincidencia por prefijo de repo_path
        rows = c.execute("SELECT id, repo_path FROM projects WHERE repo_path != ''").fetchall()
        norm_path = norm.replace("/", "\\")
        best_id = ""
        best_len = 0
        for r in rows:
            rp = str(r["repo_path"]).strip().lower().replace("/", "\\").rstrip("\\")
            if rp and (norm_path == rp or norm_path.startswith(rp + "\\")) and len(rp) > best_len:
                best_id = r["id"]
                best_len = len(rp)
        if best_id:
            return best_id

    return raw


def get_project_lineage(project_id: str) -> Optional[Dict[str, str]]:
    """Devuelve Dimensión, Área y datos del Proyecto desde cortex.db."""
    _ensure_synced()
    canon = resolve_project(project_id)
    with _conn() as c:
        row = c.execute(
            """
            SELECT p.id AS project_id, p.name AS project_name, p.repo_path, p.status,
                   a.id AS area_id, a.name AS area_name,
                   d.id AS dimension_id, d.name AS dimension_name
            FROM projects p
            JOIN areas a ON a.id = p.area_id
            JOIN dimensions d ON d.id = a.dimension_id
            WHERE p.id = ?
            """,
            (canon,),
        ).fetchone()
        return dict(row) if row else None


def list_watched_repos() -> List[Dict[str, str]]:
    """Lista proyectos con repo_path existente en disco para el observer daemon."""
    _ensure_synced()
    with _conn() as c:
        rows = c.execute("SELECT id, name, repo_path, status FROM projects WHERE repo_path != '' ORDER BY id").fetchall()
        out = []
        for r in rows:
            rp = Path(r["repo_path"])
            if rp.exists():
                out.append(dict(r))
        return out


# ---------------------------------------------------------------------------
# Nivel 4: Actividades tipo Beads (ready / in_progress / blocked / done)
# ---------------------------------------------------------------------------

def ready_activities(project_id: str = "", limit: int = 15) -> List[Dict[str, Any]]:
    _ensure_synced()
    canon = resolve_project(project_id) if project_id else ""
    with _conn() as c:
        sql = """
            SELECT a.*
            FROM activities a
            LEFT JOIN activities b ON a.blocked_by = b.id
            WHERE a.status = 'ready'
              AND (a.blocked_by = '' OR b.id IS NULL OR b.status = 'done')
        """
        params: List[Any] = []
        if canon and canon != "General":
            sql += " AND a.project_id = ?"
            params.append(canon)
        sql += " ORDER BY a.priority ASC, a.updated_at DESC LIMIT ?"
        params.append(limit)
        return [dict(r) for r in c.execute(sql, params).fetchall()]


def manage_activity(action: str, project: str = "", title: str = "", activity_id: str = "",
                    status: str = "", blocked_by: str = "", priority: int = 2,
                    source: str = "manual") -> Dict[str, Any]:
    _ensure_synced()
    act = (action or "list").strip().lower()
    canon_proj = resolve_project(project) if project else "General"
    now = _now_iso()

    with _conn() as c:
        if act == "create":
            clean_title = (title or "").strip()
            if not clean_title:
                return {"ok": False, "error": "Se requiere 'title' para crear actividad."}
            aid = (activity_id or "").strip() or _short_id("act", f"{canon_proj}:{clean_title.lower()}")
            st = (status or ("blocked" if blocked_by else "ready")).strip().lower()
            if st not in ("ready", "in_progress", "blocked", "done"):
                st = "ready"
            c.execute(
                """
                INSERT INTO activities(id, project_id, title, status, blocked_by, priority, source, created_at, updated_at)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    status=CASE WHEN activities.status='done' AND excluded.status!='done' THEN excluded.status ELSE excluded.status END,
                    blocked_by=CASE WHEN excluded.blocked_by!='' THEN excluded.blocked_by ELSE activities.blocked_by END,
                    priority=excluded.priority,
                    updated_at=excluded.updated_at
                """,
                (aid, canon_proj, clean_title[:200], st, blocked_by.strip(), int(priority), source, now, now),
            )
            row = c.execute("SELECT * FROM activities WHERE id = ?", (aid,)).fetchone()
            return {"ok": True, "action": "create", "activity": dict(row)}

        if act in ("start", "in_progress", "block", "done", "ready", "update"):
            target_id = (activity_id or "").strip()
            if not target_id and title:
                row = c.execute(
                    "SELECT id FROM activities WHERE project_id = ? AND LOWER(title) LIKE ? ORDER BY updated_at DESC LIMIT 1",
                    (canon_proj, f"%{title.strip().lower()[:60]}%"),
                ).fetchone()
                if row:
                    target_id = row["id"]
            if not target_id:
                return {"ok": False, "error": "No se encontró 'activity_id' ni actividad coincidente."}

            new_st = {
                "start": "in_progress",
                "in_progress": "in_progress",
                "block": "blocked",
                "done": "done",
                "ready": "ready",
            }.get(act, status or "in_progress")

            if blocked_by and act == "block":
                c.execute(
                    "UPDATE activities SET status = ?, blocked_by = ?, updated_at = ? WHERE id = ?",
                    (new_st, blocked_by.strip(), now, target_id),
                )
            else:
                c.execute(
                    "UPDATE activities SET status = ?, updated_at = ? WHERE id = ?",
                    (new_st, now, target_id),
                )
            # Desbloquear dependientes cuando se completa
            if new_st == "done":
                c.execute(
                    "UPDATE activities SET status = 'ready', updated_at = ? WHERE blocked_by = ? AND status = 'blocked'",
                    (now, target_id),
                )
            row = c.execute("SELECT * FROM activities WHERE id = ?", (target_id,)).fetchone()
            if not row:
                return {"ok": False, "error": f"Actividad '{target_id}' no encontrada."}
            return {"ok": True, "action": act, "activity": dict(row)}

        if act == "ready":
            items = ready_activities(project_id=canon_proj if project else "", limit=25)
            return {"ok": True, "action": "ready", "activities": items}

        # list por defecto
        sql = "SELECT * FROM activities WHERE 1=1"
        params: List[Any] = []
        if project:
            sql += " AND project_id = ?"
            params.append(canon_proj)
        if status:
            sql += " AND status = ?"
            params.append(status.strip().lower())
        sql += " ORDER BY CASE status WHEN 'in_progress' THEN 0 WHEN 'ready' THEN 1 WHEN 'blocked' THEN 2 ELSE 3 END, priority ASC, updated_at DESC LIMIT 30"
        rows = [dict(r) for r in c.execute(sql, params).fetchall()]
        return {"ok": True, "action": "list", "activities": rows}


# ---------------------------------------------------------------------------
# Instintos tipo ECC (Confidence Score + Project-Scoping + Auto-Promoción)
# ---------------------------------------------------------------------------

def record_instinct(scope_id: str, trigger: str, pattern: str, scope_type: str = "project",
                    delta: float = 0.15) -> Dict[str, Any]:
    _ensure_synced()
    stype = (scope_type or "project").strip().lower()
    if stype not in ("project", "area", "dimension", "global"):
        stype = "project"
    sid = resolve_project(scope_id) if stype == "project" else (scope_id or "global").strip()
    trig = (trigger or "").strip()
    pat = (pattern or "").strip()
    if not trig or not pat:
        return {"ok": False, "error": "Se requieren 'trigger' y 'pattern'."}

    iid = _short_id("inst", f"{stype}:{sid.lower()}:{trig.lower()}")
    now = _now_iso()
    promoted_area = ""

    with _conn() as c:
        existing = c.execute("SELECT * FROM instincts WHERE id = ?", (iid,)).fetchone()
        if existing:
            new_conf = round(min(0.95, float(existing["confidence"]) + delta), 2)
            new_cnt = int(existing["confirmations"]) + 1
            c.execute(
                "UPDATE instincts SET pattern = ?, confidence = ?, confirmations = ?, updated_at = ? WHERE id = ?",
                (pat, new_conf, new_cnt, now, iid),
            )
        else:
            c.execute(
                """
                INSERT INTO instincts(id, scope_type, scope_id, trigger, pattern, confidence, confirmations, promoted_to, created_at, updated_at)
                VALUES(?, ?, ?, ?, ?, ?, 1, '', ?, ?)
                """,
                (iid, stype, sid, trig, pat, 0.40, now, now),
            )

        row = dict(c.execute("SELECT * FROM instincts WHERE id = ?", (iid,)).fetchone())
        # Auto-promoción de Proyecto -> Área si supera umbral de confianza y repeticiones
        if stype == "project" and float(row["confidence"]) >= 0.80 and int(row["confirmations"]) >= 3 and not row["promoted_to"]:
            lineage = get_project_lineage(sid)
            if lineage and lineage.get("area_id"):
                aid = lineage["area_id"]
                area_iid = _short_id("inst", f"area:{aid.lower()}:{trig.lower()}")
                c.execute(
                    """
                    INSERT INTO instincts(id, scope_type, scope_id, trigger, pattern, confidence, confirmations, promoted_to, created_at, updated_at)
                    VALUES(?, 'area', ?, ?, ?, ?, ?, '', ?, ?)
                    ON CONFLICT(id) DO UPDATE SET pattern=excluded.pattern, confidence=excluded.confidence,
                        confirmations=instincts.confirmations + 1, updated_at=excluded.updated_at
                    """,
                    (area_iid, aid, trig, pat, row["confidence"], row["confirmations"], now, now),
                )
                c.execute("UPDATE instincts SET promoted_to = ? WHERE id = ?", (aid, iid))
                row["promoted_to"] = aid
                promoted_area = aid

    return {"ok": True, "instinct": row, "promoted_to": promoted_area}


def get_instincts(project_id: str = "", min_confidence: float = 0.35, limit: int = 8) -> List[Dict[str, Any]]:
    _ensure_synced()
    canon = resolve_project(project_id) if project_id else ""
    lineage = get_project_lineage(canon) if canon and canon != "General" else None

    clauses = ["(scope_type = 'global')"]
    params: List[Any] = []
    if canon and canon != "General":
        clauses.append("(scope_type = 'project' AND scope_id = ?)")
        params.append(canon)
    if lineage:
        clauses.append("(scope_type = 'area' AND scope_id = ?)")
        params.append(lineage["area_id"])
        clauses.append("(scope_type = 'dimension' AND scope_id = ?)")
        params.append(lineage["dimension_id"])

    sql = (
        f"SELECT * FROM instincts WHERE ({' OR '.join(clauses)}) "
        f"AND confidence >= ? ORDER BY confidence DESC, confirmations DESC LIMIT ?"
    )
    params.extend([float(min_confidence), int(limit)])
    with _conn() as c:
        return [dict(r) for r in c.execute(sql, params).fetchall()]


# ---------------------------------------------------------------------------
# Navegación Jerárquica 4-Niveles + Session Briefing + Portada Viva
# ---------------------------------------------------------------------------

def get_tree_markdown(dimension_id: str = "", area_id: str = "", project_id: str = "",
                      include_done: bool = False) -> str:
    _ensure_synced()
    canon_proj = resolve_project(project_id) if project_id else ""
    with _conn() as c:
        dims = c.execute("SELECT * FROM dimensions ORDER BY sort_order ASC, id ASC").fetchall()
        areas = c.execute("SELECT * FROM areas ORDER BY id ASC").fetchall()
        projs = c.execute("SELECT * FROM projects ORDER BY status ASC, id ASC").fetchall()
        act_sql = "SELECT * FROM activities" + ("" if include_done else " WHERE status != 'done'") + " ORDER BY priority ASC, updated_at DESC"
        acts = c.execute(act_sql).fetchall()

    acts_by_proj: Dict[str, List[sqlite3.Row]] = {}
    for ac in acts:
        acts_by_proj.setdefault(ac["project_id"], []).append(ac)

    projs_by_area: Dict[str, List[sqlite3.Row]] = {}
    for p in projs:
        if canon_proj and p["id"] != canon_proj:
            continue
        projs_by_area.setdefault(p["area_id"], []).append(p)

    areas_by_dim: Dict[str, List[sqlite3.Row]] = {}
    for a in areas:
        if area_id and a["id"].lower() != area_id.lower():
            continue
        if canon_proj and not projs_by_area.get(a["id"]):
            continue
        areas_by_dim.setdefault(a["dimension_id"], []).append(a)

    lines = ["### 🏛️ Ontología de 4 Niveles (Dimensiones → Áreas → Proyectos → Actividades)"]
    for d in dims:
        if dimension_id and d["id"].lower() != dimension_id.lower():
            continue
        d_areas = areas_by_dim.get(d["id"], [])
        if (area_id or canon_proj) and not d_areas:
            continue
        lines.append(f"\n- **{d['id']} — {d['name']}**")
        for a in d_areas:
            lines.append(f"  - 📂 **{a['name']}** (`{a['id']}`)")
            for p in projs_by_area.get(a["id"], []):
                p_acts = acts_by_proj.get(p["id"], [])
                lines.append(f"    - 📦 **[[{p['id']}]]** [`{p['status']}`] ({len(p_acts)} activas)")
                for ac in p_acts[:5]:
                    blk = f" *(bloqueada por `{ac['blocked_by']}`)*" if ac["blocked_by"] else ""
                    lines.append(f"      - `{ac['id']}` [{ac['status']}] {ac['title']}{blk}")

    return "\n".join(lines)


def save_session_state(conversation_id: str, project_id: str, summary: str,
                       open_activities: Optional[List[str]] = None) -> None:
    if not conversation_id:
        return
    canon = resolve_project(project_id) if project_id else "General"
    with _conn() as c:
        c.execute(
            """
            INSERT INTO session_states(conversation_id, project_id, summary, open_activities_json, updated_at)
            VALUES(?, ?, ?, ?, ?)
            ON CONFLICT(conversation_id) DO UPDATE SET
                project_id=excluded.project_id,
                summary=excluded.summary,
                open_activities_json=excluded.open_activities_json,
                updated_at=excluded.updated_at
            """,
            (conversation_id, canon, (summary or "")[:600], json.dumps(open_activities or [], ensure_ascii=False), _now_iso()),
        )


def build_session_briefing(workspace_paths: Optional[List[str]] = None, cwd: str = "") -> str:
    """Briefing compacto L1 (<400 tokens, <15ms) para SessionStart de Antigravity."""
    _ensure_synced()
    candidates = [str(p) for p in (workspace_paths or []) if p]
    if cwd:
        candidates.append(str(cwd))

    detected_proj = "General"
    for cand in candidates:
        res = resolve_project(cand)
        if res != cand and res != "General":
            detected_proj = res
            break

    lineage = get_project_lineage(detected_proj) if detected_proj != "General" else None
    acts = ready_activities(detected_proj if detected_proj != "General" else "", limit=4)
    with _conn() as c:
        in_prog = c.execute(
            "SELECT * FROM activities WHERE status = 'in_progress'" +
            (" AND project_id = ?" if detected_proj != "General" else "") +
            " ORDER BY updated_at DESC LIMIT 3",
            ([detected_proj] if detected_proj != "General" else []),
        ).fetchall()
        last_sess = c.execute(
            "SELECT * FROM session_states" +
            (" WHERE project_id = ?" if detected_proj != "General" else "") +
            " ORDER BY updated_at DESC LIMIT 1",
            ([detected_proj] if detected_proj != "General" else []),
        ).fetchone()

    instincts = get_instincts(detected_proj, min_confidence=0.40, limit=3)
    open_decs = open_decisions(project=detected_proj if detected_proj != "General" else "")

    lines = ["[DevBrain L1 · Memoria Activa]"]
    if lineage:
        lines.append(f"- Contexto ontológico: `{lineage['dimension_name']}` > `{lineage['area_name']}` > **[[{lineage['project_id']}]]** (`{lineage['status']}`)")
    else:
        lines.append(f"- Proyecto activo: `{detected_proj}` (usa `brain_context` / `brain_tree` para explorar Dimensiones y Áreas)")

    if in_prog or acts:
        act_str = ", ".join(f"`{r['id']}` [{r['status']}] {r['title'][:55]}" for r in (list(in_prog) + acts)[:4])
        lines.append(f"- Actividades vigentes: {act_str}")

    if open_decs:
        lines.append("- Decisiones D-ODD abiertas: " + ", ".join(f"`{d['id']}` ({d['status']})" for d in open_decs[:2]))

    if instincts:
        inst_str = " | ".join(f"{i['trigger']} -> {i['pattern'][:75]} ({i['confidence']:.2f})" for i in instincts)
        lines.append(f"- Instintos vigentes: {inst_str}")

    if last_sess and last_sess["summary"]:
        lines.append(f"- Última sesión ({last_sess['project_id']}): {last_sess['summary'][:160]}")

    lines.append("- Directiva: Ante decisiones de diseño/arquitectura o UI nueva, invoca `assess_decision` (D-ODD). Usa `brain_context` antes de investigar a ciegas.")
    return "\n".join(lines)


def _fts_metrics(fts_db_path: Optional[Path] = None) -> Dict[str, int]:
    candidates = [fts_db_path, devbrain_home() / "cortex_fts.db"]
    for p in candidates:
        if p and Path(p).exists():
            try:
                con = sqlite3.connect(str(p), timeout=2.0)
                k = con.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
                m = con.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
                s = con.execute("SELECT COUNT(*) FROM synapses").fetchone()[0]
                con.close()
                return {"knowledge": int(k), "memories": int(m), "synapses": int(s)}
            except Exception:
                pass
    return {"knowledge": 0, "memories": 0, "synapses": 0}


def render_live_portada(vault_dir: Optional[Path] = None, fts_db_path: Optional[Path] = None) -> Dict[str, Any]:
    """Genera el bloque materializado de Portada.md en <25ms desde SQLite y escribe atómicamente."""
    _ensure_synced()
    vdir = _resolve_vault_dir(vault_dir)
    portada_path = vdir / "Portada.md"
    today = datetime.now().strftime("%Y-%m-%d")
    now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    with _conn() as c:
        dims = c.execute("SELECT * FROM dimensions ORDER BY sort_order ASC, id ASC").fetchall()
        areas = c.execute("SELECT * FROM areas ORDER BY id ASC").fetchall()
        projs = c.execute("SELECT * FROM projects ORDER BY status ASC, id ASC").fetchall()
        acts = c.execute("SELECT * FROM activities ORDER BY priority ASC, updated_at DESC").fetchall()
        promoted = c.execute(
            "SELECT * FROM instincts WHERE scope_type IN ('area', 'dimension', 'global') OR promoted_to != '' ORDER BY confidence DESC LIMIT 6"
        ).fetchall()

    fts = _fts_metrics(fts_db_path)
    led = ledger_stats()
    open_decs = open_decisions()

    acts_by_proj: Dict[str, List[sqlite3.Row]] = {}
    ready_cnt = in_prog_cnt = done_cnt = 0
    for ac in acts:
        acts_by_proj.setdefault(ac["project_id"], []).append(ac)
        if ac["status"] == "ready":
            ready_cnt += 1
        elif ac["status"] == "in_progress":
            in_prog_cnt += 1
        elif ac["status"] == "done":
            done_cnt += 1

    active_projs = [p for p in projs if p["status"] == "active"]
    area_map = {a["id"]: a["name"] for a in areas}

    block_lines = [
        AUTO_START,
        f"> [!NOTE]\n> **Portada Viva Materializada** · Actualizada automáticamente: `{now_iso}` · "
        f"Cortex: `{fts['knowledge']}` notas, `{fts['memories']}` memorias, `{fts['synapses']}` sinapsis · "
        f"Actividades: `{in_prog_cnt}` en curso / `{ready_cnt}` listas / `{done_cnt}` cerradas · "
        f"D-ODD: `{led['decisions_total']}` decisiones.",
        "",
        "## 🎯 1. Horizonte Activo (Generado desde `cortex.db`)",
        "",
        "| Proyecto | Área | Estado | Actividades Clave |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for p in active_projs[:8]:
        p_acts = [a for a in acts_by_proj.get(p["id"], []) if a["status"] != "done"]
        if p_acts:
            act_txt = f"{p_acts[0]['title'][:55]} (+{len(p_acts)-1})" if len(p_acts) > 1 else p_acts[0]["title"][:65]
        else:
            act_txt = "Sin actividades pendientes"
        block_lines.append(f"| **[[{p['id']}]]** | {area_map.get(p['area_id'], p['area_id'])} | `{p['status']}` | {act_txt} |")

    block_lines.extend(["", "## 🏛️ 2. Ontología Viva (Dimensiones → Áreas → Proyectos → Actividades)", ""])
    projs_by_area: Dict[str, List[sqlite3.Row]] = {}
    for p in projs:
        projs_by_area.setdefault(p["area_id"], []).append(p)
    areas_by_dim: Dict[str, List[sqlite3.Row]] = {}
    for a in areas:
        areas_by_dim.setdefault(a["dimension_id"], []).append(a)

    for d in dims:
        block_lines.append(f"- **{d['id']}: {d['name']}**")
        for a in areas_by_dim.get(d["id"], []):
            block_lines.append(f"  - **{a['name']}** (`{a['id']}`)")
            for p in projs_by_area.get(a["id"], []):
                open_p = [ac for ac in acts_by_proj.get(p["id"], []) if ac["status"] != "done"]
                sample = f" — próximo: *{open_p[0]['title'][:45]}*" if open_p else ""
                block_lines.append(f"    - [[{p['id']}]] (`{p['status']}`, {len(open_p)} pendientes){sample}")

    if open_decs or promoted:
        block_lines.extend(["", "## ⚡ 3. Decisiones Abiertas & Instintos Consolidados (ECC)", ""])
        for dec in open_decs[:4]:
            block_lines.append(f"- 🌀 D-ODD `{dec['id']}` [{dec['status']}] **[[{dec['project']}]]**: {dec['objective'][:90]}")
        for inst in promoted[:4]:
            block_lines.append(f"- 🧩 Instinto (`{inst['scope_type']}:{inst['scope_id']}`, `{inst['confidence']:.2f}`): **{inst['trigger']}** → {inst['pattern'][:90]}")

    block_lines.append(AUTO_END)
    auto_block = "\n".join(block_lines)

    written = False
    try:
        vdir.mkdir(parents=True, exist_ok=True)
        if portada_path.exists():
            cur_text = portada_path.read_text(encoding="utf-8", errors="replace")
            cur_text = re.sub(
                r'ultima_actualizacion:\s*["\']?[\d\-]+["\']?',
                f'ultima_actualizacion: "{today}"',
                cur_text,
            )
            cur_text = re.sub(r'version:\s*["\']?[\d\.]+["\']?', 'version: "4.0"', cur_text)
            if AUTO_START in cur_text and AUTO_END in cur_text:
                new_text = re.sub(
                    re.escape(AUTO_START) + r"[\s\S]*?" + re.escape(AUTO_END),
                    lambda _: auto_block,
                    cur_text,
                    count=1,
                )
            else:
                # Preservar el bloque manual existente debajo (ej. Malla Transversal y Snapshots)
                marker = "## 🌐 3. Malla Transversal"
                idx = cur_text.find(marker)
                tail = ("\n\n---\n\n" + cur_text[idx:]) if idx != -1 else ""
                header = (
                    f"---\ntags: [portada, hud, editor-en-jefe, devbrain-executive, dashboard]\n"
                    f'version: "4.0"\nultima_actualizacion: "{today}"\nmodo: "activo"\n---\n\n'
                    f"# 📰 PORTADA — Cuadro de Mando Ejecutivo (DevBrain HUD)\n\n"
                )
                new_text = header + auto_block + tail
        else:
            new_text = (
                f"---\ntags: [portada, hud, editor-en-jefe, devbrain-executive, dashboard]\n"
                f'version: "4.0"\nultima_actualizacion: "{today}"\nmodo: "activo"\n---\n\n'
                f"# 📰 PORTADA — Cuadro de Mando Ejecutivo (DevBrain HUD)\n\n" + auto_block + "\n"
            )

        tmp_path = portada_path.with_suffix(".md.tmp")
        tmp_path.write_text(new_text, encoding="utf-8")
        os.replace(tmp_path, portada_path)
        written = True
    except Exception:
        written = False

    return {
        "updated": written,
        "portada_path": str(portada_path),
        "dimensions": len(dims),
        "areas": len(areas),
        "projects": len(projs),
        "activities_open": ready_cnt + in_prog_cnt,
        "markdown": auto_block,
    }
