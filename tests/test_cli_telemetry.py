"""
Tests Unitarios para DevBrain CLI, Motor de Telemetría y Cognitive HUD.
Verifica:
1. Estimación de tokens y cálculo de costos en USD.
2. Grabación y acumulación de métricas en TelemetryEngine.
3. Detección automática del Host IDE (Antigravity, Cursor, Claude Code).
4. Persistencia y cambio de temas en ConfigManager (Modo Papa incluido).
5. Renderizado sin excepciones del layout multipanel de DevBrainHUD.
"""
import unittest
import sys
import tempfile
import os
from pathlib import Path

# Agregar src al path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from telemetry import (
    TelemetryEngine,
    estimate_tokens,
    calculate_cost,
    MODEL_PRICING
)
from cli_theme import ConfigManager, THEMES, ThemeColors
from cli_hud import DevBrainHUD


class TestTelemetryEngine(unittest.TestCase):
    """Pruebas unitarias para el motor de telemetría y métricas de rendimiento."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.tmp_dir.name)
        self.engine = TelemetryEngine(log_dir=self.data_dir)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_estimate_tokens_empty_and_valid(self):
        """estimate_tokens debe devolver 0 para cadenas vacías y cálculo heurístico para texto."""
        self.assertEqual(estimate_tokens(""), 0)
        tokens = estimate_tokens("Hola mundo, probando DevBrain ODD y su motor de telemetría.")
        self.assertGreater(tokens, 5)

    def test_calculate_cost_models(self):
        """calculate_cost debe aplicar tarifas diferenciadas por familia de modelo."""
        cost_flash = calculate_cost("gemini-3.8-flash", in_tokens=10_000, out_tokens=5_000)
        cost_sonnet = calculate_cost("claude-sonnet-5", in_tokens=10_000, out_tokens=5_000)
        
        self.assertGreater(cost_sonnet, cost_flash, "Sonnet debe costar más que Flash por token")
        self.assertGreater(cost_flash, 0.0)

    def test_detect_client_host_signatures(self):
        """detect_client debe reconocer Antigravity, Cursor, Claude Code o Test Runner."""
        self.assertEqual(self.engine.detect_client({"name": "antigravity-ide"}), "Antigravity (AGY)")
        self.assertEqual(self.engine.detect_client({"name": "cursor-agent"}), "Cursor IDE")
        self.assertEqual(self.engine.detect_client({"name": "claude-code"}), "Claude Code")
        self.assertEqual(self.engine.detect_client({"name": "unit-tester"}), "Test Runner")
        self.assertEqual(self.engine.detect_client({"name": "custom-agent"}), "custom-agent")

    def test_record_event_and_stats_accumulation(self):
        """Grabar eventos debe reflejarse en métricas agregadas (throughput, tokens, latencia)."""
        ev = self.engine.record_event(
            tool_name="search_knowledge",
            input_data={"query": "odd architecture"},
            output_data="Organic Driven Development guide...",
            latency_ms=12.5,
            plc_route="LOCAL_FAST",
            synapses_fired=["odd", "tdd"],
            thought_trace="Local retrieval performed via FTS5 with synaptic rerank.",
            model="gemini-3.8-flash",
            client="Antigravity (AGY)"
        )

        self.assertIsNotNone(ev)
        self.assertEqual(ev["tool"], "search_knowledge")
        self.assertEqual(ev["plc_route"], "LOCAL_FAST")
        self.assertIn("odd", ev["synapses_fired"])

        summary = self.engine.get_summary()
        self.assertEqual(summary["total_calls"], 1)
        self.assertGreater(summary["total_tokens"], 0)
        self.assertGreater(summary["total_cost_usd"], 0.0)
        self.assertEqual(summary["tool_counts"].get("search_knowledge"), 1)
        self.assertEqual(summary["active_client"], "Antigravity (AGY)")
        self.assertEqual(summary["active_model"], "gemini-3.8-flash")

    def test_persistence_and_reload(self):
        """Los snapshots deben persistir en session_stats.json y recuperarse en una nueva instancia."""
        self.engine.record_event(
            tool_name="classify_odd_task",
            input_data={"task": "Fix bug in CLI"},
            output_data="SMALL_DIRECT",
            latency_ms=8.0
        )

        # Crear una segunda instancia apuntando al mismo log_dir
        engine2 = TelemetryEngine(log_dir=self.data_dir)
        summary2 = engine2.get_summary()
        self.assertEqual(summary2["total_calls"], 1)
        self.assertEqual(summary2["tool_counts"].get("classify_odd_task"), 1)


class TestConfigManager(unittest.TestCase):
    """Pruebas unitarias para gestión de configuración, temas y Modo Papa."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.tmp_dir.name) / "config.json"
        self.config_mgr = ConfigManager(config_file=self.config_path)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_default_theme_is_gentleman(self):
        """El tema por defecto debe ser gentleman."""
        self.assertEqual(self.config_mgr.config.get("theme"), "gentleman")
        theme = self.config_mgr.get_theme()
        self.assertEqual(theme.name, "Gentleman-Dark")
        self.assertEqual(theme.primary, "magenta")

    def test_switch_theme_persists(self):
        """Cambiar de tema debe persistirse a disco y cambiar los estilos."""
        success = self.config_mgr.set_theme("cyberpunk")
        self.assertTrue(success)
        self.assertEqual(self.config_mgr.config.get("theme"), "cyberpunk")
        
        # Recargar en una nueva instancia
        reloaded = ConfigManager(config_file=self.config_path)
        self.assertEqual(reloaded.config.get("theme"), "cyberpunk")
        self.assertEqual(reloaded.get_theme().name, "Cyberpunk")

    def test_invalid_theme_rejected(self):
        """Intentar asignar un tema desconocido debe fallar de forma segura."""
        success = self.config_mgr.set_theme("inexistente_123")
        self.assertFalse(success)
        self.assertEqual(self.config_mgr.config.get("theme"), "gentleman")

    def test_papa_mode_toggle(self):
        """Activar y desactivar Modo Papa debe reflejarse en configuración."""
        self.assertFalse(self.config_mgr.config.get("papa_mode"))
        new_state = self.config_mgr.toggle_papa_mode()
        self.assertTrue(new_state)
        self.assertTrue(self.config_mgr.config.get("papa_mode"))
        
        # En modo papa, get_theme devuelve la paleta austera 'papa'
        self.assertEqual(self.config_mgr.get_theme().name, "Modo Papa (Minimal)")
        
        new_state2 = self.config_mgr.toggle_papa_mode()
        self.assertFalse(new_state2)
        self.assertFalse(self.config_mgr.config.get("papa_mode"))


