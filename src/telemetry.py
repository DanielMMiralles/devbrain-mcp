"""
DevBrain Telemetry & Cognitive Event Bus (v1.0)
Captura en tiempo real métricas de rendimiento de la IA: tokens, latencia, costos en USD,
árbol de orquestación, trazas cognitivas ("Cómo Piensa") y disparos de sinapsis.
"""
from __future__ import annotations
import os
import json
import time
import math
from pathlib import Path
from datetime import datetime, timezone
from collections import deque

# Tabla de costos por millón de tokens (USD)
MODEL_PRICING: dict[str, dict[str, float]] = {
    "gemini-3.8-flash": {"in": 0.075, "out": 0.30, "cache": 0.01875},
    "gemini-3.8-flash-cyber": {"in": 0.075, "out": 0.30, "cache": 0.01875},
    "claude-3-5-sonnet": {"in": 3.00, "out": 15.00, "cache": 0.30},
    "claude-sonnet-5": {"in": 3.00, "out": 15.00, "cache": 0.30},
    "claude-opus-5": {"in": 15.00, "out": 75.00, "cache": 1.50},
    "gpt-5.6-sol": {"in": 2.50, "out": 10.00, "cache": 0.25},
    "default": {"in": 0.20, "out": 0.80, "cache": 0.05}
}

def estimate_tokens(text: str) -> int:
    """Estimación heurística precisa de tokens para español, código y JSON (~3.8 caracteres por token)."""
    if not text:
        return 0
    # Heurística ponderada
    return max(1, math.ceil(len(str(text)) / 3.8))

def calculate_cost(model: str, in_tokens: int, out_tokens: int, cached_tokens: int = 0) -> float:
    """Calcula el costo en USD basado en el modelo y conteo de tokens."""
    model_lower = model.lower()
    pricing = MODEL_PRICING.get("default")
    for k, p in MODEL_PRICING.items():
        if k in model_lower:
            pricing = p
            break
            
    cost = (
        (in_tokens * pricing["in"] / 1_000_000.0) +
        (out_tokens * pricing["out"] / 1_000_000.0) +
        (cached_tokens * pricing["cache"] / 1_000_000.0)
    )
    return round(cost, 6)

def resolve_telemetry_dir() -> Path:
    """Resuelve la ruta para el archivo de eventos de telemetría."""
    home_dir = Path(os.path.expanduser("~")) / ".devbrain"
    try:
        home_dir.mkdir(parents=True, exist_ok=True)
        return home_dir
    except Exception:
        fallback = Path("./.devbrain_cache").resolve()
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback

