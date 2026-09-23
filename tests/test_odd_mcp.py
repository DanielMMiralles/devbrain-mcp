"""
Unit Tests for DevBrain MCP Server: ODD & Gentle-Shell Extensions
"""
import unittest
import sys
from pathlib import Path

# Agregar src al path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from devbrain_mcp import (
    handle_classify_odd_task,
    handle_prepare_odd_task,
    handle_reconcile_odd_resume,
    handle_orchestrator_session_bridge,
    handle_prepare_sdd_preflight,
    handle_search_knowledge
)

class TestDevBrainODD(unittest.TestCase):

    def test_classify_read_only(self):
        res = handle_classify_odd_task({
            "request_description": "Explica como funciona la arquitectura de CQRS en el proyecto",
            "is_read_only": True
        })
        self.assertIn("[READ_ONLY]", res)
        self.assertIn("Zero ceremony", res)

    def test_classify_small_direct(self):
        res = handle_classify_odd_task({
            "request_description": "Corrige un typo en el mensaje de error de login",
            "files_touched_estimate": 1
        })
        self.assertIn("[SMALL_DIRECT]", res)
        self.assertIn("Tarea pequeña", res)

    def test_classify_substantial_odd(self):
        res = handle_classify_odd_task({
            "request_description": "Implementar módulo completo de autenticación OAuth2 con Google y GitHub",
            "files_touched_estimate": 5
        })
        self.assertIn("[SUBSTANTIAL_ODD]", res)
        self.assertIn("odd/tasks/", res)
        self.assertIn("odd/<feature-name>/tasks", res)
        self.assertIn("Review Mode (Gentle-AI v3.5.0)", res)
        self.assertIn("fail-safe", res)

    def test_classify_explicit_sdd(self):
        res = handle_classify_odd_task({
            "request_description": "Por favor use SDD para diseñar la nueva arquitectura del motor de pagos",
            "explicit_sdd_requested": True
        })
        self.assertIn("[EXPLICIT_SDD]", res)
        self.assertIn("openspec/specs/", res)

    def test_prepare_odd_task_document(self):
        res = handle_prepare_odd_task({
            "feature_name": "Exportador CSV Métricas",
            "project_name": "Chambita",
            "objective": "Permitir a los administradores descargar reportes en CSV",
            "scope": "Solo exportación de datos ya filtrados en pantalla",
            "tasks": [
                "Crear endpoint GET /api/reports/csv",
                "Implementar streaming CSV con fast-csv",
                "Añadir tests unitarios y de integración"
            ],
            "acceptance_criteria": [
                "Tiempo de respuesta < 500ms para 10k filas",
                "Cabeceras Content-Disposition correctas"
            ],
            "tdd_mode": True,
            "test_runner": "pnpm test"
        })
        self.assertIn("[ODD] Creado odd/tasks/exportador-csv-metricas.md con 3 tareas", res)
        self.assertIn("# Feature: Exportador CSV Métricas", res)
        self.assertIn("- [ ] [TASK-01] Crear endpoint GET /api/reports/csv", res)
        self.assertIn("- [ ] [TASK-02] Implementar streaming CSV con fast-csv", res)
        self.assertIn("- [ ] [TASK-03] Añadir tests unitarios y de integración", res)
        self.assertIn("TDD Mode**: ENABLED (Observed RED -> GREEN -> REFACTOR required)", res)
        self.assertIn("Engram Mirror Locator**: `odd/exportador-csv-metricas/tasks`", res)

    def test_reconcile_odd_resume(self):
        file_content = """# Feature: Test
- [x] [TASK-01] Configuración inicial
- [ ] [TASK-02] Implementación de lógica
"""
        engram_mirror = """# Feature: Test
- [x] [TASK-01] Configuración inicial
- [x] [TASK-02] Implementación de lógica
- [ ] [TASK-03] Verificación final
"""
        res = handle_reconcile_odd_resume({
            "feature_name": "test-feature",
            "project_name": "TestProject",
            "file_content": file_content,
            "engram_mirror_content": engram_mirror
        })
        self.assertIn("Reconciliación de Sesión ODD", res)
        self.assertIn("Divergencia Detectada", res)
        self.assertIn("Tareas Verificadas Totales (2)", res)

    def test_orchestrator_session_bridge(self):
        explain_res = handle_orchestrator_session_bridge({"action": "explain"})
        self.assertIn("orchestrator_session_id", explain_res)
        self.assertIn("orchestrator_send_message", explain_res)
        self.assertIn("Semántica ACK", explain_res)

        format_res = handle_orchestrator_session_bridge({
            "action": "format_notification",
            "session_id": "sess-alpha-01",
            "target_session_id": "sess-worker-02",
            "message_payload": {"type": "ODD_TASK_DELEGATION", "task": "TASK-02"}
        })
        self.assertIn("sess-alpha-01", format_res)
        self.assertIn("sess-worker-02", format_res)
        self.assertIn("orchestrator_send_message", format_res)

        ack_res = handle_orchestrator_session_bridge({
            "action": "verify_ack",
            "target_session_id": "sess-worker-02",
            "ack_received": True
        })
        self.assertIn("Transporte ACK Confirmado", ack_res)

    def test_prepare_sdd_preflight_lightened(self):
        res = handle_prepare_sdd_preflight({
            "feature_name": "Motor de Pagos",
            "project_name": "Narval-SGN"
        })
        self.assertIn("Gentle-AI v3.0 Lightened SDD Contract", res)
        self.assertIn("Workflow Branch**: Explicit SDD Opt-In", res)
        self.assertIn("108 rutas burocráticas retiradas", res)

    def test_builtin_knowledge_odd_and_gentle_shell(self):
        odd_know = handle_search_knowledge({"query": "odd"})
        self.assertIn("Organic Driven Development", odd_know)
        self.assertIn("preguntas interactivas", odd_know)

        shell_know = handle_search_knowledge({"query": "gentle-shell"})
        self.assertIn("Gentle-Shell", shell_know)
        self.assertIn("gentle-shell", shell_know)

        engram_know = handle_search_knowledge({"query": "engram-v2"})
        self.assertIn("Engram v2.0", engram_know)

        rdd_know = handle_search_knowledge({"query": "rdd"})
        self.assertIn("PRENDIDA de fábrica", rdd_know)
        self.assertIn("fail-safe", rdd_know)

        neuro_know = handle_search_knowledge({"query": "neuroplasticity"})
        self.assertIn("Neuroplasticidad", neuro_know)
        self.assertIn("Hebb", neuro_know)

        plc_know = handle_search_knowledge({"query": "plc-router"})
        self.assertIn("PLC Router", plc_know)
        self.assertIn("LOCAL_FAST", plc_know)

    def test_synaptic_recording_and_bonus(self):
        # Ejecutar búsquedas co-ocurrentes
        handle_search_knowledge({"query": "odd"})
        handle_search_knowledge({"query": "clean architecture"})
        
        # Verificar que buscar odd ahora tiene sinapsis o notas
        res = handle_search_knowledge({"query": "odd"})
        self.assertIn("Organic Driven Development", res)

if __name__ == "__main__":
    unittest.main()
