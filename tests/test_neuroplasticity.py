"""
Tests Unitarios para DevBrain Neuroplasticity Engine & PLC Router
Verifica LTP, LTD, poda sináptica, reranking contextual y routing PLC.
"""
import unittest
import sys
import tempfile
import os
from pathlib import Path
from datetime import datetime, timedelta

# Agregar src al path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))


class TestSynapticEngine(unittest.TestCase):
    """Tests del motor de plasticidad sináptica."""

    def setUp(self):
        """Crear una DB temporal para cada test."""
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.db_path = Path(self.tmp.name)
        from neuroplasticity import SynapticEngine
        self.engine = SynapticEngine(self.db_path)

    def tearDown(self):
        try:
            os.unlink(self.db_path)
        except Exception:
            pass

    def test_record_activation_creates_entry(self):
        """Registrar una activación debe crear una entrada en la tabla."""
        self.engine.record_activation("odd", context_type="coding", session_id="sess-001")
        nodes = self.engine.get_session_nodes("sess-001")
        self.assertIn("odd", nodes)

    def test_hebbian_co_activation(self):
        """Dos nodos activados en la misma sesión deben crear una sinapsis (Hebb)."""
        self.engine.record_activation("odd", session_id="sess-002")
        self.engine.record_activation("clean-architecture", session_id="sess-002")
        
        associated = self.engine.get_associated_nodes("odd")
        keys = [a["key"] for a in associated]
        self.assertIn("clean-architecture", keys)

    def test_ltp_strengthening(self):
        """Cada co-activación debe incrementar el peso sináptico (LTP)."""
        self.engine.strengthen_synapse("odd", "tdd", delta=1.0)
        w1 = self.engine.get_associated_nodes("odd")[0]["weight"]

        self.engine.strengthen_synapse("odd", "tdd", delta=1.0)
        w2 = self.engine.get_associated_nodes("odd")[0]["weight"]

        self.assertGreater(w2, w1, "LTP debe incrementar el peso con cada refuerzo")

    def test_ltp_saturation(self):
        """El peso sináptico debe saturar en W_MAX=100.0, nunca excederlo."""
        for _ in range(200):
            self.engine.strengthen_synapse("a", "b", delta=5.0)
        
        assoc = self.engine.get_associated_nodes("a")
        self.assertLessEqual(assoc[0]["weight"], 100.0, "Peso no debe exceder W_MAX")

    def test_bidirectional_synapses(self):
        """strengthen_synapse debe crear sinapsis bidireccionales."""
        self.engine.strengthen_synapse("node_a", "node_b")
        
        from_a = self.engine.get_associated_nodes("node_a")
        from_b = self.engine.get_associated_nodes("node_b")
        
        self.assertTrue(any(n["key"] == "node_b" for n in from_a))
        self.assertTrue(any(n["key"] == "node_a" for n in from_b))

    def test_ltd_decay(self):
        """decay_synapses debe reducir pesos según half-life exponencial."""
        self.engine.strengthen_synapse("x", "y", delta=10.0)
        
        # Forzar last_fired a hace 60 días
        import sqlite3
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        old_date = (datetime.now() - timedelta(days=60)).isoformat()
        conn.execute("UPDATE synapses SET last_fired = ?", (old_date,))
        conn.commit()
        conn.close()
        
        decayed = self.engine.decay_synapses(half_life_days=30.0)
        self.assertGreater(decayed, 0, "Debe haber decaído al menos una sinapsis")
        
        assoc = self.engine.get_associated_nodes("x")
        if assoc:
            # Después de 60 días con half-life de 30 → peso ~= original * 0.25
            self.assertLess(assoc[0]["weight"], 10.0, "LTD debe reducir peso")

    def test_pruning(self):
        """prune_synapses debe eliminar sinapsis bajo el umbral mínimo."""
        self.engine.strengthen_synapse("a", "b", delta=0.05)
        
        # Forzar peso muy bajo
        import sqlite3
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.execute("UPDATE synapses SET weight = 0.01")
        conn.commit()
        conn.close()
        
        pruned = self.engine.prune_synapses(min_weight=0.1)
        self.assertGreater(pruned, 0, "Debe haber podado sinapsis bajo umbral")
        
        assoc = self.engine.get_associated_nodes("a")
        self.assertEqual(len(assoc), 0, "No deben quedar sinapsis después de la poda")

    def test_synaptic_bonus(self):
        """compute_synaptic_bonus debe retornar un score > 0 para nodos conectados."""
        self.engine.strengthen_synapse("odd", "tdd", delta=5.0)
        
        bonus = self.engine.compute_synaptic_bonus("tdd", session_nodes=["odd"], scale=0.5)
        self.assertGreater(bonus, 0.0, "Bonus sináptico debe ser positivo para nodos conectados")
        
        no_bonus = self.engine.compute_synaptic_bonus("tdd", session_nodes=["unrelated"], scale=0.5)
        self.assertEqual(no_bonus, 0.0, "Bonus debe ser 0 para nodos sin conexión")

    def test_hot_paths(self):
        """get_hot_paths debe retornar las sinapsis más fuertes."""
        self.engine.strengthen_synapse("odd", "tdd", delta=10.0)
        self.engine.strengthen_synapse("cqrs", "saga", delta=5.0)
        
        hot = self.engine.get_hot_paths(limit=2)
        self.assertGreaterEqual(len(hot), 1)
        self.assertEqual(hot[0]["source"], "odd")

    def test_stats(self):
        """get_stats debe retornar estadísticas del motor sináptico."""
        self.engine.strengthen_synapse("a", "b", delta=3.0)
        self.engine.record_activation("a", session_id="s1")
        
        stats = self.engine.get_stats()
        self.assertGreater(stats["total_synapses"], 0)
        self.assertGreater(stats["total_activations"], 0)
        self.assertGreater(stats["avg_weight"], 0)


