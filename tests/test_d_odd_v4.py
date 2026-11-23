"""
Tests unitarios para D-ODD v4 (DevBrain v4.1):
  - Cuarentena sustractiva & presupuesto UI en rediseños (sin dispararse en tareas no UI)
  - Lentes Epistémicos en search_memories & brain_context (bloqueo cross-domain / antithesis)
  - Ciclo Dual Vigilia / Sueño silencioso en ontology_engine (promoción + olvido + poda ruido)
  - Superficie MCP consolidada preservada en 12 herramientas
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

_TMP_D_ODD = tempfile.TemporaryDirectory()
if not os.environ.get("DEVBRAIN_HOME"):
    os.environ["DEVBRAIN_HOME"] = _TMP_D_ODD.name
os.environ.setdefault("DEVBRAIN_SKIP_LEGACY_MIGRATION", "1")

import creative_odd  # noqa: E402
import devbrain_mcp  # noqa: E402
import ontology_engine as ont  # noqa: E402
from devbrain_index import DevBrainIndex  # noqa: E402

if devbrain_mcp.VAULT_DIR in devbrain_mcp.DECISIONS_DIR.parents or devbrain_mcp.DECISIONS_DIR == devbrain_mcp.VAULT_DIR:
    _TMP_DEC = Path(_TMP_D_ODD.name) / "vault_decisions"
    _TMP_DEC.mkdir(parents=True, exist_ok=True)
    devbrain_mcp.DECISIONS_DIR = _TMP_DEC


YAML_TEST = """version: 1
dimensions:
  - id: D1
    name: "Sistemas Core & Industria"
    order: 1
    areas:
      - id: A1-industria
        name: "Industria & Telemetría"
        projects:
          - id: Bit4Us-Industrial
            name: "Bit4Us"
            repo_path: "C:\\\\Repos\\\\Bit4Us"
            status: active
            aliases: ["Bit4Us", "Beat For Us"]
          - id: Leopard-SG-Rondas
            name: "Leopard"
            repo_path: "C:\\\\Repos\\\\Leopard"
            status: active
            aliases: ["Leopard"]
      - id: A3-marketplaces
        name: "Marketplaces & Web"
        projects:
          - id: Chambita-Ecosystem
            name: "Chambita"
            repo_path: "C:\\\\Repos\\\\Chambita"
            status: active
            aliases: ["Chambita"]
