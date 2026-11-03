"""
Tests unitarios y de integración para el marco D-ODD v2 (Dynamic Outcome-Driven Development)
con separación de responsabilidades: gate determinista + juicio semántico + ledger + calibración.
"""

import unittest
import sys
import os
import json
import tempfile
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

# Aislar el entorno de pruebas para no alterar la BD de producción
_TMP_DIR = tempfile.TemporaryDirectory()
os.environ["DEVBRAIN_HOME"] = _TMP_DIR.name

import decision_ledger as led
from creative_odd import (
    CynefinDomain,
    gate_score,
    assess,
    provocations_for,
    is_ui_objective,
    deal_visual_directions,
    build_context_packet,
    calibrate,
    load_calibration,
    DEFAULT_CALIBRATION
)
from d_odd_corpus import CORPUS
import devbrain_mcp
from devbrain_mcp import (
    handle_assess_decision,
    handle_commit_decision,
    handle_close_decision,
    handle_decision_ledger_stats,
    handle_stimulate_creative_odd,
    handle_orchestrate_gentle_task,
    process_request
)
from plc_router import PLCRouter

# Redirigir DECISIONS_DIR al directorio temporal para no escribir en el Vault real durante tests
devbrain_mcp.DECISIONS_DIR = Path(_TMP_DIR.name)


