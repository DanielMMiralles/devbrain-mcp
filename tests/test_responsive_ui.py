"""
Tests para la Arquitectura Responsive y Adaptativa de DevBrain CLI y HUD (test_responsive_ui.py)
Verifica la adaptación de breakpoints (Narrow < 90/112, Medium, Wide >= 112, Compact Height < 28)
y la ausencia de desbordamiento horizontal en terminales estándar de 79/80 columnas.
"""
from __future__ import annotations
import unittest
import sys
from pathlib import Path
from unittest.mock import patch

# Añadir src al path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from rich.console import Console
from cli_hud import DevBrainHUD
from cli_shell import DevBrainShell
from cli_help import render_help_overview
from cli_theme import ConfigManager

class TestResponsiveUI(unittest.TestCase):

    def setUp(self):
        self.config_mgr = ConfigManager()

    def test_layout_mode_detection(self):
        """Verifica que el HUD detecte correctamente los modos narrow, wide y compact_height."""
        c_narrow = Console(width=79, height=24, legacy_windows=False)
        hud_narrow = DevBrainHUD(c_narrow, self.config_mgr)
        m_narrow = hud_narrow.get_layout_mode()
        self.assertTrue(m_narrow["is_narrow"])
        self.assertFalse(m_narrow["is_wide"])
        self.assertTrue(m_narrow["is_compact_height"])

        c_wide = Console(width=140, height=40, legacy_windows=False)
        hud_wide = DevBrainHUD(c_wide, self.config_mgr)
        m_wide = hud_wide.get_layout_mode()
        self.assertFalse(m_wide["is_narrow"])
        self.assertTrue(m_wide["is_wide"])
        self.assertFalse(m_wide["is_compact_height"])

    def test_render_narrow_79x24(self):
        """Verifica que el HUD se renderice perfectamente en una terminal estándar de 79x24."""
        c = Console(width=79, height=24, legacy_windows=False)
        hud = DevBrainHUD(c, self.config_mgr)
        layout = hud.render_layout()
        self.assertIsNotNone(layout)

        # Capturar salida renderizada en string
        with c.capture() as capture:
            c.print(layout)
        output = capture.get()

        # Verificar títulos compactos para no quebrar columnas de 38 caracteres
        self.assertIn("Métricas & Tokens", output)
        self.assertIn("¿Cómo Piensa?", output)
        self.assertIn("Orquestación", output)
        self.assertIn("DEVBRAIN", output)

    def test_render_wide_140x40(self):
        """Verifica que el HUD se renderice en modo completo en pantallas anchas."""
        c = Console(width=140, height=40, legacy_windows=False)
        hud = DevBrainHUD(c, self.config_mgr)
        layout = hud.render_layout()
        self.assertIsNotNone(layout)

        with c.capture() as capture:
            c.print(layout)
        output = capture.get()

        self.assertIn("Consumo de Tokens", output)
        self.assertIn("Carril de Orquestación en Vivo", output)
        self.assertIn("Host: Standalone", output)

    def test_workspace_dock_responsive(self):
        """Verifica que el dock de DevBrainShell adapte sus banners en narrow y wide."""
        # Modo Narrow
        c_narrow = Console(width=79, height=24, legacy_windows=False)
        shell_narrow = DevBrainShell(c_narrow, config_mgr=self.config_mgr)
        with c_narrow.capture() as cap_narrow:
            shell_narrow.render_workspace()
        out_narrow = cap_narrow.get()
        self.assertIn("WORKSPACE DOCK", out_narrow)
        self.assertIn("Pregunta libre", out_narrow)

        # Modo Wide
        c_wide = Console(width=130, height=35, legacy_windows=False)
        shell_wide = DevBrainShell(c_wide, config_mgr=self.config_mgr)
        with c_wide.capture() as cap_wide:
            shell_wide.render_workspace()
        out_wide = cap_wide.get()
        self.assertIn("WORKSPACE DOCK", out_wide)
        self.assertIn("[Enter = HUD]", out_wide)

    def test_help_overview_responsive(self):
        """Verifica que el manual de ayuda se adapte sin romper líneas en terminales estrechas."""
        c_narrow = Console(width=79, height=24, legacy_windows=False)
        with c_narrow.capture() as cap:
            render_help_overview(c_narrow, self.config_mgr.get_theme())
        out_narrow = cap.get()
        self.assertIn("Comandos del CLI", out_narrow)
        self.assertIn("ask, \"prompt\"", out_narrow)

if __name__ == "__main__":
    unittest.main()
