"""
DevBrain Weekly Snapshot Engine v1.0
Automatiza la captura de estado semanal (Foto de los Viernes),
agregando telemetría de RDD, salud del Cortex y actividad de proyectos,
actualizando atómicamente la Portada viva (Portada.md) y archivando el snapshot.
"""
from __future__ import annotations
import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import re

class WeeklySnapshotEngine:
    def __init__(self, vault_dir: Path):
        self.vault_dir = vault_dir
        self.portada_path = vault_dir / "Portada.md"
        self.snapshots_dir = vault_dir / "04-APRENDIZAJES" / "snapshots"
        self.proyectos_dir = vault_dir / "02-PROYECTOS"
        self.aprendizajes_dir = vault_dir / "04-APRENDIZAJES"

    def capture_snapshot(self, custom_verdict: str = "", force: bool = False) -> dict:
        """
        Ejecuta la captura del snapshot semanal y actualiza la Portada.
        """
        now = datetime.now()
        year, week_num, weekday = now.isocalendar()
        snapshot_id = f"{year}-W{week_num:02d}"
        iso_timestamp = now.strftime("%Y-%m-%dT%H:%M:%S")
        date_str = now.strftime("%Y-%m-%d")

        cutoff_7d = now - timedelta(days=7)
        cutoff_ts = cutoff_7d.timestamp()

        # 1. Recolectar Decisiones y Aprendizajes de la semana
        decisions_week = []
        if self.aprendizajes_dir.exists():
            for f in self.aprendizajes_dir.rglob("*.md"):
                try:
                    mtime = f.stat().st_mtime
                    if mtime >= cutoff_ts and "snapshot" not in f.name.lower():
                        clean_name = f.stem
                        decisions_week.append(f"[[{clean_name}]]")
                except Exception:
                    pass

        # 2. Recolectar Tareas ODD / Recibos RDD
        # Buscar en carpetas odd/tasks conocidas
        odd_tasks_completed = 0
        odd_tasks_in_progress = 0
        odd_features = []

        candidate_odd_dirs = [
            Path.cwd() / "odd" / "tasks",
            Path(r"C:\Users\damm1\AppData\Local\Programs\antigravity\odd\tasks"),
            self.vault_dir / "odd" / "tasks"
        ]

        for odd_dir in candidate_odd_dirs:
            if odd_dir.exists():
                for task_file in odd_dir.glob("*.md"):
                    try:
                        content = task_file.read_text(encoding="utf-8", errors="ignore")
                        done_count = len(re.findall(r"-\s*\[x\]", content, re.IGNORECASE))
                        pending_count = len(re.findall(r"-\s*\[\s\]", content))
                        odd_tasks_completed += done_count
                        odd_tasks_in_progress += pending_count
                        
                        feat_name = task_file.stem
                        if done_count > 0 or pending_count > 0:
                            odd_features.append(f"`{feat_name}` ({done_count} completadas / {pending_count} pendientes)")
                    except Exception:
                        pass

        # 3. Métricas del Cortex en Vault
        total_notes = 0
        notes_updated_week = 0
        if self.vault_dir.exists():
            for note in self.vault_dir.rglob("*.md"):
                if ".obsidian" in str(note) or ".trash" in str(note):
                    continue
                total_notes += 1
                try:
                    if note.stat().st_mtime >= cutoff_ts:
                        notes_updated_week += 1
                except Exception:
                    pass

        # 4. Proyectos Activos
        active_projects = []
        if self.proyectos_dir.exists():
            for p in self.proyectos_dir.iterdir():
                if p.is_dir() and p.name not in ["specs", "_templates", "context-bundles"]:
                    active_projects.append(p.name)

        # 5. Formular Veredicto
        if not custom_verdict:
            verdict_parts = [
                f"Semana {week_num}: {len(decisions_week)} aprendizaje(s)/decisión(es) registradas.",
                f"{odd_tasks_completed} tarea(s) ODD verificadas exitosamente.",
                f"{notes_updated_week} nota(s) del Vault actualizadas en los últimos 7 días."
            ]
            if odd_tasks_in_progress > 0:
                verdict_parts.append(f"{odd_tasks_in_progress} tarea(s) en curso listas para el próximo ciclo.")
            custom_verdict = " ".join(verdict_parts)

        # 6. Construir Bloque Markdown del Snapshot
        snapshot_entry = f"""### 📸 Snapshot: `{date_str}` (Semana {week_num})
- **Timestamp**: `{iso_timestamp}`
- **Recibos RDD / Tareas ODD**: {odd_tasks_completed} tarea(s) verificadas, {odd_tasks_in_progress} en progreso.
- **Salud del Cortex**: {total_notes} notas en Vault ({notes_updated_week} tocadas esta semana).
- **Decisiones & Aprendizajes Recientes**:
{chr(10).join(f'  - {d}' for d in decisions_week[:5]) if decisions_week else '  - *Sin decisiones críticas registradas esta semana.*'}
- **Veredicto del Editor en Jefe**:
  > "{custom_verdict}"
"""

        # 7. Guardar Snapshot Inmutable en 04-APRENDIZAJES/snapshots/
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

## 📋 Detalle de Features ODD
{chr(10).join(f'- {f}' for f in odd_features) if odd_features else '- *Sin features activas registradas en odd/tasks/.*'}

## 🏛️ Proyectos Auditados
{chr(10).join(f'- [[{p}]]' for p in active_projects)}
"""
        archive_file.write_text(archive_content, encoding="utf-8")

        # 8. Actualizar Portada.md Atómicamente
        portada_updated = False
        if self.portada_path.exists():
            portada_text = self.portada_path.read_text(encoding="utf-8", errors="ignore")
            
            # Actualizar frontmatter ultima_actualizacion
            portada_text = re.sub(
                r'ultima_actualizacion:\s*["\']?[\d\-]+["\']?',
                f'ultima_actualizacion: "{date_str}"',
                portada_text
            )

            # Insertar en la sección de Snapshots
            header_target = "## 📸 5. Registro de Snapshots (Fotos de los Viernes)"
            if header_target in portada_text:
                parts = portada_text.split(header_target, 1)
                pre_section = parts[0] + header_target + "\n\n"
                post_section = parts[1]
                
                # Reemplazar o anteponer el snapshot nuevo
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
                "decisions_count": len(decisions_week)
            },
            "verdict": custom_verdict,
            "markdown_snippet": snapshot_entry
        }