class TestCreativeODDv2(unittest.TestCase):

    def test_gate_corpus_accuracy(self):
        """Verifica que el gate capture decisiones de diseño y no dispare en triviales."""
        misses = 0
        fps = 0
        cal = load_calibration()
        for phrase, is_decision in CORPUS:
            res = gate_score(phrase, cal)
            if is_decision and not res["fired"]:
                misses += 1
            elif not is_decision and res["fired"]:
                fps += 1
        self.assertEqual(misses, 0, f"El gate omitió {misses} decisiones reales.")
        self.assertEqual(fps, 0, f"El gate tuvo {fps} falsos positivos en tareas triviales.")

    def test_assess_dimension_mapping(self):
        """Verifica que las dimensiones del LLM mapeen a los dominios Cynefin correctos."""
        # 1. Clear: costo y blast radius bajos, alternativa única
        res_clear = assess({
            "reversibility_cost": 0, "blast_radius": 0, "uncertainty": 0,
            "vault_novelty": 0, "viable_alternatives": 0
        })
        self.assertEqual(res_clear["domain"], CynefinDomain.CLEAR.value)
        self.assertEqual(res_clear["verdict"], "fast_track")

        # 2. Complicated: análisis técnico acotado
        res_comp = assess({
            "reversibility_cost": 1, "blast_radius": 1, "uncertainty": 1,
            "vault_novelty": 1, "viable_alternatives": 1
        })
        self.assertEqual(res_comp["domain"], CynefinDomain.COMPLICATED.value)
        self.assertEqual(res_comp["verdict"], "analytical")

        # 3. Complex: alta incertidumbre y alternativas viables (activa D-ODD)
        res_cx = assess({
            "reversibility_cost": 2, "blast_radius": 2, "uncertainty": 2,
            "vault_novelty": 2, "viable_alternatives": 2
        })
        self.assertEqual(res_cx["domain"], CynefinDomain.COMPLEX.value)
        self.assertEqual(res_cx["verdict"], "d_odd")

        # 4. Chaotic: flag de incidente activo
        res_ch = assess({
            "reversibility_cost": 1, "blast_radius": 1, "uncertainty": 1,
            "vault_novelty": 1, "viable_alternatives": 1
        }, incident=True)
        self.assertEqual(res_ch["domain"], CynefinDomain.CHAOTIC.value)
        self.assertEqual(res_ch["verdict"], "stabilize_first")

    def test_provocations_selection(self):
        """Verifica que las provocaciones se seleccionen según la dimensión dominante."""
        provs_rev = provocations_for("reversibility_cost")
        self.assertTrue(any(p["id"] == "REVERSIBILITY" for p in provs_rev))

        provs_nov = provocations_for("vault_novelty")
        self.assertTrue(any(p["id"] == "INVERSION" for p in provs_nov))

    def test_full_decision_lifecycle_mcp(self):
        """Prueba E2E: assess -> commit -> close -> stats."""
        conv_id = "test-conv-e2e-01"

        # Simular evento previo del gate
        led.record_gate_event(conv_id, "hash123", 0.65, 0.35, True)

        # 1. Assess (Complejo)
        assess_res = handle_assess_decision({
            "objective": "Migrar colas de jobs de Redis a Postgres",
            "project_name": "DevBrain",
            "reversibility_cost": 2,
            "blast_radius": 2,
            "uncertainty": 2,
            "vault_novelty": 2,
            "viable_alternatives": 2,
            "conversation_id": conv_id
        })
        self.assertIn("D-ODD activado", assess_res)
        self.assertIn("Protocolo D-ODD (divergencia con contextos aislados)", assess_res)

        # Extraer decision_id
        open_decs = led.open_decisions(conv_id)
        self.assertTrue(len(open_decs) >= 1)
        dec_id = open_decs[0]["id"]

        # 2. Commit
        commit_res = handle_commit_decision({
            "decision_id": dec_id,
            "chosen": "antithesis",
            "synthesis": "Se adopta tabla append-only en Postgres con LISTEN/NOTIFY para evitar dependencias.",
            "tasks": ["Crear migración de jobs", "Implementar worker"],
            "acceptance_criteria": ["Latencia p95 < 5ms"],
            "write_to_disk": False
        })
        self.assertIn(f"Decisión `{dec_id}` comprometida", commit_res)

        # 3. Adjuntar evidencia simulando ejecución de tests
        led.attach_evidence(conv_id, {"type": "test_run", "command": "pytest", "passed": True})

        # 4. Close
        close_res = handle_close_decision({
            "decision_id": dec_id,
            "outcome": "success",
            "notes": "Funciona impecable con cero sobrecarga operativa."
        })
        self.assertIn(f"Decisión `{dec_id}` cerrada", close_res)
        self.assertIn("success", close_res)

        # 5. Stats
        stats_res = handle_decision_ledger_stats({})
        self.assertIn("D-ODD · Bucle de aprendizaje", stats_res)
        self.assertIn("100% de 1 comprometidas", stats_res)

    def test_orchestrate_gentle_task_with_d_odd(self):
        """Verifica que orchestrate_gentle_task enlace decisiones o sugiera assess sin forzar artefactos."""
        # Tarea que dispara gate sugiere assess
        res_gate = handle_orchestrate_gentle_task({
            "task_description": "Diseñar arquitectura para micro-broker de eventos",
            "project_name": "DevBrain",
            "mode": "auto"
        })
        self.assertIn("Posible decisión de diseño", res_gate)

        # Tarea simple no mete aviso de decisión
        res_simple = handle_orchestrate_gentle_task({
            "task_description": "Corrige un typo en el mensaje de error",
            "project_name": "DevBrain",
            "mode": "auto"
        })
        self.assertNotIn("Posible decisión de diseño", res_simple)

    def test_plc_router_all_tools_local(self):
        """Verifica que las 4 nuevas tools y las previas de D-ODD estén en LOCAL_FAST."""
        router = PLCRouter()
        for t in ["assess_decision", "commit_decision", "close_decision", "decision_ledger_stats", "stimulate_creative_odd"]:
            self.assertEqual(router.classify(t), PLCRouter.ROUTE_LOCAL)

    def test_visual_variance_dealer_and_anti_clone_veto(self):
        """Verifica que objetivos UI reciban el Anti-Clone Veto y 2 direcciones visuales contrastadas."""
        ui_obj = "Crear desde cero el dashboard de monitoreo forense de rondas en planta"
        self.assertTrue(is_ui_objective(ui_obj))
        d1, d2 = deal_visual_directions(ui_obj, "Leopard")
        self.assertNotEqual(d1["id"], d2["id"])

        res_cx = assess({
            "reversibility_cost": 2, "blast_radius": 2, "uncertainty": 2,
            "vault_novelty": 2, "viable_alternatives": 2
        })
        pkt = build_context_packet(ui_obj, "Leopard", res_cx, "", "dec-ui-test")
        self.assertIn("VETO ANTI-CLON VISUAL", pkt)
        self.assertIn("Direcciones de Arte Sorteadas", pkt)

    def test_mcp_initialize_and_prompts(self):
        """Verifica que initialize exponga instructions y prompts/list + prompts/get expongan d-odd."""
        init_res = process_request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        self.assertIn("instructions", init_res["result"])
        self.assertIn("prompts", init_res["result"]["capabilities"])

        plist = process_request({"jsonrpc": "2.0", "id": 2, "method": "prompts/list", "params": {}})
        self.assertEqual(plist["result"]["prompts"][0]["name"], "d-odd")

        pget = process_request({
            "jsonrpc": "2.0", "id": 3, "method": "prompts/get",
            "params": {"name": "d-odd", "arguments": {"objective": "Rediseñar dashboard industrial", "project_name": "Leopard"}}
        })
        self.assertIn("VETO ANTI-CLON VISUAL", pget["result"]["messages"][0]["content"]["text"])


if __name__ == "__main__":
    unittest.main()
