"""
DevBrain Cortex Server v1.0 — Servidor Local SSE & API del Grafo Cerebral 3D
100% Local (localhost:8765) — Cero Fugas a Internet:
1. Endpoint SSE (/api/events): Transmite en tiempo real el pensamiento y acciones de los agentes desde live_events.jsonl.
2. Endpoint Grafo (/api/graph): Genera la morfología 3D de lóbulos cerebrales con 19.000 neuronas y fibras sinápticas.
3. Servidor Web estático: Entrega el visualizador WebGL 3D a 60 FPS.
4. Endpoint Hook (/api/hook): Recibe eventos instantáneos de Claude Code, Antigravity y Cursor.
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
import threading
import time
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import re
from cortex_housekeeper import CortexHousekeeper

DEFAULT_PORT = 8765
VAULT_DEFAULT = Path(r"C:\Users\damm1\OneDrive\Documentos\Obsidian Vault")
EVENTS_FILE = Path(os.path.expanduser("~")) / ".devbrain" / "live_events.jsonl"


def _global_record_event(event_type: str, data: Any) -> None:
    try:
        EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data
        }
        with open(EVENTS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass


class AutoSleepEngine:
    """Motor de auto-consolidación y modo sueño biológico por inactividad."""
    _instance: AutoSleepEngine | None = None

    @classmethod
    def get_instance(cls, vault_dir: Path | None = None) -> AutoSleepEngine:
        if cls._instance is None:
            v_dir = vault_dir or VAULT_DEFAULT
            cls._instance = AutoSleepEngine(v_dir)
            cls._instance.start()
        return cls._instance

    def __init__(self, vault_dir: Path, idle_minutes: int = 15):
        self.vault_dir = Path(vault_dir).resolve()
        self.idle_minutes = idle_minutes
        self.enabled = True
        self.last_activity = time.time()
        self.last_sleep_timestamp: str | None = None
        self.last_sleep_result: dict | None = None
        self._running = False
        self._thread: threading.Thread | None = None

    def record_activity(self) -> None:
        self.last_activity = time.time()

    def get_status(self) -> dict[str, Any]:
        current_idle = round(time.time() - self.last_activity, 1)
        return {
            "auto_sleep_enabled": self.enabled,
            "idle_minutes_threshold": self.idle_minutes,
            "current_idle_seconds": current_idle,
            "current_idle_minutes": round(current_idle / 60.0, 1),
            "last_sleep_timestamp": self.last_sleep_timestamp,
            "last_sleep_result": self.last_sleep_result
        }

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="DevBrain-AutoSleepEngine")
        self._thread.start()

    def _run_loop(self) -> None:
        while self._running:
            time.sleep(15.0)
            if not self.enabled:
                continue

            idle_duration = time.time() - self.last_activity
            idle_threshold = self.idle_minutes * 60.0

            if idle_duration >= idle_threshold:
                if self.last_sleep_timestamp:
                    try:
                        last_dt = datetime.fromisoformat(self.last_sleep_timestamp)
                        secs_since_last = (datetime.now(timezone.utc) - last_dt).total_seconds()
                        if secs_since_last < (self.idle_minutes * 60.0):
                            continue
                    except Exception:
                        pass

                sys.stdout.write(f"\n[DevBrain Auto-Sleep] Inactividad de {round(idle_duration / 60, 1)} min detectada. Consolidando automáticamente...\n")
                try:
                    hk = CortexHousekeeper(self.vault_dir)
                    res = hk.consolidate_dream_cycle()
                    now_str = datetime.now(timezone.utc).isoformat()
                    self.last_sleep_timestamp = now_str
                    self.last_sleep_result = res
                    
                    event_data = {
                        "type": "auto_sleep_completed",
                        "status": res.get("status"),
                        "decayed_synapses": res.get("decayed_synapses", 0),
                        "optimized_sqlite": res.get("optimized_sqlite", False),
                        "elapsed_ms": res.get("elapsed_ms", 0),
                        "timestamp": now_str,
                        "message": f"Consolidación automática: {res.get('decayed_synapses', 0)} sinapsis decaídas, SQLite FTS optimizado en {res.get('elapsed_ms', 0)} ms."
                    }
                    _global_record_event("auto_sleep_completed", event_data)
                    sys.stdout.write(f"[DevBrain Auto-Sleep] Consolidación completada ({res.get('elapsed_ms', 0)} ms).\n")
                except Exception as e:
                    sys.stdout.write(f"[DevBrain Auto-Sleep] Error: {e}\n")


class BrainMorphologyGenerator:
    """Genera coordenadas 3D para una nube densa de neuronas con la morfología del cerebro humano."""

    @staticmethod
    def generate_brain_cloud(real_notes: list[dict], target_total: int = 19000) -> dict[str, Any]:
        nodes = []
        links = []
        random.seed(42)

        categories = [
            {"id": "frontal", "name": "Lóbulo Frontal (ODD & Decisiones)", "color": "#00f0ff"},
            {"id": "temporal", "name": "Lóbulo Temporal (Memoria & Engram)", "color": "#a855f7"},
            {"id": "parietal", "name": "Lóbulo Parietal (Arquitectura & Código)", "color": "#10b981"},
            {"id": "occipital", "name": "Lóbulo Occipital (Percepción & Logs)", "color": "#f59e0b"},
            {"id": "core", "name": "Cortex Central & Sistema Límbico", "color": "#ec4899"}
        ]

        # 1. Posicionar notas reales primero
        num_real = len(real_notes)
        for i, note in enumerate(real_notes):
            title = note.get("title", f"Nota-{i}")
            cat_idx = hash(title) % len(categories)
            cat = categories[cat_idx]
            x, y, z = BrainMorphologyGenerator._sample_brain_surface(cat["id"], i, max(num_real, 1))
            nodes.append({
                "id": note.get("id", title),
                "label": title,
                "category": cat["id"],
                "color": cat["color"],
                "x": round(x, 2),
                "y": round(y, 2),
                "z": round(z, 2),
                "is_real": True,
                "weight": note.get("weight", 1.0)
            })

        # 2. Generar inter-neuronas de soporte para alcanzar la densidad deseada (~19k)
        remaining = max(0, target_total - len(nodes))
        for j in range(remaining):
            cat = random.choice(categories)
            x, y, z = BrainMorphologyGenerator._sample_brain_surface(cat["id"], j, remaining)
            # Agregar variación interna sutil
            nodes.append({
                "id": f"syn_{j}",
                "label": f"Inter-neurona #{j}",
                "category": cat["id"],
                "color": cat["color"],
                "x": round(x, 2),
                "y": round(y, 2),
                "z": round(z, 2),
                "is_real": False,
                "weight": 0.5
            })

        # 3. Generar fibras sinápticas representativas
        # Conectar neuronas reales vecinas
        num_nodes = len(nodes)
        for k in range(min(num_real * 2, 2500)):
            src = k % num_nodes
            tgt = (k + random.randint(1, 15)) % num_nodes
            links.append({
                "source": nodes[src]["id"],
                "target": nodes[tgt]["id"],
                "weight": random.uniform(0.5, 3.5)
            })

        return {
            "total_neurons": len(nodes),
            "real_notes_count": num_real,
            "total_synapses": len(links),
            "nodes": nodes,
            "links": links
        }

    @staticmethod
    def _sample_brain_surface(region: str, index: int, total: int) -> tuple[float, float, float]:
        """Calcula coordenadas (x, y, z) de dos hemisferios cerebrales elipsoidales con hendidura interhemisférica."""
        # Hemisferio izquierdo (-1) o derecho (+1)
        hemisphere = -1 if (index % 2 == 0) else 1
        
        # Parámetros elipsoidales
        u = random.uniform(0, 2 * math.pi)
        v = random.uniform(-math.pi / 2, math.pi / 2)
        
        rx = 42.0  # Ancho
        ry = 32.0  # Alto
        rz = 55.0  # Profundidad (ant-post)

        # Base elipsoidal
        x = rx * math.cos(v) * math.cos(u)
        y = ry * math.sin(v)
        z = rz * math.cos(v) * math.sin(u)

        # Hendidura interhemisférica
        x = x * 0.45 + (hemisphere * 14.0)

        # Modulación por lóbulos
        if region == "frontal":
            z += 15.0
            y += 4.0
        elif region == "temporal":
            y -= 12.0
            x *= 1.15
        elif region == "parietal":
            y += 14.0
            z -= 5.0
        elif region == "occipital":
            z -= 25.0
            y -= 4.0
        elif region == "core":
            x *= 0.4
            y *= 0.4
            z *= 0.4

        # Circunvoluciones sutiles (arrugas corticales con funciones sinusoidales)
        noise = math.sin(x * 0.3) * math.cos(z * 0.3) * 2.2
        return (x + noise, y + noise, z + noise)


class CortexHTTPHandler(SimpleHTTPRequestHandler):
    """Manejador HTTP para la API del cerebro, streaming SSE y archivos estáticos WebGL."""

    vault_dir: Path = VAULT_DEFAULT
    web_dir: Path = Path(__file__).parent / "web"
    cached_graph: dict | None = None

    def translate_path(self, path: str) -> str:
        """Sirve archivos estáticos desde src/web/."""
        parsed = urlparse(path).path
        if parsed == "/" or parsed == "/index.html":
            return str(self.web_dir / "index.html")
        clean_name = parsed.lstrip("/")
        candidate = self.web_dir / clean_name
        if candidate.exists() and candidate.is_file():
            return str(candidate)
        return str(self.web_dir / "index.html")

    def do_GET(self) -> None:
        AutoSleepEngine.get_instance(self.vault_dir).record_activity()
        parsed = urlparse(self.path)

        if parsed.path == "/api/events":
            self._handle_sse_stream()
        elif parsed.path == "/api/graph":
            self._handle_graph_api()
        elif parsed.path == "/api/health":
            self._handle_health_api()
        elif parsed.path == "/api/stats":
            self._handle_stats_api()
        elif parsed.path == "/api/note":
            self._handle_note_api(parsed)
        elif parsed.path == "/api/sleep/status":
            self._handle_sleep_status_api()
        else:
            super().do_GET()

    def do_POST(self) -> None:
        AutoSleepEngine.get_instance(self.vault_dir).record_activity()
        parsed = urlparse(self.path)
        if parsed.path == "/api/hook":
            self._handle_incoming_hook()
        elif parsed.path == "/api/sleep":
            self._handle_sleep_api()
        elif parsed.path == "/api/sleep/toggle":
            self._handle_sleep_toggle_api()
        elif parsed.path == "/api/chat":
            self._handle_chat_api()
        elif parsed.path == "/api/compress":
            self._handle_compress_api()
        elif parsed.path == "/api/fix_link":
            self._handle_fix_link_api()
        elif parsed.path == "/api/create_note":
            self._handle_create_note_api()
        elif parsed.path == "/api/unlink":
            self._handle_unlink_api()
        elif parsed.path == "/api/fix_all":
            self._handle_fix_all_api()
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Ruta no encontrada")

    def _handle_sse_stream(self) -> None:
        """Transmite eventos SSE en tiempo real leyendo live_events.jsonl."""
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        # Enviar mensaje de bienvenida / sincronización inicial
        init_payload = {
            "type": "welcome",
            "message": "DevBrain Cortex SSE conectado a 60 FPS",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.wfile.write(f"data: {json.dumps(init_payload)}\n\n".encode("utf-8"))
        self.wfile.flush()

        # Posición inicial en live_events.jsonl
        last_pos = 0
        if EVENTS_FILE.exists():
            try:
                # Iniciar leyendo las últimas 15 líneas
                with open(EVENTS_FILE, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    last_pos = f.tell()
                    for line in lines[-10:]:
                        clean = line.strip()
                        if clean:
                            self.wfile.write(f"data: {clean}\n\n".encode("utf-8"))
                    self.wfile.flush()
            except Exception:
                pass

        # Bucle de cola reactivo
        try:
            while True:
                time.sleep(0.1)
                if EVENTS_FILE.exists():
                    try:
                        with open(EVENTS_FILE, "r", encoding="utf-8", errors="ignore") as f:
                            f.seek(last_pos)
                            new_lines = f.readlines()
                            last_pos = f.tell()
                            for line in new_lines:
                                clean = line.strip()
                                if clean:
                                    self.wfile.write(f"data: {clean}\n\n".encode("utf-8"))
                                    self.wfile.flush()
                    except Exception:
                        pass
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _handle_graph_api(self) -> None:
        """Devuelve el grafo 3D completo de neuronas y sinapsis en formato JSON."""
        if CortexHTTPHandler.cached_graph is None:
            # Descubrir notas reales del Vault
            real_notes = []
            hk = CortexHousekeeper(self.vault_dir)
            discovered = hk._discover_all_notes()
            for name, path in list(discovered.items()):
                real_notes.append({"title": path.stem, "id": path.stem})

            CortexHTTPHandler.cached_graph = BrainMorphologyGenerator.generate_brain_cloud(
                real_notes=real_notes,
                target_total=19000
            )

        resp = json.dumps(CortexHTTPHandler.cached_graph).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(resp)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(resp)

    def _handle_health_api(self) -> None:
        hk = CortexHousekeeper(self.vault_dir)
        report = hk.audit_cortex_health(auto_prune=False)
        resp = json.dumps(report).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(resp)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(resp)

    def _handle_sleep_api(self) -> None:
        hk = CortexHousekeeper(self.vault_dir)
        report = hk.consolidate_dream_cycle()
        # Registrar evento en live_events para que el visualizador reaccione
        self._record_live_event("sleep_mode", report)
        resp = json.dumps(report).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(resp)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(resp)

    def _handle_stats_api(self) -> None:
        stats = {
            "uptime_seconds": time.time(),
            "vault_dir": str(self.vault_dir),
            "events_path": str(EVENTS_FILE),
            "port": DEFAULT_PORT,
            "sse_active": True
        }
        resp = json.dumps(stats).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(resp)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(resp)

    def _handle_note_api(self, parsed) -> None:
        """Devuelve el contenido markdown real, enlaces wikilinks y sinapsis de una nota."""
        qs = parse_qs(parsed.query)
        note_id = qs.get("id", [""])[0].strip()
        if not note_id:
            self.send_error(HTTPStatus.BAD_REQUEST, "Parámetro 'id' requerido")
            return

        hk = CortexHousekeeper(self.vault_dir)
        discovered = hk._discover_all_notes()
        path = discovered.get(note_id.lower())

        if not path or not path.exists():
            # Buscar por coincidencia aproximada
            for k, p in discovered.items():
                if note_id.lower() in k or k in note_id.lower():
                    path = p
                    break

        if not path or not path.exists():
            self.send_error(HTTPStatus.NOT_FOUND, f"Nota '{note_id}' no encontrada en el Vault")
            return

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, f"Error leyendo nota: {e}")
            return

        # Extraer enlaces wikilinks [[...]]
        raw_links = re.findall(r"\[\[(.*?)\]\]", content)
        links = []
        for l in raw_links:
            t = l.split("|")[0].split("#")[0].strip()
            if t and t not in links:
                links.append(t)

        # Consultar sinapsis Hebbianas en SQLite
        synapses = []
        try:
            if hk.db_path.exists():
                from neuroplasticity import SynapticEngine
                eng = SynapticEngine(hk.db_path)
                synapses = eng.get_associated_nodes(note_id.lower(), limit=10)
        except Exception:
            pass

        try:
            rel_path = str(path.relative_to(self.vault_dir))
        except Exception:
            rel_path = str(path)

        note_data = {
            "id": note_id,
            "title": path.stem,
            "rel_path": rel_path,
            "content": content[:60000],  # Hasta 60k caracteres
            "size_chars": len(content),
            "links": links,
            "synapses": synapses,
            "obsidian_uri": f"obsidian://open?vault={self.vault_dir.name}&file={rel_path}"
        }

        resp = json.dumps(note_data).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(resp)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(resp)

    def _handle_chat_api(self) -> None:
        """Procesa una consulta en lenguaje natural con DevBrainAgent y emite sinapsis activadas."""
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8", errors="replace")
            data = json.loads(body)
            prompt = data.get("message", "").strip()
            if not prompt:
                self.send_error(HTTPStatus.BAD_REQUEST, "Mensaje vacío")
                return

            from agentic_engine import DevBrainAgent
            agent = DevBrainAgent()
            res = agent.process_prompt(prompt)

            event_payload = {
                "type": "agent_chat",
                "prompt": prompt,
                "response": res.content,
                "intent": res.intent,
                "tools_called": res.tools_called,
                "synapses_fired": res.synapses_fired,
                "latency_ms": res.latency_ms,
                "tokens_in": res.tokens_in,
                "tokens_out": res.tokens_out,
                "plc_route": res.plc_route,
                "provider": res.provider_used,
                "thought_trace": res.thought_trace,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            self._record_live_event("agent_chat", event_payload)

            resp = json.dumps(event_payload).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(resp)
        except Exception as e:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, f"Error en chat agéntico: {e}")

    def _handle_compress_api(self) -> None:
        """Ejecuta el Token Budget Optimizer (AST slicing, chunking o deduplicación)."""
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8", errors="replace")
            data = json.loads(body)
            text = data.get("text", "")
            mode = data.get("mode", "code")
            tokens = int(data.get("tokens", 450))
            lang = data.get("language", "auto")
            focus = data.get("focus", "")

            from token_optimizer import TokenOptimizer
            opt = TokenOptimizer()
            if mode == "knowledge":
                res = opt.optimize_knowledge_chunks(text, topic=focus, max_tokens=tokens)
            elif mode == "session":
                res = opt.deduplicate_session_context(text, session_id="web-playground")
            else:
                res = opt.optimize_code_context(text, language=lang, max_tokens=tokens, focus_symbol=focus)

            resp = json.dumps(res).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(resp)
        except Exception as e:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, f"Error en compresión de tokens: {e}")

    def _handle_fix_link_api(self) -> None:
        """Repara automáticamente un enlace roto en el archivo markdown correspondiente."""
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8", errors="replace")
            data = json.loads(body)
            source = data.get("source_note", "").strip()
            broken = data.get("broken_target", "").strip()
            fix = data.get("suggested_fix", "").strip()

            if not source or not broken or not fix:
                self.send_error(HTTPStatus.BAD_REQUEST, "Parámetros incompletos (source_note, broken_target, suggested_fix)")
                return

            hk = CortexHousekeeper(self.vault_dir)
            discovered = hk._discover_all_notes()
            path = discovered.get(source.lower())
            if not path or not path.exists():
                self.send_error(HTTPStatus.NOT_FOUND, f"Nota fuente '{source}' no encontrada en el Vault")
                return

            content = path.read_text(encoding="utf-8", errors="replace")
            pattern = re.compile(rf"\[\[{re.escape(broken)}(\|[a-zA-Z0-9_\-\s]+)?\]\]")
            def replacer(m):
                alias = m.group(1) or ""
                return f"[[{fix}{alias}]]"

            new_content, count = pattern.subn(replacer, content)
            if count > 0:
                path.write_text(new_content, encoding="utf-8")
                self._record_live_event("fix_link", {
                    "source": source,
                    "broken": broken,
                    "fix": fix,
                    "count": count
                })
                resp = json.dumps({"status": "ok", "message": f"Reparado: {count} enlace(s) a [[{fix}]] en {source}", "count": count}).encode("utf-8")
            else:
                resp = json.dumps({"status": "warn", "message": f"No se encontró el enlace exacto [[{broken}]] en {source}", "count": 0}).encode("utf-8")

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(resp)
        except Exception as e:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, f"Error reparando enlace: {e}")

    def _handle_create_note_api(self) -> None:
        """Crea una nota conceptual vacía en el Vault para resolver un enlace roto."""
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8", errors="replace")
            data = json.loads(body)
            note_name = data.get("note_name", "").strip()
            folder = data.get("folder", "03-CONOCIMIENTO").strip()

            if not note_name:
                self.send_error(HTTPStatus.BAD_REQUEST, "Parámetro 'note_name' requerido")
                return

            hk = CortexHousekeeper(self.vault_dir)
            result = hk.create_missing_note(note_name, folder)
            self._record_live_event("create_note", result)

            resp = json.dumps(result).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(resp)
        except Exception as e:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, f"Error creando nota: {e}")

    def _handle_unlink_api(self) -> None:
        """Convierte un enlace roto a texto plano en el archivo fuente."""
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8", errors="replace")
            data = json.loads(body)
            source = data.get("source_note", "").strip()
            broken = data.get("broken_target", "").strip()

            if not source or not broken:
                self.send_error(HTTPStatus.BAD_REQUEST, "Parámetros 'source_note' y 'broken_target' requeridos")
                return

            hk = CortexHousekeeper(self.vault_dir)
            result = hk.unlink_broken_link(source, broken)
            self._record_live_event("unlink", result)

            resp = json.dumps(result).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(resp)
        except Exception as e:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, f"Error desvinculando enlace: {e}")

    def _handle_fix_all_api(self) -> None:
        """Repara automáticamente en lote todos los enlaces con sugerencias de alta confianza."""
        try:
            hk = CortexHousekeeper(self.vault_dir)
            result = hk.batch_fix_all_suggestions()
            self._record_live_event("batch_fix_links", result)

            resp = json.dumps(result).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(resp)
        except Exception as e:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, f"Error en reparación por lotes: {e}")

    def _handle_sleep_status_api(self) -> None:
        """Devuelve el estado de automatización del ciclo de sueño por inactividad."""
        engine = AutoSleepEngine.get_instance(self.vault_dir)
        status = engine.get_status()
        resp = json.dumps(status).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(resp)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(resp)

    def _handle_sleep_toggle_api(self) -> None:
        """Permite activar/desactivar o ajustar el umbral de inactividad del auto-sueño."""
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8", errors="replace")
            data = json.loads(body)
            engine = AutoSleepEngine.get_instance(self.vault_dir)
            if "enabled" in data:
                engine.enabled = bool(data["enabled"])
            if "idle_minutes" in data:
                engine.idle_minutes = max(1, int(data["idle_minutes"]))
            resp = json.dumps(engine.get_status()).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(resp)
        except Exception as e:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, f"Error actualizando auto-sueño: {e}")

    def _handle_incoming_hook(self) -> None:
        """Recibe payloads de hooks de Claude Code, Antigravity o Cursor."""
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8", errors="ignore")
            data = json.loads(body)
            self._record_live_event(data.get("type", "agent_action"), data)
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        except Exception as e:
            self.send_error(HTTPStatus.BAD_REQUEST, str(e))

    def _record_live_event(self, event_type: str, data: Any) -> None:
        try:
            EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
            record = {
                "type": event_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": data
            }
            with open(EVENTS_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception:
            pass


def start_cortex_server(
    port: int = DEFAULT_PORT,
    vault_dir: Path | None = None,
    open_browser: bool = True
) -> ThreadingHTTPServer:
    """Inicia el servidor local del cortex en un hilo o proceso dedicado."""
    v_dir = Path(vault_dir).resolve() if vault_dir else VAULT_DEFAULT
    CortexHTTPHandler.vault_dir = v_dir

    # Inicializar motor de auto-sueño biológico en segundo plano
    auto_sleep = AutoSleepEngine.get_instance(v_dir)

    server_address = ("127.0.0.1", port)
    httpd = ThreadingHTTPServer(server_address, CortexHTTPHandler)

    url = f"http://localhost:{port}"
    sys.stdout.write(f"\n🧠 [DevBrain Cortex 3D] Servidor WebGL + SSE activo en: {url}\n")
    sys.stdout.write("   • 19.000 neuronas y fibras sincronizadas localmente (60 FPS)\n")
    sys.stdout.write("   • Transmisión SSE de pensamientos en vivo en /api/events\n")
    sys.stdout.write("   • 100% privado y seguro (cero llamadas externas)\n\n")

    if open_browser:
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            pass

    return httpd


def run_server(
    port: int = DEFAULT_PORT,
    vault_dir: Path | None = None,
    open_browser: bool = False
) -> None:
    """Inicia el servidor Cortex y bloquea el hilo principal atendiendo peticiones hasta Ctrl+C."""
    srv = start_cortex_server(port=port, vault_dir=vault_dir, open_browser=open_browser)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        sys.stdout.write("\n[DevBrain] Cerrando servidor Cortex...\n")
    finally:
        try:
            srv.shutdown()
            srv.server_close()
        except Exception:
            pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="DevBrain Cortex 3D WebGL & SSE Server")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Puerto HTTP local")
    parser.add_argument("--vault", type=str, default="", help="Ruta al Vault de Obsidian")
    parser.add_argument("--no-open", action="store_true", help="No abrir automáticamente el navegador")
    args = parser.parse_args()

    v_path = Path(args.vault) if args.vault else VAULT_DEFAULT
    run_server(port=args.port, vault_dir=v_path, open_browser=not args.no_open)
