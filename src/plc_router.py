"""DevBrain PLC Router v1.0 — Controlador Lógico Programable
Clasifica peticiones MCP y las enruta al procesador más eficiente.

La metáfora PLC (Programmable Logic Controller): DevBrain actúa como un
controlador rápido que clasifica y enruta peticiones. Si la petición
es rápida (estado, memoria), se procesa localmente en DevBrain. Si
es pesada o de orquestación, se delega a Gentle-PI/Shell para su ejecución.
"""

from __future__ import annotations

import os
import json
import time
from datetime import datetime, timezone

# Routing decisions (module-level for import convenience)
ROUTE_LOCAL = 'local'
ROUTE_DELEGATE = 'delegate'
ROUTE_ORCHESTRATE = 'orchestrate'

class PLCRouter:
    """Clase principal de enrutamiento PLC.
    
    Clasifica las herramientas de MCP en categorías y decide si deben ser
    ejecutadas localmente o delegadas a otro orquestador como Gentle-PI.
    """

    # Tools that DevBrain ALWAYS processes locally (fast path, < 50ms)
    LOCAL_FAST: set[str] = {
        'search_knowledge', 'recall_memory', 'remember_decision',
        'classify_odd_task', 'list_projects', 'get_project_context',
        'route_model_dispatch', 'get_spec_questions'
    }

    # Tools that CAN be delegated to Gentle-PI if available
    DELEGATABLE: set[str] = {
        'prepare_odd_task', 'reconcile_odd_resume',
        'sync_project_graph', 'query_code_graph',
        'package_project_context', 'audit_project_health',
        'generate_scaffold', 'propose_spec', 'validate_spec',
        'debate_project_feasibility', 'audit_ponytail_complexity'
    }

    # Tools that REQUIRE Gentle-PI for full orchestration
    REQUIRES_ORCHESTRATOR: set[str] = {
        'orchestrator_session_bridge',
        'prepare_sdd_preflight'
    }

    # Routing decisions as class constants
    ROUTE_LOCAL = ROUTE_LOCAL
    ROUTE_DELEGATE = ROUTE_DELEGATE
    ROUTE_ORCHESTRATE = ROUTE_ORCHESTRATE

    def __init__(self) -> None:
        """Inicializa el enrutador PLC."""
        self._gentle_pi_available: bool = False
        self._last_probe: float = 0.0
        self._probe_interval: float = 30.0

    def classify(self, tool_name: str) -> str:
        """Clasifica el nombre de una herramienta en una decisión de enrutamiento.
        
        Args:
            tool_name: Nombre de la herramienta.
            
        Returns:
            Una constante ROUTE_*. Si es desconocida, retorna ROUTE_LOCAL.
        """
        if tool_name in self.REQUIRES_ORCHESTRATOR:
            return ROUTE_ORCHESTRATE
        elif tool_name in self.DELEGATABLE:
            return ROUTE_DELEGATE
        # Cualquier otra herramienta o en LOCAL_FAST se procesa local
        return ROUTE_LOCAL

    def probe_gentle_pi(self) -> bool:
        """Realiza un chequeo ligero para ver si Gentle-PI está disponible.
        
        Usa caché si ha pasado menos tiempo que el intervalo de prueba.
        Revisa la existencia de la carpeta de configuración o pipes/sockets.
        
        Returns:
            True si Gentle-PI parece estar disponible, False de lo contrario.
        """
        current_time = time.time()
        if (current_time - self._last_probe) < self._probe_interval:
            return self._gentle_pi_available

        # Realizar prueba muy ligera (filesystem)
        # Revisar carpeta ~/.pi/gentle-ai/
        home_dir = os.path.expanduser('~')
        pi_dir = os.path.join(home_dir, '.pi', 'gentle-ai')
        
        # Consideramos disponible si el directorio existe
        is_available = os.path.exists(pi_dir) and os.path.isdir(pi_dir)
        
        self._gentle_pi_available = is_available
        self._last_probe = current_time
        
        return self._gentle_pi_available

    def route(self, tool_name: str, arguments: dict) -> dict:
        """Decide y formatea el enrutamiento principal de una petición.
        
        Args:
            tool_name: Nombre de la herramienta a enrutar.
            arguments: Argumentos de la herramienta.
            
        Returns:
            Diccionario con la acción y detalles de enrutamiento.
        """
        classification = self.classify(tool_name)
        
        if classification == ROUTE_LOCAL:
            return {'action': 'process_local', 'tool': tool_name, 'args': arguments}
            
        elif classification == ROUTE_ORCHESTRATE:
            # Requiere orquestador. Verificamos si Gentle-PI está.
            if self.probe_gentle_pi():
                return {
                    'action': 'delegate_gentle_pi',
                    'tool': tool_name,
                    'args': arguments,
                    'delegation_payload': self.format_delegation_payload(tool_name, arguments)
                }
            else:
                # No podemos procesar esto localmente bien, pero Gentle-PI no está.
                # Intentamos fallback local o informamos error.
                return {'action': 'process_local', 'tool': tool_name, 'args': arguments, 'fallback': True}
                
        elif classification == ROUTE_DELEGATE:
            # Puede ser delegada.
            if self.probe_gentle_pi():
                return {
                    'action': 'delegate_gentle_pi',
                    'tool': tool_name,
                    'args': arguments,
                    'delegation_payload': self.format_delegation_payload(tool_name, arguments)
                }
            else:
                # Fallback a local si Gentle-PI no está
                return {'action': 'process_local', 'tool': tool_name, 'args': arguments, 'fallback': True}
                
        return {'action': 'process_local', 'tool': tool_name, 'args': arguments}

    def format_delegation_payload(self, tool_name: str, arguments: dict) -> dict:
        """Formatea la petición como un payload de delegación de DevBrain.
        
        Args:
            tool_name: Nombre de la herramienta.
            arguments: Argumentos de la herramienta.
            
        Returns:
            Diccionario estructurado para la delegación inter-orquestador.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        return {
            'type': 'DEVBRAIN_DELEGATION',
            'source': 'devbrain-mcp',
            'tool': tool_name,
            'arguments': arguments,
            'timestamp': now_iso,
            'requires_ack': True
        }

    def get_routing_stats(self) -> dict:
        """Obtiene las estadísticas actuales del enrutador PLC.
        
        Returns:
            Diccionario con estadísticas de estado y disponibilidad.
        """
        last_probe_dt = datetime.fromtimestamp(self._last_probe, tz=timezone.utc) if self._last_probe > 0 else datetime.now(timezone.utc)
        return {
            'gentle_pi_available': self._gentle_pi_available,
            'last_probe': last_probe_dt.isoformat(),
            'local_tools': len(self.LOCAL_FAST),
            'delegatable_tools': len(self.DELEGATABLE),
            'orchestrator_tools': len(self.REQUIRES_ORCHESTRATOR)
        }


class GentlePIBridge:
    """Clase puente para la comunicación directa con Gentle-PI."""
    
    def __init__(self) -> None:
        """Inicializa el puente con Gentle-PI."""
        pass
        
    def is_available(self) -> bool:
        """Comprueba de forma ligera si la configuración de Gentle-PI existe.
        
        Returns:
            True si existe el directorio de configuración o el package.json.
        """
        home_dir = os.path.expanduser('~')
        
        # Verificar GENTLE_PI_CONFIG_HOME o ~/.pi/gentle-ai/
        config_home = os.environ.get('GENTLE_PI_CONFIG_HOME', os.path.join(home_dir, '.pi', 'gentle-ai'))
        
        if os.path.exists(config_home) and os.path.isdir(config_home):
            return True
            
        # Verificar package.json
        pkg_path = os.path.join(home_dir, '.pi', 'agent', 'npm', 'node_modules', 'gentle-pi', 'package.json')
        return os.path.exists(pkg_path) and os.path.isfile(pkg_path)
        
    def get_version(self) -> str | None:
        """Intenta leer la versión instalada de Gentle-PI desde package.json.
        
        Returns:
            Cadena de versión o None si no se pudo leer.
        """
        home_dir = os.path.expanduser('~')
        pkg_path = os.path.join(home_dir, '.pi', 'agent', 'npm', 'node_modules', 'gentle-pi', 'package.json')
        
        if os.path.exists(pkg_path) and os.path.isfile(pkg_path):
            try:
                with open(pkg_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('version')
            except Exception:
                return None
        return None
        
    def build_notification(self, session_id: str, target_session_id: str, payload: dict) -> str:
        """Construye un mensaje de notificación JSON estructurado.
        
        Args:
            session_id: ID de la sesión de origen (DevBrain).
            target_session_id: ID de la sesión destino (Gentle-PI).
            payload: Datos a enviar.
            
        Returns:
            Cadena JSON con el formato orchestrator_send_message.
        """
        message = {
            "action": "orchestrator_send_message",
            "source_session": session_id,
            "target_session": target_session_id,
            "payload": payload,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        return json.dumps(message)
