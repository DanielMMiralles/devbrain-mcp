"""
Tests unitarios y de integración para el marco D-ODD (Dynamic Outcome-Driven Development)
en DevBrain MCP.
"""

import unittest
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from creative_odd import (
    CynefinDomain,
    CreativeMode,
    classify_cynefin,
    select_provocations,
    triangulate_cognitive_odd,
    format_creative_odd_markdown,
    run_creative_odd_pipeline
)
from devbrain_mcp import (
    handle_stimulate_creative_odd,
    handle_orchestrate_gentle_task
)
from plc_router import PLCRouter

class TestCreativeODD(unittest.TestCase):

    def test_cynefin_classification(self):
        # 1. Clear / Canónico
        res_clear = classify_cynefin("Corrige un typo en el README", files_touched_estimate=1)
        self.assertEqual(res_clear["domain"], CynefinDomain.CLEAR.value)
        self.assertFalse(res_clear["divergence_required"])
        self.assertEqual(res_clear["action_protocol"], "fast_track")

        # 2. Complicated / Analítico
        res_comp = classify_cynefin("Optimizar query FTS5 en la base de datos", files_touched_estimate=2)
        self.assertEqual(res_comp["domain"], CynefinDomain.COMPLICATED.value)
        self.assertFalse(res_comp["divergence_required"])
        self.assertEqual(res_comp["action_protocol"], "analytical_graph")

        # 3. Complex / Emergente (Activa D-ODD)
        res_cx = classify_cynefin("Diseñar la arquitectura de concurrencia y desacoplar el estado", files_touched_estimate=4)
        self.assertEqual(res_cx["domain"], CynefinDomain.COMPLEX.value)
        self.assertTrue(res_cx["divergence_required"])
        self.assertEqual(res_cx["action_protocol"], "divergent_triangulation")

        # 4. Chaotic / Contención
        res_ch = classify_cynefin("Crash en producción con corrupción de base de datos", files_touched_estimate=1)
        self.assertEqual(res_ch["domain"], CynefinDomain.CHAOTIC.value)
        self.assertEqual(res_ch["action_protocol"], "stabilize_first")

    def test_provocation_seeds(self):
        provs = select_provocations("Diseño de caché distribuido", count=2)
        self.assertEqual(len(provs), 2)
        self.assertTrue(any(k in provs[0] for k in ["id", "title", "question", "focus"]))

    def test_triangulate_cognitive_odd_modes(self):
        modes = ["divergent", "red_team", "first_principles", "lateral"]
        for m in modes:
            tri = triangulate_cognitive_odd(
                objective="Estructurar nuevo motor de eventos",
                project_name="Narval-SGN",
                creative_mode=m,
                vault_context="En el pasado se usó una tabla SQLite para jobs."
            )
            self.assertIn("thesis", tri)
            self.assertIn("antithesis", tri)
            self.assertIn("synthesis", tri)
            self.assertIn("outcomes", tri)
            self.assertIn("tasks", tri)
            self.assertTrue(len(tri["tasks"]) >= 3)

    def test_format_creative_odd_markdown(self):
        tri = triangulate_cognitive_odd(
            objective="Crear micro-broker de mensajería",
            project_name="Chambita",
            creative_mode="divergent"
        )
        md = format_creative_odd_markdown(tri)
        self.assertIn("# 🧠 DevBrain D-ODD", md)
        self.assertIn("Desacoplamiento de Resultados", md)
        self.assertIn("Tesis (Canon del Vault", md)
        self.assertIn("Antítesis (Pensamiento Disruptivo", md)
        self.assertIn("Síntesis D-ODD", md)
        self.assertIn("Tareas ODD de Acción Inmediata", md)

    def test_handle_stimulate_creative_odd_mcp(self):
        res = handle_stimulate_creative_odd({
            "objective": "Evaluar cómo evitar el comportamiento estático del cerebro en decisiones de arquitectura",
            "project_name": "DevBrain",
            "creative_mode": "first_principles",
            "write_to_disk": False
        })
        self.assertIn("DevBrain D-ODD: Triangulación Dialéctica", res)
        self.assertIn("[CYNEFIN: COMPLEJO / EMERGENTE]", res)
        self.assertIn("Antítesis de Primeros Principios", res)

    def test_orchestrate_gentle_task_creative_integration(self):
        # Tarea compleja en auto debe invocar D-ODD
        res = handle_orchestrate_gentle_task({
            "task_description": "Diseñar e implementar una nueva arquitectura de toma de decisiones para LLMs",
            "project_name": "DevBrain",
            "mode": "auto"
        })
        self.assertIn("DevBrain: Orquestación D-ODD Dinámica", res)
        self.assertIn("Triangulación dialéctica completada", res)
        self.assertIn("odd/tasks/", res)

        # Modo explícito 'creative'
        res_creative = handle_orchestrate_gentle_task({
            "task_description": "Implementar módulo de caché en memoria",
            "project_name": "DevBrain",
            "mode": "creative"
        })
        self.assertIn("DevBrain: Orquestación D-ODD Dinámica", res_creative)

        # Modo 'direct' mantiene Fast Path
        res_direct = handle_orchestrate_gentle_task({
            "task_description": "Explica la clase PLCRouter",
            "project_name": "DevBrain",
            "mode": "direct"
        })
        self.assertIn("DevBrain Fast Path", res_direct)

    def test_plc_router_has_creative_tool(self):
        router = PLCRouter()
        self.assertEqual(router.classify("stimulate_creative_odd"), PLCRouter.ROUTE_LOCAL)


if __name__ == "__main__":
    unittest.main()
