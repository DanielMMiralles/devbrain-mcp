"""
Tests unitarios y de integración para DevBrain v4.0:
- Ontología de 4 niveles (Dimensiones -> Áreas -> Proyectos -> Actividades tipo Beads)
- Resolución de aliases y linaje
- Instintos tipo ECC (project-scoping, confianza, auto-promoción a Área)
- Portada Viva materializada conservando texto manual
- Búsqueda Híbrida (FTS5 + Vectorizer RRF) y validez bi-temporal
- Hooks v4 (SessionStart, Gate systemMessage, Guard PreToolUse ECC)
- MCP v4 (12 tools consolidadas, 3 resources, retrocompatibilidad legacy)
"""

import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
HOOKS_DIR = SRC_DIR / "hooks"
sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(HOOKS_DIR))

_TMP_ROOT = tempfile.TemporaryDirectory()
if not os.environ.get("DEVBRAIN_HOME"):
    os.environ["DEVBRAIN_HOME"] = _TMP_ROOT.name
os.environ.setdefault("DEVBRAIN_SKIP_LEGACY_MIGRATION", "1")

import ontology_engine as ont
from devbrain_index import DevBrainIndex, HybridVectorizer
import devbrain_mcp
import d_odd_hooks

# Aislar DECISIONS_DIR en directorio temporal solo si no fue aislado ya por otra suite
if devbrain_mcp.VAULT_DIR in devbrain_mcp.DECISIONS_DIR.parents or devbrain_mcp.DECISIONS_DIR == devbrain_mcp.VAULT_DIR:
    _TMP_DEC = Path(_TMP_ROOT.name) / "vault_decisions"
    _TMP_DEC.mkdir(parents=True, exist_ok=True)
    devbrain_mcp.DECISIONS_DIR = _TMP_DEC


SAMPLE_YAML = """version: 1
dimensions:
  - id: D1
    name: "Sistemas Core & Industria"
    order: 1
    areas:
      - id: A1-industria
        name: "Industria & Telemetría"
        projects:
          - id: Leopard-SG-Rondas
            name: "Leopard SGRO"
            repo_path: "C:\\\\Repos\\\\Leopard"
            status: active
            aliases: ["Leopard", "Leopard - SG Rondas Operacionales"]
      - id: A2-b2b
        name: "B2B & Gestión"
        projects:
          - id: Lidera-Project
            name: "Lidera"
            repo_path: "C:\\\\Repos\\\\LideraProject"
            status: active
            aliases: ["Lidera", "Lidera_project2026"]
"""