class TelemetryEngine:
    """Motor de telemetría en vivo y bus de eventos cognitivos."""
    
    _instance: TelemetryEngine | None = None

    @classmethod
    def get_instance(cls) -> TelemetryEngine:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, log_dir: Path | None = None):
        self.log_dir = log_dir or resolve_telemetry_dir()
        self.events_file = self.log_dir / "live_events.jsonl"
        self.stats_file = self.log_dir / "session_stats.json"
        
        # Estado en memoria para cálculo de latencias p50/p95 y acumuladores
        self.total_calls: int = 0
        self.total_in_tokens: int = 0
        self.total_out_tokens: int = 0
        self.total_cost_usd: float = 0.0
        self.latencies: deque[float] = deque(maxlen=200)
        self.tool_counts: dict[str, int] = {}
        self.active_client: str = "Standalone"
        self.active_model: str = "gemini-3.8-flash"
        self.recent_events: deque[dict] = deque(maxlen=50)
        self.session_start_time: float = time.time()
        
        self._load_session_stats()

    def _load_session_stats(self) -> None:
        """Carga estadísticas previas desde snapshot o reconstruye desde live_events."""
        if self.stats_file.exists():
            try:
                data = json.loads(self.stats_file.read_text(encoding="utf-8"))
                self.total_calls = data.get("total_calls", 0)
                self.total_in_tokens = data.get("total_in_tokens", 0)
                self.total_out_tokens = data.get("total_out_tokens", 0)
                self.total_cost_usd = data.get("total_cost_usd", 0.0)
                self.tool_counts = data.get("tool_counts", {})
                return
            except Exception:
                pass

        # Reconstrucción desde live_events.jsonl si existe
        if self.events_file.exists():
            try:
                with open(self.events_file, "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        ev = json.loads(line)
                        self.total_calls += 1
                        toks = ev.get("tokens", {})
                        self.total_in_tokens += toks.get("in", 0)
                        self.total_out_tokens += toks.get("out", 0)
                        self.total_cost_usd += ev.get("cost_usd", 0.0)
                        tool = ev.get("tool")
                        if tool:
                            self.tool_counts[tool] = self.tool_counts.get(tool, 0) + 1
                        lat = ev.get("latency_ms")
                        if lat is not None:
                            self.latencies.append(lat)
                        self.recent_events.append(ev)
            except Exception:
                pass

    def _persist_session_stats(self) -> None:
        """Guarda un snapshot de estadísticas."""
        try:
            data = {
                "total_calls": self.total_calls,
                "total_in_tokens": self.total_in_tokens,
                "total_out_tokens": self.total_out_tokens,
                "total_cost_usd": round(self.total_cost_usd, 6),
                "tool_counts": self.tool_counts,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            self.stats_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass

    def detect_client(self, client_info: dict | None = None) -> str:
        """Detecta automáticamente el cliente que está consumiendo DevBrain."""
        if client_info and "name" in client_info:
            name = client_info["name"].lower()
            if "antigravity" in name or "agy" in name:
                self.active_client = "Antigravity (AGY)"
            elif "cursor" in name:
                self.active_client = "Cursor IDE"
            elif "claude" in name:
                self.active_client = "Claude Code"
            elif "tester" in name:
                self.active_client = "Test Runner"
            else:
                self.active_client = client_info["name"]
            return self.active_client

        # Heurísticas por variables de entorno
        if os.getenv("ANTIGRAVITY_AGENT") or os.getenv("GEMINI_CLI"):
            self.active_client = "Antigravity (AGY)"
        elif os.getenv("CURSOR_SESSION") or os.getenv("CURSOR_TRACE_ID"):
            self.active_client = "Cursor IDE"
        elif os.getenv("CLAUDE_CODE_ENTRYPOINT"):
            self.active_client = "Claude Code"
        elif os.getenv("GENTLE_PI_CONFIG_HOME") or os.getenv("GENTLE_SHELL_ACTIVE"):
            self.active_client = "Gentle-Shell"
        return self.active_client

    def record_event(
        self,
        tool_name: str,
        input_data: str | dict,
        output_data: str,
        latency_ms: float,
        plc_route: str = "LOCAL_FAST",
        synapses_fired: list[str] | None = None,
        thought_trace: str = "",
        odd_phase: str = "",
        model: str | None = None,
        client: str | None = None
    ) -> dict:
        """Registra un evento cognitivo y métricas asociadas de forma atómica y no bloqueante."""
        if model:
            self.active_model = model
        if client:
            self.active_client = client

        in_text = json.dumps(input_data) if isinstance(input_data, dict) else str(input_data)
        in_tokens = estimate_tokens(in_text)
        out_tokens = estimate_tokens(output_data)
        cost = calculate_cost(self.active_model, in_tokens, out_tokens)

        # Actualizar acumuladores
        self.total_calls += 1
        self.total_in_tokens += in_tokens
        self.total_out_tokens += out_tokens
        self.total_cost_usd += cost
        self.latencies.append(latency_ms)
        self.tool_counts[tool_name] = self.tool_counts.get(tool_name, 0) + 1

        now_iso = datetime.now(timezone.utc).isoformat()
        event = {
            "timestamp": now_iso,
            "tool": tool_name,
            "client": self.active_client,
            "model": self.active_model,
            "latency_ms": round(latency_ms, 2),
            "tokens": {
                "in": in_tokens,
                "out": out_tokens,
                "total": in_tokens + out_tokens
            },
            "cost_usd": cost,
            "plc_route": plc_route,
            "synapses_fired": synapses_fired or [],
            "thought_trace": thought_trace[:300] if thought_trace else "",
            "odd_phase": odd_phase
        }

        self.recent_events.append(event)

        # Escritura append atómica al archivo de eventos para el HUD en vivo
        try:
            line = json.dumps(event, ensure_ascii=False) + "\n"
            with open(self.events_file, "a", encoding="utf-8", errors="replace") as f:
                f.write(line)
        except Exception:
            pass

        # Persistir snapshot atómico
        self._persist_session_stats()

        return event

    def get_summary(self) -> dict:
        """Calcula el resumen de rendimiento y estado actual."""
        lats = sorted(self.latencies) if self.latencies else [0.0]
        p50 = lats[len(lats) // 2]
        p95_idx = min(len(lats) - 1, int(len(lats) * 0.95))
        p95 = lats[p95_idx]

        elapsed_sec = max(1.0, time.time() - self.session_start_time)
        throughput_tps = round((self.total_in_tokens + self.total_out_tokens) / elapsed_sec, 1)

        return {
            "active_client": self.active_client,
            "active_model": self.active_model,
            "total_calls": self.total_calls,
            "total_tokens": self.total_in_tokens + self.total_out_tokens,
            "total_in_tokens": self.total_in_tokens,
            "total_out_tokens": self.total_out_tokens,
            "total_cost_usd": round(self.total_cost_usd, 6),
            "p50_latency_ms": round(p50, 1),
            "p95_latency_ms": round(p95, 1),
            "throughput_tps": throughput_tps,
            "tool_counts": self.tool_counts,
            "recent_events": list(self.recent_events)
        }

    def tail_events(self, limit: int = 15) -> list[dict]:
        """Lee los últimos eventos directamente desde el bus de eventos en disco."""
        if not self.events_file.exists():
            return list(self.recent_events)
        
        events = []
        try:
            with open(self.events_file, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    line = line.strip()
                    if line:
                        events.append(json.loads(line))
        except Exception:
            return list(self.recent_events)
        return events
