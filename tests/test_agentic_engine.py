"""
Tests para el Motor Agéntico en Lenguaje Natural de DevBrain (agentic_engine.py)
Verifica la clasificación de intenciones, la síntesis cognitiva determinista,
el registro de telemetría y la integración con el shell interactivo.
"""
from __future__ import annotations
import unittest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Añadir src al path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from agentic_engine import DevBrainAgent, is_endpoint_reachable
from cli_shell import DevBrainShell
from telemetry import TelemetryEngine
from cli_theme import ConfigManager

class TestAgenticEngine(unittest.TestCase):

    def setUp(self):
        self.config_mgr = ConfigManager()
        self.agent = DevBrainAgent(self.config_mgr)
        self.telemetry = TelemetryEngine.get_instance()

    def test_intent_classification_odd(self):
        """Verifica la clasificación de tareas ODD, refactors y features."""
        r1 = self.agent.classify_intent("Necesito crear una tarea para implementar el login OAuth2")
        self.assertEqual(r1.intent_type, "ODD_TASK")
        self.assertIn("classify_odd_task", r1.suggested_tools)

        r2 = self.agent.classify_intent("Vamos a clasificar esta refactorización de la base de datos")
        self.assertEqual(r2.intent_type, "ODD_TASK")

    def test_intent_classification_memory(self):
        """Verifica la clasificación de consultas sobre decisiones y acuerdos pasados."""
        r1 = self.agent.classify_intent("¿Qué decidimos sobre la arquitectura de microservicios?")
        self.assertEqual(r1.intent_type, "DECISION_MEMORY")
        self.assertIn("recall_memory", r1.suggested_tools)

        r2 = self.agent.classify_intent("Recuerda que acordamos usar SQLite para DevBrain")
        self.assertEqual(r2.intent_type, "DECISION_MEMORY")

    def test_intent_classification_health(self):
        """Verifica la clasificación de diagnósticos y chequeos de salud."""
        r1 = self.agent.classify_intent("Revisa la salud del sistema y entorno")
        self.assertEqual(r1.intent_type, "HEALTH_DOCTOR")
        self.assertIn("audit_project_health", r1.suggested_tools)

        r2 = self.agent.classify_intent("Ejecutar chequeo de doctor")
        self.assertEqual(r2.intent_type, "HEALTH_DOCTOR")

    def test_intent_classification_knowledge(self):
        """Verifica la clasificación de consultas conceptuales y técnicas."""
        r1 = self.agent.classify_intent("¿Cómo funciona la regla de Hebb en devbrain?")
        self.assertEqual(r1.intent_type, "KNOWLEDGE_QUERY")
        self.assertIn("search_knowledge", r1.suggested_tools)

        r2 = self.agent.classify_intent("Explica el patrón token bucket para rate limiting")
        self.assertEqual(r2.intent_type, "KNOWLEDGE_QUERY")

    def test_intent_classification_spec_and_debate(self):
        """Verifica la clasificación de especificaciones OpenSpec y debates de factibilidad."""
        r_spec = self.agent.classify_intent("Quiero crear spec de la API de pagos")
        self.assertEqual(r_spec.intent_type, "SPEC_ARCHITECTURE")

        r_deb = self.agent.classify_intent("Debatamos si es mejor migrar a PostgreSQL o quedarnos en SQLite")
        self.assertEqual(r_deb.intent_type, "DEBATE_FEASIBILITY")

    def test_process_prompt_deterministic(self):
        """Verifica que el pipeline agéntico procese un prompt y devuelva respuesta estructurada."""
        res = self.agent.process_prompt("¿Cómo funciona la neuroplasticidad?")
        self.assertIsNotNone(res)
        self.assertIn("DevBrain", res.content)
        self.assertEqual(res.intent, "KNOWLEDGE_QUERY")
        self.assertGreater(res.tokens_in, 0)
        self.assertGreater(res.tokens_out, 0)
        self.assertGreaterEqual(res.latency_ms, 0)
        self.assertIn(res.plc_route, ["LOCAL_FAST", "DELEGATABLE"])

    def test_telemetry_event_recorded(self):
        """Verifica que al procesar un prompt agéntico se registre el evento en TelemetryEngine."""
        initial_calls = self.telemetry.total_calls
        self.agent.process_prompt("Explica el protocolo ODD en 2 líneas")
        self.assertGreater(self.telemetry.total_calls, initial_calls)
        recent = list(self.telemetry.recent_events)
        self.assertTrue(any(ev.get("tool") == "agentic_prompt" for ev in recent))

    def test_shell_handles_natural_language(self):
        """Verifica que DevBrainShell despache lenguaje natural a través de agentic_engine."""
        shell = DevBrainShell(config_mgr=self.config_mgr)
        # Mock de print para no ensuciar la salida
        with patch.object(shell.console, "print") as mock_print:
            shell.handle_command("¿Qué es DevBrain?")
            mock_print.assert_called()

    def test_is_endpoint_reachable(self):
        """Verifica que is_endpoint_reachable devuelva False para puertos cerrados sin lanzar excepciones."""
        # Puerto 59999 local improbable de estar abierto
        reachable = is_endpoint_reachable("http://127.0.0.1:59999", timeout=0.04)
        self.assertFalse(reachable)

if __name__ == "__main__":
    unittest.main()