"""


class TestDODDv4(unittest.TestCase):
    def test_01_subtractive_quarantine_only_on_ui_redesign(self):
        ui_redesign = "Redisenar interfaz de Bit4Us porque muestra demasiados datos y es abrumadora; queremos algo limpio."
        info = creative_odd.detect_redesign_intent(ui_redesign)
        self.assertTrue(info["is_ui"])
        self.assertTrue(info["quarantine_legacy_ui"])

        assess = creative_odd.assess({
            "reversibility_cost": 2, "blast_radius": 2, "uncertainty": 2,
            "vault_novelty": 2, "viable_alternatives": 3,
        })
        pkt = creative_odd.build_context_packet(ui_redesign, "Bit4Us-Industrial", assess, "")
        self.assertIn("Cuarentena Sustractiva & Presupuesto de Densidad UI (D-ODD v4)", pkt)
        self.assertIn("max_primary_kpis=4", pkt)

        backend_obj = "Optimizar indice SQL para consultas de lecturas por org_id en Postgres"
        info_b = creative_odd.detect_redesign_intent(backend_obj)
        self.assertFalse(info_b["quarantine_legacy_ui"])
        pkt_b = creative_odd.build_context_packet(backend_obj, "Bit4Us-Industrial", assess, "")
        self.assertNotIn("Presupuesto de Densidad UI", pkt_b)

    def test_02_epistemic_lenses_filter_cross_domain_and_preserve_12_tools(self):
        tl = devbrain_mcp.process_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
        self.assertEqual(len(tl["result"]["tools"]), 12)

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            vdir = root / "vault"
            dec = vdir / "04-APRENDIZAJES" / "decisiones"
            err = vdir / "04-APRENDIZAJES" / "errores"
            dec.mkdir(parents=True, exist_ok=True)
            err.mkdir(parents=True, exist_ok=True)
            (vdir / "06-SISTEMA").mkdir(parents=True, exist_ok=True)
            yp = vdir / "06-SISTEMA" / "ontologia.yaml"
            yp.write_text(YAML_TEST, encoding="utf-8")
            ont.sync_ontology_yaml(yaml_path=yp, force=True, vault_dir=vdir)

            (dec / "leopard-scada.md").write_text(
                "---\ntitle: \"Leopard SCADA 12 KPIs\"\ntags: [decision, ui, scada-dense]\nproyecto: \"[[Leopard-SG-Rondas]]\"\n---\n\n"
                "# Dashboard 12 KPIs telemetria sensores\nGrid denso de 12 tarjetas.",
                encoding="utf-8",
            )
            (dec / "bit4us-tokens.md").write_text(
                "---\ntitle: \"Bit4Us Tokens Visuales\"\ntags: [decision, ui, tokens]\nproyecto: \"[[Bit4Us-Industrial]]\"\n---\n\n"
                "# Sistema Visual Limpio Bit4Us\nTipografia clara sin sobrecarga de sensores.",
                encoding="utf-8",
            )
            (dec / "bit4us-sse.md").write_text(
                "---\ntitle: \"Bit4Us SSE Stream\"\ntags: [decision, backend, sync]\nproyecto: \"[[Bit4Us-Industrial]]\"\n---\n\n"
                "# SSE Streaming Multi-Tenant\nStream reactivo de sensores sin polling.",
                encoding="utf-8",
            )

            idx = DevBrainIndex(vdir, db_path=root / "fts.db")
            try:
                idx.sync_index(force=True, fast_only=False)

                res_ant = idx.search_memories("sensores dashboard", agent_role="antithesis")
                self.assertIn("0 memorias del Vault", res_ant)

                res_back = idx.search_memories("sensores streaming tokens", project_filter="Bit4Us", agent_role="backend")
                self.assertIn("Bit4Us SSE Stream", res_back)
                self.assertNotIn("Bit4Us Tokens Visuales", res_back)
                self.assertNotIn("Leopard SCADA", res_back)

                res_ui_q = idx.search_memories("dashboard sensores scada", project_filter="Bit4Us", agent_role="ui", quarantine=True)
                self.assertNotIn("Leopard SCADA", res_ui_q)
                self.assertNotIn("Bit4Us SSE Stream", res_ui_q)
            finally:
                idx.close()

        ant_ctx = devbrain_mcp.handle_brain_context({"project": "Bit4Us", "query": "dashboard", "agent_role": "antithesis"})
        self.assertIn("0 memorias/instintos del Vault", ant_ctx)

    def test_03_wake_sleep_cycle_in_ontology_engine(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            vdir = root / "vault"
            dec = vdir / "04-APRENDIZAJES" / "decisiones"
            dec.mkdir(parents=True, exist_ok=True)
            (vdir / "06-SISTEMA").mkdir(parents=True, exist_ok=True)
            yp = vdir / "06-SISTEMA" / "ontologia.yaml"
            yp.write_text(YAML_TEST, encoding="utf-8")
            ont.sync_ontology_yaml(yaml_path=yp, force=True, vault_dir=vdir)

            (dec / "polling-old.md").write_text(
                "---\ntitle: \"Polling HTTP Viejo\"\ntags: [decision, backend]\nproyecto: \"[[Bit4Us-Industrial]]\"\n---\n\n"
                "# Polling cada 5s\nConsultar HTTP en bucle.",
                encoding="utf-8",
            )
            idx = DevBrainIndex(vdir, db_path=root / "fts.db")
            try:
                idx.sync_index(force=True, fast_only=False)

                for _ in range(3):
                    tr = ont.record_wake_trace(
                        "Chambita", "error", "rls-insert-42501",
                        "Definir WITH CHECK en politica INSERT por org_id",
                    )
                    self.assertEqual(tr["online_llm_tokens"], 0)
                    self.assertEqual(tr["project"], "Chambita-Ecosystem")

                ont.record_wake_trace(
                    "Bit4Us", "architecture", "sse-upgrade",
                    "Bit4Us SSE Stream", evidence_passed=True, supersedes_query="polling",
                )
                ont.record_wake_trace("Bit4Us", "typo", "isolated-typo-99", "Fix puntual de texto")

                rep = ont.run_sleep_consolidation(indexer=idx, min_recurrence=2)
                self.assertGreaterEqual(rep["traces_processed"], 5)
                self.assertEqual(rep["instincts_consolidated_count"], 1)
                self.assertIn("A3-marketplaces", rep["auto_promoted_areas"])
                self.assertGreaterEqual(rep["memories_superseded"], 1)
                self.assertGreaterEqual(rep["pruned_noise_count"], 1)

                active = idx.search_memories("polling", project_filter="Bit4Us", include_historical=False)
                self.assertNotIn("Polling HTTP Viejo", active)
            finally:
                idx.close()

    def test_04_fts5_clean_delete_compact_and_remember_seeds(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            vdir = root / "vault"
            know = vdir / "03-CONOCIMIENTO" / "backend"
            know.mkdir(parents=True, exist_ok=True)
            note = know / "legacy-note.md"
            note.write_text("# Token Ghost Alpha\nContenido fantasma inicial.", encoding="utf-8")

            idx = DevBrainIndex(vdir, db_path=root / "fts_clean.db")
            try:
                idx.sync_index(force=True, fast_only=False)
                self.assertIn("Token Ghost Alpha", idx.search_knowledge("fantasma", limit=3))

                note.write_text("# Token Renovado Beta\nContenido nuevo actualizado.", encoding="utf-8")
                idx.sync_index(force=True, fast_only=False)
                res_old = idx.search_knowledge("fantasma", limit=3)
                self.assertIn("No se encontraron", res_old)
                self.assertIn("Token Renovado Beta", idx.search_knowledge("renovado", limit=3))

                note.unlink()
                idx.sync_index(force=True, fast_only=False)
                self.assertIn("No se encontraron", idx.search_knowledge("renovado", limit=3))

                comp = idx.compact_fts(vacuum=True)
                self.assertTrue(comp["vacuumed"])
                self.assertGreaterEqual(comp["before_mb"], comp["after_mb"])
                with idx._get_conn() as con:
                    con.execute("INSERT INTO knowledge_fts(knowledge_fts) VALUES('integrity-check')")
                    con.execute("INSERT INTO memories_fts(memories_fts) VALUES('integrity-check')")
            finally:
                idx.close()

        yp = Path(_TMP_D_ODD.name) / "ontologia_remember.yaml"
        yp.write_text(YAML_TEST, encoding="utf-8")
        ont.sync_ontology_yaml(yaml_path=yp, force=True)
        orig_bridge = devbrain_mcp.GENTLE_PI_BRIDGE
        devbrain_mcp.GENTLE_PI_BRIDGE = None
        try:
            out = devbrain_mcp.handle_brain_remember({
                "title": "Validar RLS con WITH CHECK",
                "details": "Toda politica multi-tenant requiere USING y WITH CHECK",
                "project": "Chambita",
                "tags": ["decision", "pinned"],
            })
        finally:
            devbrain_mcp.GENTLE_PI_BRIDGE = orig_bridge
        self.assertIn("Directriz guardada", out)
        insts = ont.get_instincts("Chambita", min_confidence=0.35)
        self.assertTrue(any("Validar RLS" in i["trigger"] for i in insts))


if __name__ == "__main__":
    unittest.main()