class TestDevBrainHUD(unittest.TestCase):
    """Pruebas unitarias para el renderizado del dashboard HUD."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.tmp_dir.name)
        self.telemetry = TelemetryEngine(log_dir=self.data_dir)
        # Apuntar el singleton a la instancia de prueba temporal
        TelemetryEngine._instance = self.telemetry

        self.config_path = self.data_dir / "config.json"
        self.config_mgr = ConfigManager(config_file=self.config_path)
        self.hud = DevBrainHUD(config_mgr=self.config_mgr)

    def tearDown(self):
        TelemetryEngine._instance = None
        self.tmp_dir.cleanup()

    def test_render_layout_returns_rich_layout(self):
        """render_layout debe devolver un objeto Layout de Rich con todos los paneles."""
        self.telemetry.record_event(
            tool_name="classify_odd_task",
            input_data={"task": "Implement CLI"},
            output_data="STANDARD_FEATURE",
            latency_ms=9.1,
            plc_route="LOCAL_FAST",
            synapses_fired=["odd", "gentle-ai"],
            thought_trace="Classifying task as standard feature with TDD loop."
        )

        layout = self.hud.render_layout()
        self.assertIsNotNone(layout)
        self.assertIsNotNone(layout["header"])
        self.assertIsNotNone(layout["main"])
        self.assertIsNotNone(layout["footer"])

    def test_render_layout_in_papa_mode(self):
        """En Modo Papa el HUD debe renderizarse con la paleta minimalista sin errores."""
        self.config_mgr.toggle_papa_mode()
        self.hud.theme = self.config_mgr.get_theme()
        layout = self.hud.render_layout()
        self.assertIsNotNone(layout)
        header = self.hud.generate_header(self.telemetry.get_summary())
        self.assertIsNotNone(header)


if __name__ == "__main__":
    unittest.main()
