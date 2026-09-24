"""
DevBrain Agentic Engine (v1.0)
Motor de Agente Cognitivo en Lenguaje Natural al estilo OpenCode / Claude Code / Gentle-Shell:
- Clasificación heurística y semántica de intenciones (Consultas técnicas, ODD, Memoria, Arquitectura, Salud).
- Orquestación multi-herramienta con las 21 capacidades MCP de DevBrain.
- Activación dinámica de sinapsis neuronales según contexto (Regla de Hebb).
- Despacho dual: Gateway LLM (OmniRoute / OpenAI / Ollama / Anthropic) con fallback determinista 100% offline.
- Telemetría de tokens, latencia, throughput y traza de razonamiento en vivo.
"""
from __future__ import annotations
import sys
import os
import re
import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
import socket
from urllib.parse import urlparse

def is_endpoint_reachable(url: str, timeout: float = 0.05) -> bool:
    """Verifica si el host y puerto están escuchando en <50ms antes de intentar HTTP."""
    try:
        parsed = urlparse(url)
        host = parsed.hostname or "127.0.0.1"
        if host == "localhost":
            host = "127.0.0.1"
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

# Añadir src al path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from telemetry import TelemetryEngine
from cli_theme import ConfigManager, ThemeColors

@dataclass
class IntentResult:
    intent_type: str
    confidence: float
    detected_keywords: list[str] = field(default_factory=list)
    suggested_tools: list[str] = field(default_factory=list)
    context_type: str = "general"

@dataclass
class AgentResponse:
    content: str
    intent: str
    tools_called: list[str] = field(default_factory=list)
    synapses_fired: list[str] = field(default_factory=list)
    latency_ms: float = 0.0
    tokens_in: int = 0
    tokens_out: int = 0
    plc_route: str = "LOCAL_FAST"
    provider_used: str = "DevBrain-Cognitive-Engine (Offline)"
    thought_trace: str = ""