class TestDevBrainV4(unittest.TestCase):

    def test_01_ontology_sync_aliases_and_4level_tree(self):
        yp = Path(_TMP_ROOT.name) / "ontologia.yaml"
        yp.write_text(SAMPLE_YAML, encoding="utf-8")
        res = ont.sync_ontology_yaml(yaml_path=yp, force=True)
        self.assertEqual(res["dimensions"], 1)
        self.assertEqual(res["areas"], 2)
        self.assertEqual(res["projects"], 2)

        self.assertEqual(ont.resolve_project("Lidera_project2026"), "Lidera-Project")
        self.assertEqual(ont.resolve_project(r"C:\Repos\Leopard\src\App.tsx"), "Leopard-SG-Rondas")

        # Actividades con dependencias (Beads pattern)
        a1 = ont.manage_activity("create", project="Leopard", title="Diseñar esquema WAL", priority=1)
        a1_id = a1["activity"]["id"]
        a2 = ont.manage_activity("create", project="Leopard", title="Construir dashboard HMI", blocked_by=a1_id)
        self.assertEqual(a2["activity"]["status"], "blocked")

        ready_before = [x["id"] for x in ont.ready_activities("Leopard-SG-Rondas")]
        self.assertIn(a1_id, ready_before)
        self.assertNotIn(a2["activity"]["id"], ready_before)

        # Completar a1 desbloquea a2 automáticamente
        ont.manage_activity("done", activity_id=a1_id)
        ready_after = [x["id"] for x in ont.ready_activities("Leopard-SG-Rondas")]
        self.assertIn(a2["activity"]["id"], ready_after)

        tree = ont.get_tree_markdown()
        self.assertIn("D1 — Sistemas Core & Industria", tree)
        self.assertIn("Leopard-SG-Rondas", tree)

    def test_02_ecc_instincts_scoping_and_autopromotion(self):
        # Grabar instinto en Lidera -> no debe aparecer en Leopard
        ont.record_instinct("Lidera_project2026", "auth-rls", "Validar tenant_id en cada policy RLS")
        leopard_inst = ont.get_instincts("Leopard-SG-Rondas")
        self.assertFalse(any(i["trigger"] == "auth-rls" for i in leopard_inst))

        # 3 confirmaciones más en Leopard deben promover el instinto al Área A1-industria
        r1 = ont.record_instinct("Leopard", "hmi-contrast", "Usar alto contraste ISA-101")
        self.assertEqual(r1["instinct"]["confidence"], 0.40)
        r2 = ont.record_instinct("Leopard", "hmi-contrast", "Usar alto contraste ISA-101")
        r3 = ont.record_instinct("Leopard", "hmi-contrast", "Usar alto contraste ISA-101")
        r4 = ont.record_instinct("Leopard", "hmi-contrast", "Usar alto contraste ISA-101")
        self.assertGreaterEqual(r4["instinct"]["confidence"], 0.80)
        self.assertEqual(r4["promoted_to"], "A1-industria")

    def test_03_live_portada_materialization_preserves_manual_notes(self):
        tvault = Path(_TMP_ROOT.name) / "tmp_vault"
        tvault.mkdir(parents=True, exist_ok=True)
        portada = tvault / "Portada.md"
        portada.write_text(
            "# PORTADA\n\n## 🎯 1. Horizonte Activo\nViejo\n\n## 🌐 3. Malla Transversal\n- Mis notas manuales intactas\n",
            encoding="utf-8",
        )
        t0 = time.perf_counter()
        rep = ont.render_live_portada(tvault)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        self.assertTrue(rep["updated"])
        self.assertLess(elapsed_ms, 150.0)
        txt = portada.read_text(encoding="utf-8")
        self.assertIn(ont.AUTO_START, txt)
        self.assertIn(ont.AUTO_END, txt)
        self.assertIn("Mis notas manuales intactas", txt)

    def test_04_hybrid_search_and_bitemporal_memories(self):
        vdir = Path(_TMP_ROOT.name) / "search_vault"
        dec_dir = vdir / "04-APRENDIZAJES" / "decisiones"
        know_dir = vdir / "03-CONOCIMIENTO" / "backend"
        dec_dir.mkdir(parents=True, exist_ok=True)
        know_dir.mkdir(parents=True, exist_ok=True)

        (dec_dir / "decision-old.md").write_text(
            "---\ntags: [decision]\nproyecto: \"[[Leopard]]\"\nfecha: 2026-09-01\n---\n\n# Usar polling HTTP cada 5s\nPolling simple.",
            encoding="utf-8",
        )
        (dec_dir / "decision-new.md").write_text(
            "---\ntags: [decision, pinned]\nproyecto: \"[[Leopard]]\"\nfecha: 2026-11-10\n---\n\n# Autenticacion JWT y OAuth2\nToken stateless en cabecera.",
            encoding="utf-8",
        )
        (know_dir / "redis-caching.md").write_text(
            "# Redis In-Memory Cache\nReduces database latency using key-value memory store.",
            encoding="utf-8",
        )

        idx = DevBrainIndex(vdir, db_path=Path(_TMP_ROOT.name) / "test_hybrid.db")
        try:
            # Búsqueda conceptual por sinónimo ("latencia rendimiento memoria" encuentra Redis In-Memory Cache)
            res_k = idx.search_knowledge("latencia velocidad cache", limit=3)
            self.assertIn("redis caching", res_k.lower())

            # Búsqueda conceptual de memorias ("login permisos sesion" encuentra "Autenticacion JWT y OAuth2")
            res_m = idx.search_memories("login permisos sesion", project_filter="Leopard")
            self.assertIn("Autenticacion JWT", res_m)

            # Validez bi-temporal: marcar vieja como obsoleta
            n = idx.supersede_memory("polling http", "SSE Streaming")
            self.assertGreaterEqual(n, 1)
            res_old = idx.search_memories("polling", include_historical=False)
            self.assertNotIn("Usar polling HTTP", res_old)
            res_hist = idx.search_memories("polling", include_historical=True)
            self.assertIn("Usar polling HTTP", res_hist)
        finally:
            idx.close()

    def test_05_hooks_session_start_gate_and_ecc_guard(self):
        # SessionStart debe inyectar systemMessage con contexto del proyecto
        ss = d_odd_hooks.hook_session_start({"cwd": r"C:\Repos\Leopard"})
        self.assertIn("injectSteps", ss)
        msg = ss["injectSteps"][0]["systemMessage"]["systemMessage"]
        self.assertIn("Leopard-SG-Rondas", msg)

        # Gate debe disparar con este prompt arquitectónico (usa systemMessage, no deprecated ephemeralMessage)
        g = d_odd_hooks.hook_gate({
            "conversationId": "conv-v4-test",
            "lastUserInput": "Necesito que analices la estructura completa de DevBrain para mejorar su autonomia y organizar la portada",
        })
        self.assertIn("injectSteps", g)
        self.assertIn("systemMessage", g["injectSteps"][0])

        # ECC Guardrail PreToolUse
        blocked = d_odd_hooks.hook_guard({"toolCall": {"name": "run_command", "args": {"CommandLine": "git commit -m x --no-verify"}}})
        self.assertEqual(blocked["decision"], "ask")

        secret_block = d_odd_hooks.hook_guard({
            "toolCall": {"name": "write_file", "args": {"Path": "app.py", "Content": "API='sk-1234567890abcdefghijklmnop'"}}
        })
        self.assertEqual(secret_block["decision"], "ask")

        safe = d_odd_hooks.hook_guard({"toolCall": {"name": "run_command", "args": {"CommandLine": "pytest tests/"}}})
        self.assertEqual(safe["decision"], "allow")

    def test_06_mcp_v4_surface_resources_and_legacy_compat(self):
        tl = devbrain_mcp.process_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
        tools = tl["result"]["tools"]
        self.assertEqual(len(tools), 12)

        rl = devbrain_mcp.process_request({"jsonrpc": "2.0", "id": 2, "method": "resources/list", "params": {}})
        uris = [r["uri"] for r in rl["result"]["resources"]]
        self.assertIn("devbrain://portada", uris)
        self.assertIn("devbrain://tree", uris)

        rr = devbrain_mcp.process_request({"jsonrpc": "2.0", "id": 3, "method": "resources/read", "params": {"uri": "devbrain://tree"}})
        self.assertIn("Sistemas Core & Industria", rr["result"]["contents"][0]["text"])

        # Nuevas tools + compatibilidad legacy
        ctx = devbrain_mcp.process_request({
            "jsonrpc": "2.0", "id": 4, "method": "tools/call",
            "params": {"name": "brain_context", "arguments": {"project": "Leopard"}}
        })
        self.assertIn("Leopard-SG-Rondas", ctx["result"]["content"][0]["text"])

        leg = devbrain_mcp.process_request({
            "jsonrpc": "2.0", "id": 5, "method": "tools/call",
            "params": {"name": "classify_odd_task", "arguments": {"request_description": "Cambiar color de boton"}}
        })
        self.assertIn("SMALL_DIRECT", leg["result"]["content"][0]["text"])


if __name__ == "__main__":
    unittest.main()
