"""
decision_ledger.py: Ledger persistente de decisiones D-ODD + eventos del gate.

Compartido entre el servidor MCP y los hooks de ciclo de vida (procesos distintos),
por eso vive en una ruta estable: ~/.devbrain/decisions.db (override: DEVBRAIN_HOME).
Solo depende de la stdlib para que los hooks arranquen rápido.
"""

from __future__ import annotations

import json
import os
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

OPEN_STATUSES = ("exploring", "committed")


def devbrain_home() -> Path:
    base = os.environ.get("DEVBRAIN_HOME")
    home = Path(base) if base else Path(os.path.expanduser("~")) / ".devbrain"
    home.mkdir(parents=True, exist_ok=True)
    return home


def _open(db_path: Optional[Path] = None) -> sqlite3.Connection:
    path = db_path or (devbrain_home() / "decisions.db")
    conn = sqlite3.connect(str(path), timeout=5.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS decisions (
            id TEXT PRIMARY KEY,
            conversation_id TEXT,
            project TEXT,
            objective TEXT,
            dimensions TEXT,
            domain TEXT,
            status TEXT,
            chosen TEXT,
            synthesis TEXT,
            outcome TEXT,
            outcome_notes TEXT,
            evidence TEXT DEFAULT '[]',
            close_requested INTEGER DEFAULT 0,
            created_at REAL,
            updated_at REAL
        );
        CREATE INDEX IF NOT EXISTS idx_dec_conv ON decisions(conversation_id, status);
        CREATE TABLE IF NOT EXISTS gate_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT,
            input_hash TEXT,
            score REAL,
            threshold REAL,
            fired INTEGER,
            verdict TEXT,
            created_at REAL
        );
        CREATE INDEX IF NOT EXISTS idx_gate_conv ON gate_events(conversation_id, id);
        """
    )
    return conn


class _connect:
    """Context manager: commit al salir y cierre explícito (evita locks de archivo en Windows)."""

    def __enter__(self) -> sqlite3.Connection:
        self.conn = _open()
        return self.conn

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
        finally:
            self.conn.close()


# ---------------- Gate events ----------------

def last_gate_hash(conversation_id: str) -> Optional[str]:
    with _connect() as c:
        row = c.execute(
            "SELECT input_hash FROM gate_events WHERE conversation_id=? ORDER BY id DESC LIMIT 1",
            (conversation_id,),
        ).fetchone()
    return row["input_hash"] if row else None


def record_gate_event(conversation_id: str, input_hash: str, score: float, threshold: float, fired: bool) -> int:
    with _connect() as c:
        cur = c.execute(
            "INSERT INTO gate_events(conversation_id,input_hash,score,threshold,fired,verdict,created_at) VALUES(?,?,?,?,?,?,?)",
            (conversation_id, input_hash, score, threshold, int(fired), None, time.time()),
        )
        return int(cur.lastrowid)


def label_last_gate_event(conversation_id: str, verdict: str) -> bool:
    """Etiqueta el último evento del gate de la conversación con el veredicto del LLM."""
    if not conversation_id:
        return False
    with _connect() as c:
        row = c.execute(
            "SELECT id FROM gate_events WHERE conversation_id=? ORDER BY id DESC LIMIT 1",
            (conversation_id,),
        ).fetchone()
        if not row:
            return False
        c.execute("UPDATE gate_events SET verdict=? WHERE id=?", (verdict, row["id"]))
    return True


def labeled_gate_events(limit: int = 200) -> List[Dict[str, Any]]:
    with _connect() as c:
        rows = c.execute(
            "SELECT score, fired, verdict FROM gate_events WHERE verdict IS NOT NULL ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


# ---------------- Decisions ----------------

def open_decision(objective: str, project: str, dimensions: Dict[str, int], domain: str,
                  conversation_id: str = "") -> str:
    dec_id = "dec-" + uuid.uuid4().hex[:10]
    now = time.time()
    with _connect() as c:
        c.execute(
            "INSERT INTO decisions(id,conversation_id,project,objective,dimensions,domain,status,created_at,updated_at)"
            " VALUES(?,?,?,?,?,?,?,?,?)",
            (dec_id, conversation_id or "", project, objective, json.dumps(dimensions), domain, "exploring", now, now),
        )
    return dec_id


def get_decision(dec_id: str) -> Optional[Dict[str, Any]]:
    with _connect() as c:
        row = c.execute("SELECT * FROM decisions WHERE id=?", (dec_id,)).fetchone()
    if not row:
        return None
    d = dict(row)
    d["dimensions"] = json.loads(d.get("dimensions") or "{}")
    d["evidence"] = json.loads(d.get("evidence") or "[]")
    return d


def commit_decision(dec_id: str, chosen: str, synthesis: str) -> bool:
    with _connect() as c:
        cur = c.execute(
            "UPDATE decisions SET status='committed', chosen=?, synthesis=?, updated_at=? WHERE id=? AND status IN ('exploring','committed')",
            (chosen, synthesis, time.time(), dec_id),
        )
        return cur.rowcount > 0


def close_decision(dec_id: str, outcome: str, notes: str = "") -> bool:
    with _connect() as c:
        cur = c.execute(
            "UPDATE decisions SET status='closed', outcome=?, outcome_notes=?, updated_at=? WHERE id=?",
            (outcome, notes, time.time(), dec_id),
        )
        return cur.rowcount > 0


def attach_evidence(conversation_id: str, item: Dict[str, Any]) -> int:
    """Adjunta evidencia a todas las decisiones abiertas de la conversación. Retorna cuántas."""
    if not conversation_id:
        return 0
    item = dict(item)
    item.setdefault("ts", time.time())
    count = 0
    with _connect() as c:
        rows = c.execute(
            "SELECT id, evidence FROM decisions WHERE conversation_id=? AND status IN ('exploring','committed')",
            (conversation_id,),
        ).fetchall()
        for r in rows:
            ev = json.loads(r["evidence"] or "[]")
            ev.append(item)
            ev = ev[-20:]
            c.execute("UPDATE decisions SET evidence=?, updated_at=? WHERE id=?", (json.dumps(ev), time.time(), r["id"]))
            count += 1
    return count


def open_decisions(conversation_id: Optional[str] = None, project: Optional[str] = None) -> List[Dict[str, Any]]:
    q = "SELECT * FROM decisions WHERE status IN ('exploring','committed')"
    params: list = []
    if conversation_id is not None:
        q += " AND conversation_id=?"
        params.append(conversation_id)
    if project:
        q += " AND project=?"
        params.append(project)
    q += " ORDER BY created_at DESC LIMIT 20"
    with _connect() as c:
        rows = c.execute(q, params).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["evidence"] = json.loads(d.get("evidence") or "[]")
        out.append(d)
    return out


def decisions_needing_close(conversation_id: str) -> List[Dict[str, Any]]:
    """Decisiones comprometidas, con evidencia y aún sin solicitud de cierre."""
    return [
        d for d in open_decisions(conversation_id)
        if d["status"] == "committed" and d["evidence"] and not d["close_requested"]
    ]


def mark_close_requested(dec_id: str) -> None:
    with _connect() as c:
        c.execute("UPDATE decisions SET close_requested=1 WHERE id=?", (dec_id,))


def stats() -> Dict[str, Any]:
    with _connect() as c:
        total = c.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
        by_status = {r[0]: r[1] for r in c.execute("SELECT status, COUNT(*) FROM decisions GROUP BY status")}
        by_choice = {r[0]: r[1] for r in c.execute(
            "SELECT chosen, COUNT(*) FROM decisions WHERE chosen IS NOT NULL GROUP BY chosen")}
        by_outcome = {r[0]: r[1] for r in c.execute(
            "SELECT outcome, COUNT(*) FROM decisions WHERE outcome IS NOT NULL GROUP BY outcome")}
        with_ev = c.execute("SELECT COUNT(*) FROM decisions WHERE evidence != '[]'").fetchone()[0]
        gate_total = c.execute("SELECT COUNT(*) FROM gate_events").fetchone()[0]
        gate_fired = c.execute("SELECT COUNT(*) FROM gate_events WHERE fired=1").fetchone()[0]
    return {
        "decisions_total": total,
        "by_status": by_status,
        "by_choice": by_choice,
        "by_outcome": by_outcome,
        "with_evidence": with_ev,
        "gate_events": gate_total,
        "gate_fired": gate_fired,
    }