class TestPLCRouter(unittest.TestCase):
    """Tests del controlador lógico programable (PLC Router)."""

    def setUp(self):
        from plc_router import PLCRouter
        self.router = PLCRouter()

    def test_classify_local_fast(self):
        """Herramientas LOCAL_FAST deben clasificarse como 'local'."""
        from plc_router import PLCRouter
        for tool in PLCRouter.LOCAL_FAST:
            result = self.router.classify(tool)
            self.assertEqual(result, PLCRouter.ROUTE_LOCAL, f"{tool} debe ser LOCAL")

    def test_classify_delegatable(self):
        """Herramientas DELEGATABLE deben clasificarse como 'delegate'."""
        from plc_router import PLCRouter
        for tool in PLCRouter.DELEGATABLE:
            result = self.router.classify(tool)
            self.assertEqual(result, PLCRouter.ROUTE_DELEGATE, f"{tool} debe ser DELEGATE")

    def test_classify_orchestrator(self):
        """Herramientas REQUIRES_ORCHESTRATOR deben clasificarse como 'orchestrate'."""
        from plc_router import PLCRouter
        for tool in PLCRouter.REQUIRES_ORCHESTRATOR:
            result = self.router.classify(tool)
            self.assertEqual(result, PLCRouter.ROUTE_ORCHESTRATE, f"{tool} debe ser ORCHESTRATE")

    def test_classify_unknown_defaults_local(self):
        """Herramientas desconocidas deben rutear a local por defecto."""
        from plc_router import PLCRouter
        result = self.router.classify("unknown_tool_xyz")
        self.assertEqual(result, PLCRouter.ROUTE_LOCAL)

    def test_route_local_returns_process_local(self):
        """Routing de herramienta local debe retornar action='process_local'."""
        result = self.router.route("search_knowledge", {"query": "odd"})
        self.assertEqual(result["action"], "process_local")
        self.assertEqual(result["tool"], "search_knowledge")

    def test_route_delegatable_without_gentle_pi(self):
        """Sin Gentle-PI, herramientas delegables deben fallar a local con fallback=True."""
        import time
        self.router._gentle_pi_available = False
        self.router._last_probe = time.time()  # Evitar que probe_gentle_pi re-evalúe
        result = self.router.route("prepare_odd_task", {"feature_name": "test"})
        self.assertEqual(result["action"], "process_local")
        self.assertTrue(result.get("fallback", False))

    def test_format_delegation_payload(self):
        """El payload de delegación debe seguir el formato inter-orquestador."""
        payload = self.router.format_delegation_payload(
            "prepare_odd_task",
            {"feature_name": "test-feature"}
        )
        self.assertEqual(payload["type"], "DEVBRAIN_DELEGATION")
        self.assertEqual(payload["source"], "devbrain-mcp")
        self.assertEqual(payload["tool"], "prepare_odd_task")
        self.assertTrue(payload["requires_ack"])

    def test_routing_stats(self):
        """get_routing_stats debe retornar conteos correctos de herramientas."""
        stats = self.router.get_routing_stats()
        self.assertIn("gentle_pi_available", stats)
        self.assertIn("local_tools", stats)
        self.assertGreater(stats["local_tools"], 0)
        self.assertGreater(stats["delegatable_tools"], 0)


class TestGenerateSessionId(unittest.TestCase):
    """Test del generador de session IDs."""

    def test_session_id_format(self):
        """El session ID debe tener formato YYYYMMDD-XXXX."""
        from neuroplasticity import generate_session_id
        sid = generate_session_id()
        self.assertRegex(sid, r"^\d{8}-[0-9a-f]{4}$")

    def test_session_ids_are_unique(self):
        """Dos session IDs consecutivos deben ser distintos."""
        from neuroplasticity import generate_session_id
        s1 = generate_session_id()
        s2 = generate_session_id()
        self.assertNotEqual(s1, s2)


if __name__ == "__main__":
    unittest.main()