class DevBrainAgent:
    """Agente de desarrollo y arquitectura cognitiva para DevBrain CLI."""

    def __init__(self, config_mgr: ConfigManager | None = None):
        self.config_mgr = config_mgr or ConfigManager()
        self.theme = self.config_mgr.get_theme()
        self.telemetry = TelemetryEngine.get_instance()
        self.omni_route_url = os.getenv("OMNI_ROUTE_URL", "http://127.0.0.1:8000/v1")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")

    def classify_intent(self, prompt: str) -> IntentResult:
        """Clasifica la intención del usuario a partir de su prompt en lenguaje natural."""
        p_lower = prompt.lower().strip()
        words = set(re.findall(r"\w+", p_lower))

        # 1. ODD Task / Feature / Planning
        odd_keywords = {"tarea", "feature", "odd", "clasifica", "refactor", "refactorizar", "bug", "implementar",
                        "crear", "ticket", "tdd", "sdd", "backlog", "requisito", "requerimiento", "alcance"}
        odd_matches = [w for w in odd_keywords if w in p_lower]
        if any(trigger in p_lower for trigger in ["crear tarea", "nueva tarea", "clasifica esta", "clasificar", "quiero implementar", "vamos a programar", "refactor de"]):
            return IntentResult("ODD_TASK", 0.95, odd_matches, ["classify_odd_task", "prepare_odd_task"], "coding")
        if len(odd_matches) >= 2:
            return IntentResult("ODD_TASK", 0.85, odd_matches, ["classify_odd_task"], "coding")

        # 2. Decision Memory / Engram
        mem_keywords = {"decision", "decisión", "decisiones", "decidimos", "acordamos", "memoria", "engram",
                        "acuerdo", "guardar", "recuerda", "recordar", "directriz", "regla", "por qué usamos", "historico"}
        mem_matches = [w for w in mem_keywords if w in p_lower]
        if any(trigger in p_lower for trigger in ["qué decidimos", "que decidimos", "por qué se eligió", "recuerda que", "guardar memoria", "decisiones sobre", "en memoria"]):
            return IntentResult("DECISION_MEMORY", 0.95, mem_matches, ["recall_memory"], "memory")
        if len(mem_matches) >= 2:
            return IntentResult("DECISION_MEMORY", 0.80, mem_matches, ["recall_memory"], "memory")

        # 3. System Health / Doctor
        health_keywords = {"salud", "doctor", "diagnóstico", "diagnostico", "chequeo", "verificar"}
        health_matches = [w for w in health_keywords if w in p_lower]
        if any(trigger in p_lower for trigger in ["salud", "doctor", "diagnóstico", "diagnostico", "chequeo"]) or (any(w in p_lower for w in ["revisar", "cómo está", "estado"]) and any(w in p_lower for w in ["sistema", "entorno", "proyecto", "devbrain"])):
            return IntentResult("HEALTH_DOCTOR", 0.95, health_matches or ["salud"], ["audit_project_health"], "diagnostic")

        # 4. OpenSpec / Architecture Spec
        spec_keywords = {"spec", "openspec", "especificacion", "especificación", "contrato", "schema", "esquema", "propose_spec", "api"}
        spec_matches = [w for w in spec_keywords if w in p_lower]
        if any(trigger in p_lower for trigger in ["crear spec", "generar spec", "diseño de api", "contrato de datos"]):
            return IntentResult("SPEC_ARCHITECTURE", 0.90, spec_matches, ["propose_spec", "get_spec_questions"], "architecture")

        # 5. Debate / Feasibility
        debate_keywords = {"debate", "debatir", "conviene", "pros", "contras", "factibilidad", "alternativas", "comparar", "mejor opción", "migrar a"}
        debate_matches = [w for w in debate_keywords if w in p_lower]
        if any(trigger in p_lower for trigger in ["es mejor", "conviene usar", "debemos migrar", "pros y contras", "factibilidad de", "debatir si"]):
            return IntentResult("DEBATE_FEASIBILITY", 0.90, debate_matches, ["debate_project_feasibility", "search_knowledge"], "architecture")

        # 6. Technical Knowledge Query (Default para preguntas arquitectónicas y conceptuales)
        tech_keywords = {"como", "cómo", "qué", "que", "explicar", "explica", "patrón", "patron", "arquitectura",
                         "neuroplasticidad", "sinapsis", "plc", "gentle", "vault", "obsidian", "fts5", "rerank"}
        tech_matches = [w for w in tech_keywords if w in p_lower]
        if any(p_lower.startswith(w) for w in ["cómo", "como", "qué", "que", "cuál", "cual", "dónde", "donde", "explica", "describe", "busca"]):
            return IntentResult("KNOWLEDGE_QUERY", 0.90, tech_matches, ["search_knowledge", "recall_memory"], "investigation")

        return IntentResult("KNOWLEDGE_QUERY", 0.70, list(words)[:4], ["search_knowledge"], "general")

    def _query_external_llm(self, prompt: str, system_context: str) -> str | None:
        """Intenta consultar un LLM local o remoto (OmniRoute, Ollama, OpenAI-compatible)."""
        messages = [
            {"role": "system", "content": system_context},
            {"role": "user", "content": prompt}
        ]

        # 1. Probar OmniRoute / OpenAI endpoint compatible si el socket está abierto
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY") or os.getenv("GEMINI_API_KEY") or "devbrain-local"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        # Intentar OmniRoute local o endpoint personalizado
        for endpoint in [self.omni_route_url, "http://localhost:11434/v1"]:
            if not endpoint or not is_endpoint_reachable(endpoint, timeout=0.08):
                continue
            payload = json.dumps({
                "model": os.getenv("DEVBRAIN_MODEL", "gemini-2.5-flash"),
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": 1500
            }).encode("utf-8")

            try:
                req = urllib.request.Request(f"{endpoint.rstrip('/')}/chat/completions", data=payload, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=0.8) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        choices = data.get("choices", [])
                        if choices:
                            return choices[0].get("message", {}).get("content", "").strip()
            except Exception:
                pass

        # 2. Intentar Ollama nativo si el socket está abierto
        if self.ollama_url and is_endpoint_reachable(self.ollama_url, timeout=0.08):
            try:
                ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
                payload = json.dumps({
                    "model": ollama_model,
                    "prompt": f"{system_context}\n\nUsuario: {prompt}\nAsistente:",
                    "stream": False
                }).encode("utf-8")
                req = urllib.request.Request(f"{self.ollama_url.rstrip('/')}/api/generate", data=payload, headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(req, timeout=0.8) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        ans = data.get("response", "").strip()
                        if ans:
                            return ans
            except Exception:
                pass

        return None

    def synthesize_deterministic_response(self, prompt: str, intent_res: IntentResult, tool_data: dict, synapses: list[str]) -> str:
        """Sintetiza una respuesta estructurada de alta fidelidad cuando no hay LLM externo."""
        intent = intent_res.intent_type
        sections = []

        # 1. Encabezado Cognitivo
        sections.append(f"### 🤖 DevBrain Cognitive Synthesis\n")

        # 2. Respuesta según intención
        if intent == "ODD_TASK":
            odd_res = tool_data.get("classify_odd_task", "")
            sections.append(odd_res)
            sections.append("\n**Siguientes Pasos Sugeridos**:")
            sections.append("- Para generar el documento de trabajo formal: usa `/feature <nombre> | <objetivo>` o solicítamelo con el nombre de la feature.")
            sections.append("- Recuerda la regla ODD: ~400 líneas modificadas por tarea es una guía de carga cognitiva, nunca un corte burocrático forzado.")

        elif intent == "DECISION_MEMORY":
            mem_res = tool_data.get("recall_memory", "")
            sections.append(mem_res)
            sections.append("\n**Directriz de Memoria**:")
            sections.append("- Todas las decisiones persistidas se sincronizan bidireccionalmente entre el Vault de Obsidian (`04-MEMORIA/decisiones/`) y el espejo Engram.")
            sections.append("- Para registrar un nuevo acuerdo arquitectónico: escribe `/remember <título> | <detalle>`.")

        elif intent == "HEALTH_DOCTOR":
            health_res = tool_data.get("audit_project_health", "")
            sections.append(health_res)

        elif intent == "SPEC_ARCHITECTURE":
            sections.append("#### 📐 Arquitectura OpenSpec & Contratos de Integración\n")
            spec_res = tool_data.get("propose_spec", "")
            if spec_res:
                sections.append(spec_res)
            else:
                sections.append("- **Directriz SDD**: Las especificaciones se redactan en `openspec/specs/<feature>/` conteniendo `proposal.md`, `spec.md`, `design.md` y `tasks.md`.")
                sections.append("- SDD es opcional y liviano: úsalo cuando múltiples componentes o APIs públicas deban acordar esquemas antes de codificar.")

        elif intent == "DEBATE_FEASIBILITY":
            debate_res = tool_data.get("debate_project_feasibility", "")
            sections.append(debate_res)

        else: # KNOWLEDGE_QUERY / GENERAL
            knowledge_res = tool_data.get("search_knowledge", "")
            mem_res = tool_data.get("recall_memory", "")
            
            sections.append(f"**Respuesta al requerimiento**: *\"{prompt}\"*\n")
            
            if knowledge_res and "No se encontraron" not in knowledge_res:
                sections.append("#### 📚 Conocimiento Técnico Relacionado:\n")
                sections.append(knowledge_res)
            else:
                sections.append("No se localizó una nota idéntica por coincidencia léxica exacta, pero he indexado los términos clave en el cortex neuronal.")

            if mem_res and "No se encontraron" not in mem_res:
                sections.append("\n#### 🧠 Antecedentes en Memoria & Decisiones:\n")
                sections.append(mem_res)

            # Extraer enlaces wiki encontrados
            found_wikilinks = re.findall(r"\[\[(.*?)\]\]", knowledge_res + mem_res)
            if found_wikilinks:
                unique_nodes = list(dict.fromkeys(found_wikilinks))[:6]
                links_str = " • ".join(f"`[[{node}]]`" for node in unique_nodes)
                sections.append(f"\n**Nodos Sinápticos Conectados**: {links_str}")

        # 3. Pie de estado de neuroplasticidad
        if synapses:
            syn_str = " ──⚡──► ".join(f"`⬡ {s}`" for s in synapses[:4])
            sections.append(f"\n> [!NOTE]\n> **Corteza Sináptica Activa**: {syn_str} (Regla de Hebb aplicada).")

        return "\n\n".join(sections)

    def process_prompt(self, user_prompt: str) -> AgentResponse:
        """
        Orquesta el ciclo cognitivo completo para un prompt en lenguaje natural:
        1. Clasificación de intención.
        2. Recolección de contexto vía herramientas MCP.
        3. Estimulación del grafo sináptico (neuroplasticidad).
        4. Despacho a LLM Gateway u orquestación local determinista.
        5. Medición de telemetría y emisión de evento live.
        """
        start_time = time.time()
        prompt = user_prompt.strip()

        # 1. Clasificación de Intención
        intent_res = self.classify_intent(prompt)
        tools_called = []
        tool_data = {}
        synapses_fired = []

        # Importar dinámicamente handlers de devbrain_mcp
        try:
            import devbrain_mcp as mcp
        except Exception:
            mcp = None

        # 2. Invocación de herramientas según intención
        if mcp:
            current_session = getattr(mcp, "CURRENT_SESSION_ID", "agentic-session")
            syn_engine = getattr(mcp, "SYNAPSE_ENGINE", None)

            # Activar sinapsis para las palabras clave detectadas
            if syn_engine and intent_res.detected_keywords:
                for kw in intent_res.detected_keywords[:3]:
                    try:
                        syn_engine.record_activation(kw, context_type=intent_res.context_type, session_id=current_session)
                        synapses_fired.append(kw)
                    except Exception:
                        pass

            # Ejecutar herramientas requeridas
            for tool_name in intent_res.suggested_tools:
                try:
                    if tool_name == "search_knowledge" and hasattr(mcp, "handle_search_knowledge"):
                        tools_called.append("search_knowledge")
                        tool_data["search_knowledge"] = mcp.handle_search_knowledge({"query": prompt, "limit": 4})
                    elif tool_name == "recall_memory" and hasattr(mcp, "handle_recall_memory"):
                        tools_called.append("recall_memory")
                        tool_data["recall_memory"] = mcp.handle_recall_memory({"query": prompt})
                    elif tool_name == "classify_odd_task" and hasattr(mcp, "handle_classify_odd_task"):
                        tools_called.append("classify_odd_task")
                        tool_data["classify_odd_task"] = mcp.handle_classify_odd_task({"request_description": prompt})
                    elif tool_name == "audit_project_health" and hasattr(mcp, "handle_audit_project_health"):
                        tools_called.append("audit_project_health")
                        tool_data["audit_project_health"] = mcp.handle_audit_project_health({})
                    elif tool_name == "debate_project_feasibility" and hasattr(mcp, "handle_debate_project_feasibility"):
                        tools_called.append("debate_project_feasibility")
                        tool_data["debate_project_feasibility"] = mcp.handle_debate_project_feasibility({"topic": prompt})
                    elif tool_name == "propose_spec" and hasattr(mcp, "handle_propose_spec"):
                        tools_called.append("propose_spec")
                        tool_data["propose_spec"] = mcp.handle_propose_spec({"feature_name": prompt[:40]})
                except Exception as e:
                    tool_data[tool_name] = f"Error ejecutando {tool_name}: {e}"

            # Obtener nodos activos adicionales de la sesión
            if syn_engine:
                try:
                    session_nodes = syn_engine.get_session_nodes(current_session)
                    for n in session_nodes:
                        if n not in synapses_fired:
                            synapses_fired.append(n)
                except Exception:
                    pass

        # 3. Despacho a LLM Gateway si está disponible
        system_context = (
            "Eres DevBrain Agent v3.0, el controlador PLC y asistente de arquitectura técnica con neuroplasticidad dinámica.\n"
            "Tu misión es resolver la petición del usuario con alta precisión técnica, claridad y concisión, siguiendo la filosofía Gentle-AI y ODD.\n"
            f"Contexto de herramientas DevBrain:\n{json.dumps(tool_data, ensure_ascii=False, indent=2)}\n"
            f"Sinapsis activas: {', '.join(synapses_fired)}"
        )

        llm_response = self._query_external_llm(prompt, system_context)
        if llm_response:
            final_content = llm_response
            provider = "LLM Gateway (OmniRoute / Provider)"
        else:
            final_content = self.synthesize_deterministic_response(prompt, intent_res, tool_data, synapses_fired)
            provider = "DevBrain-Cognitive-Engine (Offline Heuristic)"

        # 4. Cálculo de Telemetría
        latency_ms = (time.time() - start_time) * 1000.0
        # Estimación de tokens: ~1.3 tokens por palabra en español
        prompt_words = len(prompt.split()) + len(system_context.split())
        completion_words = len(final_content.split())
        tokens_in = int(prompt_words * 1.3)
        tokens_out = int(completion_words * 1.3)

        plc_route = "LOCAL_FAST"
        if "classify_odd_task" in tools_called or "propose_spec" in tools_called:
            plc_route = "DELEGATABLE"

        thought_trace = (
            f"Intención: {intent_res.intent_type} (confianza: {intent_res.confidence:.2f}) • "
            f"Herramientas: {', '.join(tools_called) or 'direct'} • "
            f"Sinapsis: {len(synapses_fired)} nodos • "
            f"Proveedor: {provider}"
        )

        # 5. Registrar evento en vivo en TelemetryEngine
        try:
            self.telemetry.record_event(
                tool_name="agentic_prompt",
                input_data={"prompt": prompt, "intent": intent_res.intent_type},
                output_data=final_content,
                latency_ms=latency_ms,
                plc_route=plc_route,
                synapses_fired=synapses_fired,
                thought_trace=thought_trace
            )
        except Exception:
            pass

        return AgentResponse(
            content=final_content,
            intent=intent_res.intent_type,
            tools_called=tools_called,
            synapses_fired=synapses_fired,
            latency_ms=latency_ms,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            plc_route=plc_route,
            provider_used=provider,
            thought_trace=thought_trace
        )
