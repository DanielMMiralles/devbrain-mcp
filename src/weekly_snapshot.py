"""
DevBrain Weekly Snapshot Engine v2.0
Automatiza la captura de estado semanal (Foto de los Viernes),
leyendo métricas desde SQLite (cortex_fts.db / cortex.db) para cero bloqueos sobre OneDrive,
actualizando atómicamente Portada.md mediante ontology_engine y archivando el snapshot.
"""
from __future__ import annotations
import re
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


class WeeklySnapshotEngine:
    def __init__(self, vault_dir: Path):
        self.vault_dir = vault_dir
        self.portada_path = vault_dir / "Portada.md"
        self.snapshots_dir = vault_dir / "04-APRENDIZAJES" / "snapshots"
        self.proyectos_dir = vault_dir / "02-PROYECTOS"
        self.aprendizajes_dir = vault_dir / "04-APRENDIZAJES"

    def capture_snapshot(self, custom_verdict: str = "", force: bool = False) -> dict:
        """Ejecuta la captura del snapshot semanal usando métricas en SQLite (<25ms) y actualiza Portada.md."""
        now = datetime.now()
        year, week_num, _ = now.isocalendar()
        snapshot_id = f"{year}-W{week_num:02d}"
        iso_timestamp = now.strftime("%Y-%m-%dT%H:%M:%S")
        date_str = now.strftime("%Y-%m-%d")
        cutoff_ts = (now - timedelta(days=7)).timestamp()
        cutoff_date = (now - timedelta(days=7)).strftime("%Y-%m-%d")

        # 1. Decisiones y aprendizajes recientes (solo carpeta acotada, nunca Vault completo)
        decisions_week = []
        for sub in ("decisiones", "errores"):
            dpath = self.aprendizajes_dir / sub
            if dpath.exists():
                for f in dpath.glob("*.md"):
                    try:
                        if f.stat().st_mtime >= cutoff_ts:
                            decisions_week.append(f"[[{f.stem}]]")
                    except Exception:
                        pass

        # 2. Tareas ODD / Actividades desde SQLite (y odd/tasks local si existe)
        odd_tasks_completed = 0
        odd_tasks_in_progress = 0
        odd_features = []

        try:
            from ontology_engine import manage_activity
            acts_done = manage_activity("list", status="done").get("activities", [])
            acts_open = [
                a for a in manage_activity("list").get("activities", [])
                if a.get("status") != "done"
            ]
            odd_tasks_completed += len(acts_done)
            odd_tasks_in_progress += len(acts_open)
            for ac in acts_open[:8]:
                odd_features.append(f"`{ac['id']}` [{ac['status']}] {ac['title']} ({ac['project_id']})")
        except Exception:
            pass

        for odd_dir in (Path.cwd() / "odd" / "tasks", self.vault_dir / "odd" / "tasks"):
            if odd_dir.exists():
                for task_file in odd_dir.glob("*.md"):
                    try:
                        content = task_file.read_text(encoding="utf-8", errors="ignore")
                        done_count = len(re.findall(r"-\s*\[x\]", content, re.IGNORECASE))
                        pending_count = len(re.findall(r"-\s*\[\s\]", content))
                        odd_tasks_completed += done_count
                        odd_tasks_in_progress += pending_count
                        if done_count > 0 or pending_count > 0:
                            odd_features.append(f"`{task_file.stem}` ({done_count} completadas / {pending_count} pendientes)")
                    except Exception:
                        pass

        # 3. Métricas del Cortex desde SQLite (cero rglob sobre OneDrive)
        total_notes = 0
        notes_updated_week = 0
        try:
            from decision_ledger import devbrain_home
            candidates = [devbrain_home() / "cortex_fts.db", self.vault_dir / "06-SISTEMA" / "cache" / "devbrain_fts.db"]
        except Exception:
            candidates = [self.vault_dir / "06-SISTEMA" / "cache" / "devbrain_fts.db"]

        for dbp in candidates:
            if dbp.exists():
                try:
                    con = sqlite3.connect(str(dbp), timeout=2.0)
                    total_notes = int(con.execute("SELECT COUNT(*) FROM files_meta").fetchone()[0])
                    notes_updated_week = int(
                        con.execute("SELECT COUNT(*) FROM memories WHERE updated_at >= ?", (cutoff_date,)).fetchone()[0]
                    ) + int(
                        con.execute("SELECT COUNT(*) FROM knowledge WHERE updated_at >= ?", (cutoff_date,)).fetchone()[0]
                    )
                    con.close()
                    break
                except Exception:
                    pass

        # 4. Proyectos Activos
        active_projects = []
        if self.proyectos_dir.exists():
            for p in self.proyectos_dir.iterdir():
                if p.is_dir() and p.name not in ["specs", "_templates", "context-bundles"]:
                    active_projects.append(p.name)

        # 5. Veredicto
        if not custom_verdict:
            verdict_parts = [
                f"Semana {week_num}: {len(decisions_week)} aprendizaje(s)/decisión(es) registradas.",
                f"{odd_tasks_completed} tarea(s)/actividad(es) completadas, {odd_tasks_in_progress} en curso.",
                f"{notes_updated_week} nota(s) actualizadas en SQLite.",
            ]
            custom_verdict = " ".join(verdict_parts)

        # 6. Bloque Markdown
        snapshot_entry = f"""### 📸 Snapshot: `{date_str}` (Semana {week_num})
- **Timestamp**: `{iso_timestamp}`
- **Recibos RDD / Actividades ODD**: {odd_tasks_completed} completada(s), {odd_tasks_in_progress} en curso.
- **Salud del Cortex**: {total_notes} notas indexadas ({notes_updated_week} actualizadas en 7d).
- **Decisiones & Aprendizajes Recientes**:
{chr(10).join(f'  - {d}' for d in decisions_week[:5]) if decisions_week else '  - *Sin decisiones críticas registradas esta semana.*'}
- **Veredicto del Editor en Jefe**:
  > "{custom_verdict}"
"""

        # 7. Archivar Snapshot Inmutable
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        archive_file = self.snapshots_dir / f"snapshot-{snapshot_id}.md"
        archive_content = f"""---
tags: [snapshot, rdd, devbrain, weekly-review]
snapshot_id: "{snapshot_id}"
date: "{date_str}"
week: {week_num}
year: {year}
---

# 📸 Snapshot Semanal de Estado — {snapshot_id}

{snapshot_entry}

## 📋 Detalle de Features & Actividades
{chr(10).join(f'- {f}' for f in odd_features) if odd_features else '- *Sin features activas registradas.*'}

## 🏛️ Proyectos Auditados
{chr(10).join(f'- [[{p}]]' for p in active_projects)}
"""
        archive_file.write_text(archive_content, encoding="utf-8")

        # 8. Materializar Portada Viva primero e insertar bloque Snapshot
        portada_updated = False
        try:
            from ontology_engine import render_live_portada
            render_live_portada(self.vault_dir)
        except Exception:
            pass

        if self.portada_path.exists():
            portada_text = self.portada_path.read_text(encoding="utf-8", errors="ignore")
            portada_text = re.sub(
                r'ultima_actualizacion:\s*["\']?[\d\-]+["\']?',
                f'ultima_actualizacion: "{date_str}"',
                portada_text,
            )
            header_target = "## 📸 5. Registro de Snapshots (Fotos de los Viernes)"
            if header_target in portada_text:
                parts = portada_text.split(header_target, 1)
                pre_section = parts[0] + header_target + "\n\n"
                post_section = parts[1]
                tip_box_match = re.search(r"(>\s*\[!TIP\][\s\S]*?>\s*[^\n]+\n\n)", post_section)
                if tip_box_match:
                    tip_box = tip_box_match.group(1)
                    rest = post_section[tip_box_match.end():]
                    new_post = tip_box + snapshot_entry + "\n" + rest
                else:
                    new_post = "\n" + snapshot_entry + "\n" + post_section
                self.portada_path.write_text(pre_section + new_post, encoding="utf-8")
                portada_updated = True

        return {
            "snapshot_id": snapshot_id,
            "date": date_str,
            "week": week_num,
            "archive_path": str(archive_file),
            "portada_updated": portada_updated,
            "metrics": {
                "total_notes": total_notes,
                "notes_updated_7d": notes_updated_week,
                "odd_completed": odd_tasks_completed,
                "odd_in_progress": odd_tasks_in_progress,
                "decisions_count": len(decisions_week),
            },
            "verdict": custom_verdict,
            "markdown_snippet": snapshot_entry,
        }
