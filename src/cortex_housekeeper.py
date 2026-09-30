"""
DevBrain Cortex Housekeeper v1.0 — Motor de Auto-Mantenimiento e Integridad Cognitiva
"Se revisa solo: avisa si algo que sabe quedó viejo, roto o repetido. No duplica ni pierde información."
Funcionalidades:
1. Detección de enlaces rotos (sinapsis huérfanas [[NotaInexistente]]).
2. Detección de notas obsoletas / estancadas (Long-Term Depression LTD).
3. Detección de solapamiento semántico y duplicados en el Vault.
4. Poda sináptica determinista y consolidación en Modo Sueño (Dream Cycle).
"""
from __future__ import annotations

import difflib
import os
import re
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class CortexHousekeeper:
    """Auditor y mantenedor de la integridad de la base de conocimiento y grafo sináptico."""

    def __init__(self, vault_dir: Path, db_path: Path | None = None):
        self.vault_dir = Path(vault_dir).resolve()
        self.db_path = Path(db_path).resolve() if db_path else self.vault_dir / ".devbrain_cache" / "devbrain_fts.db"

    def audit_cortex_health(
        self,
        scan_broken_links: bool = True,
        scan_duplicates: bool = True,
        scan_ltd: bool = True,
        auto_prune: bool = False
    ) -> dict[str, Any]:
        """Audita el estado de salud integral del cerebro."""
        start_time = time.time()
        all_notes = self._discover_all_notes()
        total_notes = len(all_notes)

        broken_links = []
        if scan_broken_links and total_notes > 0:
            broken_links = self._detect_broken_links(all_notes)

        duplicates = []
        if scan_duplicates and total_notes > 0:
            duplicates = self._detect_semantic_duplicates(all_notes)

        stale_notes = []
        if scan_ltd and total_notes > 0:
            stale_notes = self._detect_stale_notes(all_notes)

        synapse_stats = self._audit_synapse_table()

        pruned_count = 0
        if auto_prune and self.db_path.exists():
            pruned_count = self.prune_weak_synapses(min_weight=0.1)

        # Cálculo de Health Score (0 - 100)
        # Deducciones: -2 por enlace roto (max -40), -3 por duplicado (max -30), -1 por nota vieja (max -30)
        penalty = min(40, len(broken_links) * 2) + min(30, len(duplicates) * 3) + min(30, len(stale_notes))
        health_score = max(0, 100 - penalty)

        elapsed_ms = round((time.time() - start_time) * 1000, 1)

        return {
            "health_score": health_score,
            "status": "EXCELENTE" if health_score >= 85 else ("ADVERTENCIA" if health_score >= 60 else "CRÍTICO"),
            "total_notes": total_notes,
            "broken_links_count": len(broken_links),
            "broken_links": broken_links[:15],
            "duplicates_count": len(duplicates),
            "duplicates": duplicates[:10],
            "stale_notes_count": len(stale_notes),
            "stale_notes": stale_notes[:10],
            "synapses_total": synapse_stats.get("total_synapses", 0),
            "weak_synapses": synapse_stats.get("weak_synapses", 0),
            "pruned_synapses": pruned_count,
            "elapsed_ms": elapsed_ms,
            "recommendations": self._generate_recommendations(broken_links, duplicates, stale_notes, health_score)
        }

    def _discover_all_notes(self) -> dict[str, Path]:
        """Mapea todas las notas markdown existentes en el Vault (nombre base sin .md -> Path)."""
        notes = {}
        if not self.vault_dir.exists():
            return notes

        search_dirs = [
            self.vault_dir / "02-PROYECTOS",
            self.vault_dir / "03-CONOCIMIENTO",
            self.vault_dir / "04-APRENDIZAJES"
        ]

        # Si no tiene carpetas estándar, buscar en todo el vault excepto carpetas ocultas
        has_subdirs = any(d.exists() for d in search_dirs)
        target_roots = search_dirs if has_subdirs else [self.vault_dir]

        for root_dir in target_roots:
            if not root_dir.exists():
                continue
            for p in root_dir.rglob("*.md"):
                if any(part.startswith(".") for part in p.parts):
                    continue
                name_clean = p.stem.strip()
                notes[name_clean.lower()] = p

        return notes

    def _detect_broken_links(self, all_notes: dict[str, Path]) -> list[dict[str, Any]]:
        """Busca referencias a notas que no existen en el Vault."""
        broken = []
        note_keys = list(all_notes.keys())

        # Revisar una muestra representativa o todas las notas
        scanned_count = 0
        for name_lower, path in all_notes.items():
            if scanned_count > 300:  # Límite de tiempo/performance
                break
            scanned_count += 1

            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            matches = re.findall(r"\[\[(.*?)\]\]", content)
            for raw_link in matches:
                # Quitar alias [[Target|Alias]] y anchors [[Target#Section]]
                target = raw_link.split("|")[0].split("#")[0].strip()
                if not target or target.startswith("http://") or target.startswith("https://"):
                    continue

                target_lower = target.lower()
                if target_lower not in all_notes:
                    sugg = None
                    if len(broken) < 15:
                        suggestions = difflib.get_close_matches(target_lower, note_keys, n=1, cutoff=0.75)
                        if suggestions and suggestions[0] in all_notes:
                            sugg = all_notes[suggestions[0]].stem

                    broken.append({
                        "source_note": path.stem,
                        "broken_target": target,
                        "suggested_fix": sugg
                    })
                    if len(broken) >= 50:
                        break
            if len(broken) >= 50:
                break

        return broken

    def _detect_semantic_duplicates(self, all_notes: dict[str, Path]) -> list[dict[str, Any]]:
        """Detecta notas con títulos casi idénticos mediante agrupamiento por prefijos y similitud local rápida."""
        duplicates = []
        names = sorted(list(all_notes.keys()))

        # Comparar solo elementos adyacentes en la lista ordenada (O(N))
        for i in range(len(names) - 1):
            n1 = names[i]
            n2 = names[i + 1]
            # Si comparten prefijo significativo
            if n1[:8] == n2[:8] and len(n1) > 8:
                ratio = difflib.SequenceMatcher(None, n1, n2).quick_ratio()
                if 0.85 <= ratio < 1.0:
                    duplicates.append({
                        "note_a": all_notes[n1].name,
                        "note_b": all_notes[n2].name,
                        "similarity": round(ratio * 100, 1)
                    })
                    if len(duplicates) >= 20:
                        break
        return duplicates

    def _detect_stale_notes(self, all_notes: dict[str, Path], days_threshold: int = 90) -> list[dict[str, Any]]:
        """Identifica notas que no se han tocado en más de days_threshold días."""
        stale = []
        now_ts = time.time()
        threshold_seconds = days_threshold * 86400

        for name_lower, path in all_notes.items():
            try:
                mtime = path.stat().st_mtime
                age_days = int((now_ts - mtime) / 86400)
                if age_days >= days_threshold:
                    stale.append({
                        "note": path.name,
                        "age_days": age_days,
                        "path": str(path.relative_to(self.vault_dir))
                    })
            except Exception:
                continue

        stale.sort(key=lambda x: x["age_days"], reverse=True)
        return stale

    def _audit_synapse_table(self) -> dict[str, int]:
        """Consulta estadísticas de la tabla synapses en SQLite."""
        if not self.db_path.exists():
            return {"total_synapses": 0, "weak_synapses": 0}

        try:
            conn = sqlite3.connect(str(self.db_path), timeout=5.0)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='synapses'")
            if c.fetchone()[0] == 0:
                conn.close()
                return {"total_synapses": 0, "weak_synapses": 0}

            c.execute("SELECT COUNT(*) FROM synapses")
            total = c.fetchone()[0]

            c.execute("SELECT COUNT(*) FROM synapses WHERE weight < 0.2")
            weak = c.fetchone()[0]

            conn.close()
            return {"total_synapses": total, "weak_synapses": weak}
        except Exception:
            return {"total_synapses": 0, "weak_synapses": 0}

    def prune_weak_synapses(self, min_weight: float = 0.1) -> int:
        """Elimina sinapsis residuales para mantener ágil el grafo."""
        if not self.db_path.exists():
            return 0
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=5.0)
            c = conn.cursor()
            c.execute("DELETE FROM synapses WHERE weight < ?", (min_weight,))
            pruned = c.rowcount
            conn.commit()
            conn.close()
            return pruned
        except Exception:
            return 0

    def consolidate_dream_cycle(self) -> dict[str, Any]:
        """Ejecuta el ciclo de sueño / consolidación profunda del cerebro."""
        start_time = time.time()
        decayed_count = 0
        optimized_db = False

        if self.db_path.exists():
            try:
                conn = sqlite3.connect(str(self.db_path), timeout=10.0)
                c = conn.cursor()

                # 1. Aplicar LTD (Long-Term Depression) a sinapsis inactivas
                now_iso = datetime.now(timezone.utc).isoformat()
                c.execute("SELECT id, weight, last_fired FROM synapses WHERE last_fired IS NOT NULL")
                rows = c.fetchall()
                for syn_id, w, lf in rows:
                    try:
                        dt = datetime.fromisoformat(lf)
                        days = (datetime.now(timezone.utc) - dt).total_seconds() / 86400
                        if days > 1.0:
                            # Decaimiento suave: w * 2^(-days / 30)
                            new_w = max(0.01, w * (0.5 ** (days / 30.0)))
                            c.execute("UPDATE synapses SET weight = ? WHERE id = ?", (new_w, syn_id))
                            decayed_count += 1
                    except Exception:
                        pass
                conn.commit()

                # 2. Poda residual
                c.execute("DELETE FROM synapses WHERE weight < 0.05")
                pruned_count = c.rowcount
                conn.commit()

                # 3. Optimizar FTS5 y base de datos
                c.execute("PRAGMA optimize")
                try:
                    c.execute("INSERT INTO knowledge_fts(knowledge_fts) VALUES('optimize')")
                except Exception:
                    pass
                conn.commit()
                conn.close()
                optimized_db = True
            except Exception as e:
                pass

        elapsed_ms = round((time.time() - start_time) * 1000, 1)

        return {
            "status": "SUEÑO_CONSOLIDADO",
            "decayed_synapses": decayed_count,
            "optimized_sqlite": optimized_db,
            "elapsed_ms": elapsed_ms,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Cerebro en reposo: sinapsis consolidadas, índices FTS optimizados y axones débiles podados."
        }

    def _generate_recommendations(
        self,
        broken: list,
        duplicates: list,
        stale: list,
        score: int
    ) -> list[str]:
        recs = []
        if broken:
            recs.append(f"Reparar {len(broken)} enlace(s) rotos detectados en el Vault (revisa 'broken_links').")
        if duplicates:
            recs.append(f"Evaluar fusión de {len(duplicates)} par(es) de notas con títulos redundantes.")
        if stale:
            recs.append(f"Revisar {len(stale)} nota(s) con más de 90 días sin actualización ni activación.")
        if score >= 85:
            recs.append("Cortex en estado óptimo. Sin acciones urgentes de mantenimiento requeridas.")
        return recs
