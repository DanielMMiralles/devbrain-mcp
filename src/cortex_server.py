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

from cortex_housekeeper import CortexHousekeeper

DEFAULT_PORT = 8765
VAULT_DEFAULT = Path(r"C:\Users\damm1\OneDrive\Documentos\Obsidian Vault")
EVENTS_FILE = Path(os.path.expanduser("~")) / ".devbrain" / "live_events.jsonl"


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
        parsed = urlparse(self.path)

        if parsed.path == "/api/events":
            self._handle_sse_stream()
        elif parsed.path == "/api/graph":
            self._handle_graph_api()
        elif parsed.path == "/api/health":
            self._handle_health_api()
        elif parsed.path == "/api/stats":
            self._handle_stats_api()
        else:
            super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/hook":
            self._handle_incoming_hook()
        elif parsed.path == "/api/sleep":
            self._handle_sleep_api()
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
            for name, path in list(discovered.items())[:3000]:
                real_notes.append({"title": path.stem, "id": path.stem})

            CortexHTTPHandler.cached_graph = BrainMorphologyGenerator.generate_brain_cloud(
                real_notes=real_notes,
                target_total=19000
            )

        resp = json.dumps(CortexHTTPHandler.cached_graph).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(resp)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(resp)

    def _handle_health_api(self) -> None:
        hk = CortexHousekeeper(self.vault_dir)
        report = hk.audit_cortex_health(auto_prune=False)
        resp = json.dumps(report).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
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
        self.send_header("Content-Type", "application/json")
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
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(resp)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(resp)

    def _handle_incoming_hook(self) -> None:
        """Recibe payloads de hooks de Claude Code, Antigravity o Cursor."""
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8", errors="ignore")
            data = json.loads(body)
            self._record_live_event(data.get("type", "agent_action"), data)
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
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
    if vault_dir:
        CortexHTTPHandler.vault_dir = Path(vault_dir).resolve()

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


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="DevBrain Cortex 3D WebGL & SSE Server")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Puerto HTTP local")
    parser.add_argument("--vault", type=str, default="", help="Ruta al Vault de Obsidian")
    parser.add_argument("--no-open", action="store_true", help="No abrir automáticamente el navegador")
    args = parser.parse_args()

    v_path = Path(args.vault) if args.vault else VAULT_DEFAULT
    srv = start_cortex_server(port=args.port, vault_dir=v_path, open_browser=not args.no_open)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        sys.stdout.write("\nCerrando servidor Cortex...\n")
        srv.server_close()
