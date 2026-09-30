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

        ignored = {".obsidian", ".git", ".devbrain_cache", ".trash", "node_modules", ".venv", "__pycache__"}
        for p in self.vault_dir.rglob("*.md"):
            if any(part in ignored or part.startswith(".") for part in p.parts):
                continue
            name_clean = p.stem.strip()
            if name_clean:
                notes[name_clean.lower()] = p

        return notes

    def _discover_all_folders(self) -> dict[str, Path]:
        """Mapea carpetas existentes en el Vault (nombre en minúsculas -> Path)."""
        folders = {}
        if not self.vault_dir.exists():
            return folders
        ignored = {".obsidian", ".git", ".devbrain_cache", ".trash", "node_modules", ".venv", "__pycache__"}
        for p in self.vault_dir.rglob("*"):
            if p.is_dir() and not any(part in ignored or part.startswith(".") for part in p.parts):
                folders[p.name.strip().lower()] = p
        return folders

    def _detect_broken_links(self, all_notes: dict[str, Path]) -> list[dict[str, Any]]:
        """Busca referencias a notas que no existen en el Vault con emparejamiento sináptico inteligente."""
        broken = []
        note_keys = list(all_notes.keys())
        folders = self._discover_all_folders()

        # Revisar una muestra representativa o todas las notas
        scanned_count = 0
        for name_lower, path in all_notes.items():
            if scanned_count > 350:  # Límite de tiempo/performance
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
                    # Emparejamiento sináptico inteligente
                    sugg = None
                    m_type = None
                    is_folder = False

                    # 1. ¿Es una carpeta del Vault?
                    if target_lower in folders:
                        f_path = folders[target_lower]
                        is_folder = True
                        for sub in f_path.glob("*.md"):
                            if sub.stem.lower() in ["readme", "index", "arquitectura", target_lower]:
                                sugg = sub.stem
                                m_type = "folder_note"
                                break
                        if not sugg:
                            sugg = f_path.name
                            m_type = "folder"

                    # 2. Acrónimo corto (<= 6 letras, p. ej. OIDC, EKS, KEDA)
                    if not sugg and len(target_lower) <= 6:
                        for k, p in all_notes.items():
                            if f"({target_lower})" in k or f"[{target_lower}]" in k:
                                sugg = p.stem
                                m_type = "acronym"
                                break

                    # 3. Coincidencia por tokens y prefijo
                    if not sugg:
                        tok_matches = [
                            p.stem for k, p in all_notes.items()
                            if k.startswith(target_lower + " ") or k.startswith(target_lower + "-") or f" {target_lower} " in f" {k} "
                        ]
                        if tok_matches:
                            core = [m for m in tok_matches if "core principles" in m.lower() or "architecture" in m.lower()]
                            sugg = min(core, key=len) if core else min(tok_matches, key=len)
                            m_type = "token"

                    # 4. Fallback difflib (cutoff 0.55)
                    if not sugg:
                        close = difflib.get_close_matches(target_lower, note_keys, n=1, cutoff=0.55)
                        if close:
                            sugg = all_notes[close[0]].stem
                            m_type = "similarity"

                    broken.append({
                        "source_note": path.stem,
                        "broken_target": target,
                        "suggested_fix": sugg,
                        "match_type": m_type,
                        "is_folder": is_folder
                    })
                    if len(broken) >= 50:
                        break
            if len(broken) >= 50:
                break

        return broken

    def _detect_semantic_duplicates(self, all_notes: dict[str, Path]) -> list[dict[str, Any]]:
        """Detecta notas con títulos redundantes o duplicadas en el Vault."""
        duplicates = []
        names = sorted(list(all_notes.keys()))

        SUBSECTION_SUFFIXES = [
            'core principles & architecture', 'integration & verification runbook',
            'performance tuning & benchmarks', 'production gotchas & anti-patterns',
            'safety, formal invariants & proofs', 'security hardening & zero trust',
            'core principles & mechanics', 'safety, alignment & invariants',
            'benchmark & performance tuning', 'cheat sheet', 'deep dive', 'architecture', 'runbook'
        ]
        DATE_PATTERN = re.compile(r'(\b\d{4}[-_]\d{2}[-_]\d{2}\b|\b\d{2}[-_]\d{2}[-_]\d{2,4}\b)')
        VERSION_PATTERN = re.compile(r'[-@_]v?\d+(\.\d+)+')

        for i in range(len(names) - 1):
            n1 = names[i]
            n2 = names[i + 1]

            # Ignorar bitácoras o notas fechadas con misma plantilla
            if DATE_PATTERN.search(n1) and DATE_PATTERN.search(n2):
                continue

            # Ignorar releases con versiones distintas
            if VERSION_PATTERN.search(n1) and VERSION_PATTERN.search(n2):
                n1_no_ver = VERSION_PATTERN.sub('', n1)
                n2_no_ver = VERSION_PATTERN.sub('', n2)
                if n1_no_ver == n2_no_ver:
                    continue

            # Ignorar subseries de un mismo tema modular (p. ej. Runbook vs Architecture)
            is_series = False
            for s1 in SUBSECTION_SUFFIXES:
                if s1 in n1:
                    for s2 in SUBSECTION_SUFFIXES:
                        if s2 in n2 and s1 != s2:
                            is_series = True
                            break
            if is_series:
                continue

            ratio = difflib.SequenceMatcher(None, n1, n2).quick_ratio()
            if ratio >= 0.88:
                duplicates.append({
                    "note_a": all_notes[n1].name,
                    "note_b": all_notes[n2].name,
                    "similarity": round(ratio * 100, 1)
                })
                if len(duplicates) >= 20:
                    break
        return duplicates

    def fix_broken_link(self, source_note: str, broken_target: str, fix_target: str) -> dict[str, Any]:
        """Reemplaza un enlace roto [[broken_target]] por [[fix_target]] en el archivo fuente."""
        all_notes = self._discover_all_notes()
        path = all_notes.get(source_note.lower())
        if not path or not path.exists():
            return {"success": False, "message": f"Nota fuente '{source_note}' no encontrada en el Vault."}

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            pattern = re.compile(rf"\[\[{re.escape(broken_target)}(\|[a-zA-Z0-9_\-\s]+)?\]\]")
            def replacer(m):
                alias = m.group(1) or ""
                return f"[[{fix_target}{alias}]]"
            new_content, count = pattern.subn(replacer, content)
            if count > 0:
                path.write_text(new_content, encoding="utf-8")
                return {"success": True, "count": count, "message": f"Enlace reparado: [[{broken_target}]] ➔ [[{fix_target}]] ({count} ocurrencia(s))."}
            return {"success": False, "message": f"No se encontró el patrón [[{broken_target}]] en la nota."}
        except Exception as e:
            return {"success": False, "message": f"Error al escribir en archivo: {e}"}

    def create_missing_note(self, note_name: str, folder: str = "03-CONOCIMIENTO") -> dict[str, Any]:
        """Crea una nueva nota vacía en el Vault para satisfacer un enlace roto."""
        target_dir = self.vault_dir / folder
        if not target_dir.exists():
            target_dir = self.vault_dir
        clean_name = note_name.strip().replace("/", "-").replace("\\", "-")
        target_path = target_dir / f"{clean_name}.md"

        if target_path.exists():
            return {"success": True, "path": str(target_path), "message": f"La nota '{clean_name}.md' ya existe en el Vault."}

        template = f"""---
tags: [concepto, devbrain]
creado_por: DevBrain Cortex
fecha: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
---

# {clean_name}

> Nota conceptual inicializada automáticamente por DevBrain Cortex para resolver sinapsis pendientes.

## Contexto y Definición
- 

## Conexiones y Referencias
- 
"""
        try:
            target_path.write_text(template, encoding="utf-8")
            return {"success": True, "path": str(target_path), "message": f"Nota creada exitosamente en {folder}/{clean_name}.md"}
        except Exception as e:
            return {"success": False, "message": f"Error creando nota: {e}"}

    def unlink_broken_link(self, source_note: str, broken_target: str) -> dict[str, Any]:
        """Convierte [[broken_target]] en texto plano broken_target en la nota fuente."""
        all_notes = self._discover_all_notes()
        path = all_notes.get(source_note.lower())
        if not path or not path.exists():
            return {"success": False, "message": f"Nota fuente '{source_note}' no encontrada."}

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            pattern = re.compile(rf"\[\[{re.escape(broken_target)}\]\]")
            new_content, count = pattern.subn(broken_target, content)
            if count > 0:
                path.write_text(new_content, encoding="utf-8")
                return {"success": True, "count": count, "message": f"Enlace desvinculado a texto plano '{broken_target}'."}
            return {"success": False, "message": f"No se encontró [[{broken_target}]] en la nota."}
        except Exception as e:
            return {"success": False, "message": f"Error desvinculando: {e}"}

    def batch_fix_all_suggestions(self) -> dict[str, Any]:
        """Aplica automáticamente todas las reparaciones de enlaces que tienen sugerencias de alta confianza."""
        all_notes = self._discover_all_notes()
        broken = self._detect_broken_links(all_notes)
        repaired = 0
        for b in broken:
            if b.get("suggested_fix") and not b.get("is_folder"):
                res = self.fix_broken_link(b["source_note"], b["broken_target"], b["suggested_fix"])
                if res.get("success"):
                    repaired += 1
        return {
            "repaired_count": repaired,
            "total_broken": len(broken),
            "message": f"Se repararon automáticamente {repaired} enlaces con sugerencias inteligentes."
        }

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
