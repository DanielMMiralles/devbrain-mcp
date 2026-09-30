"""
Tests Unitarios para CortexHousekeeper (src/cortex_housekeeper.py)
Verifica la detección de enlaces rotos, duplicados semánticos,
poda sináptica y el ciclo de sueño / consolidación profunda.
"""
from __future__ import annotations
import unittest
import sys
import tempfile
import sqlite3
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Agregar src al path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from cortex_housekeeper import CortexHousekeeper


class TestCortexHousekeeper(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.vault_dir = Path(self.tmp_dir.name)
        self.db_path = self.vault_dir / "test_fts.db"

        # 1. Crear notas de prueba en el Vault simulado
        # Nota 1: referencia válida a [[arquitectura-hexagonal]] y rota a [[microservicios-imaginarios]]
        (self.vault_dir / "clean-architecture.md").write_text(
            "# Clean Architecture\n\nVer también [[arquitectura-hexagonal]] y [[microservicios-imaginarios]].\n",
            encoding="utf-8"
        )
        # Nota 2: destino válido
        (self.vault_dir / "arquitectura-hexagonal.md").write_text(
            "# Arquitectura Hexagonal\n\nPuertos y adaptadores para aislar el dominio.\n",
            encoding="utf-8"
        )
        # Notas 3 y 4: títulos redundantes para detección de duplicados
        (self.vault_dir / "guia-docker-contenedores.md").write_text(
            "# Docker Contenedores\n\nGuía de uso de Docker y Dockerfile.\n",
            encoding="utf-8"
        )
        (self.vault_dir / "guia-docker-contenedores-v2.md").write_text(
            "# Docker Contenedores v2\n\nGuía de uso de Docker y Dockerfile avanzada.\n",
            encoding="utf-8"
        )

        # 2. Inicializar DB SQLite con tabla synapses
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        c.execute("""
            CREATE TABLE synapses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_key TEXT NOT NULL,
                target_key TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                fire_count INTEGER DEFAULT 1,
                last_fired TEXT,
                created_at TEXT
            )
        """)
        old_time = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
        # Sinapsis fuerte reciente
        c.execute("INSERT INTO synapses VALUES (1, 'clean-architecture', 'arquitectura-hexagonal', 8.5, 10, ?, ?)",
                  (datetime.now(timezone.utc).isoformat(), old_time))
        # Sinapsis débil vieja (< 0.1)
        c.execute("INSERT INTO synapses VALUES (2, 'clean-architecture', 'legacy-cobol', 0.05, 1, ?, ?)",
                  (old_time, old_time))
        conn.commit()
        conn.close()

        self.hk = CortexHousekeeper(vault_dir=self.vault_dir, db_path=self.db_path)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_discover_all_notes(self):
        notes = self.hk._discover_all_notes()
        self.assertEqual(len(notes), 4)
        self.assertIn("clean-architecture", notes)
        self.assertIn("arquitectura-hexagonal", notes)

    def test_detect_broken_links(self):
        notes = self.hk._discover_all_notes()
        broken = self.hk._detect_broken_links(notes)
        self.assertGreaterEqual(len(broken), 1)
        targets = [b["broken_target"] for b in broken]
        self.assertIn("microservicios-imaginarios", targets)
        self.assertEqual(broken[0]["source_note"], "clean-architecture")

    def test_detect_duplicates(self):
        notes = self.hk._discover_all_notes()
        dups = self.hk._detect_semantic_duplicates(notes)
        self.assertGreaterEqual(len(dups), 1)
        names = {dups[0]["note_a"], dups[0]["note_b"]}
        self.assertIn("guia-docker-contenedores.md", names)
        self.assertIn("guia-docker-contenedores-v2.md", names)

    def test_audit_cortex_health(self):
        res = self.hk.audit_cortex_health(
            scan_broken_links=True,
            scan_duplicates=True,
            scan_ltd=True,
            auto_prune=False
        )
        self.assertEqual(res["total_notes"], 4)
        self.assertGreaterEqual(res["broken_links_count"], 1)
        self.assertGreaterEqual(res["duplicates_count"], 1)
        self.assertIn("health_score", res)
        self.assertIn("recommendations", res)
        self.assertGreater(len(res["recommendations"]), 0)

    def test_prune_weak_synapses(self):
        pruned = self.hk.prune_weak_synapses(min_weight=0.1)
        self.assertEqual(pruned, 1)

        # Comprobar que solo quedó la sinapsis fuerte
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM synapses")
        count = c.fetchone()[0]
        conn.close()
        self.assertEqual(count, 1)

    def test_consolidate_dream_cycle(self):
        res = self.hk.consolidate_dream_cycle()
        self.assertIn("status", res)
        self.assertEqual(res["status"], "SUEÑO_CONSOLIDADO")
        self.assertIn("decayed_synapses", res)
        self.assertEqual(res["decayed_synapses"], 1)
        self.assertIn("elapsed_ms", res)


if __name__ == "__main__":
    unittest.main()
