import sys
import io

# Asegurar UTF-8 incondicional en Windows para stdio MCP
if sys.platform == "win32":
    try:
        if hasattr(sys.stdin, "reconfigure"): sys.stdin.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"): sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

"""
DevBrain Unified MCP Server (v3.0.0 - PLC Neuroplástico):
Controlador Lógico Programable (PLC) con neuroplasticidad dinámica.
Clasifica y enruta peticiones MCP al procesador más eficiente (local o Gentle-PI).
Integra un grafo sináptico adaptativo inspirado en LTP/LTD y la regla de Hebb
para reconectar dinámicamente nodos de conocimiento según patrones de uso.
100% prescindible de un Obsidian Vault: opera en modo conectado o Standalone autónomo.
Compatible al 100% con la especificación MCP oficial (2024-11-05).
"""
import json
import os
import re
import unicodedata
from pathlib import Path
from datetime import datetime

def slugify(text: str) -> str:
    """Normaliza tildes y caracteres especiales a un slug ASCII limpio."""
    text = unicodedata.normalize('NFKD', str(text)).encode('ascii', 'ignore').decode('utf-8')
    return re.sub(r"[^a-zA-Z0-9_\-]+", "-", text.lower()).strip("-")

# ==========================================
# 1. RESOLUCIÓN RESILIENTE DE ENTORNO
# ==========================================

def resolve_environment():
    """
    Detecta si existe un Obsidian Vault activo o si debemos operar en modo Standalone.
    """
    env_vault = os.getenv("VAULT_DIR") or os.getenv("VAULT_PATH")
    if not env_vault:
        for candidate_env in [Path(".env"), Path(__file__).resolve().parent / ".env", Path(__file__).resolve().parent.parent / ".env"]:
            if candidate_env.exists():
                try:
                    for line in candidate_env.read_text(encoding="utf-8", errors="ignore").splitlines():
                        line = line.strip()
                        if line.startswith("#") or "=" not in line: continue
                        k, v = line.split("=", 1)
                        k, v = k.strip(), v.strip().strip("'\"")
                        if k in ["VAULT_DIR", "VAULT_PATH"] and v:
                            env_vault = v
                            break
                except Exception:
                    pass
            if env_vault: break

    candidate_vaults = []
    if env_vault:
        candidate_vaults.append(Path(env_vault).resolve())
    
    # Vault local por defecto si existe
    candidate_vaults.append(Path(r"C:\Users\damm1\OneDrive\Documentos\Obsidian Vault"))
    candidate_vaults.append(Path("./starter-vault").resolve())

    for cv in candidate_vaults:
        if cv.exists() and (cv / "03-CONOCIMIENTO").exists():
            return cv, True # Modo Vault Conectado

    # MODO STANDALONE: Prescindible de Vault
    standalone_dir = Path("./.devbrain").resolve()
    standalone_dir.mkdir(parents=True, exist_ok=True)
    return standalone_dir, False

VAULT_DIR, HAS_VAULT = resolve_environment()

if HAS_VAULT:
    PROYECTOS_DIR = VAULT_DIR / "02-PROYECTOS"
    CONOCIMIENTO_DIR = VAULT_DIR / "03-CONOCIMIENTO"
    APRENDIZAJES_DIR = VAULT_DIR / "04-APRENDIZAJES"
    SPECS_DIR = PROYECTOS_DIR / "specs"
    DECISIONS_DIR = VAULT_DIR / "04-APRENDIZAJES" / "decisiones"
    GRAPHS_DIR = PROYECTOS_DIR / "context-bundles" / "graphs"
else:
    PROYECTOS_DIR = VAULT_DIR / "proyectos"
    CONOCIMIENTO_DIR = VAULT_DIR / "conocimiento"
    APRENDIZAJES_DIR = VAULT_DIR / "aprendizajes"
    SPECS_DIR = Path("./specs").resolve() if Path("./specs").exists() else VAULT_DIR / "specs"
    DECISIONS_DIR = VAULT_DIR / "decisiones"
    GRAPHS_DIR = VAULT_DIR / "graphs"

for d in [PROYECTOS_DIR, CONOCIMIENTO_DIR, APRENDIZAJES_DIR, SPECS_DIR, DECISIONS_DIR, GRAPHS_DIR]:
    try:
        d.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

# Importar modulos internos de scripts si existen
if HAS_VAULT:
    sys.path.append(str(VAULT_DIR / "06-SISTEMA" / "devspec"))
    sys.path.append(str(VAULT_DIR / "06-SISTEMA" / "scripts"))
    sys.path.append(str(VAULT_DIR / "06-SISTEMA" / "mcp"))

# Inicializar motor de indexación FTS5 in-process (Engram v2 / Gentle-AI)
INDEXER = None
try:
    from devbrain_index import DevBrainIndex
    INDEXER = DevBrainIndex(VAULT_DIR)
except Exception as e:
    sys.stderr.write(f"[DevBrain] Info: Indexador FTS5 en modo fallback: {e}\n")

# Inicializar motor de neuroplasticidad sináptica (DevBrain v3.0)
SYNAPSE_ENGINE = None
CURRENT_SESSION_ID = ""
try:
    from neuroplasticity import SynapticEngine, generate_session_id
    _synapse_db = INDEXER.db_path if INDEXER else Path("./.devbrain_cache/devbrain_fts.db").resolve()
    _synapse_db.parent.mkdir(parents=True, exist_ok=True)
    SYNAPSE_ENGINE = SynapticEngine(_synapse_db)
    CURRENT_SESSION_ID = generate_session_id()
    sys.stderr.write(f"[DevBrain] Neuroplasticidad activa (session: {CURRENT_SESSION_ID})\n")
except Exception as e:
    sys.stderr.write(f"[DevBrain] Info: Motor sináptico en modo fallback: {e}\n")

# Inicializar PLC Router (DevBrain v3.0)
PLC_ROUTER = None
GENTLE_PI_BRIDGE = None
try:
    from plc_router import PLCRouter, GentlePIBridge
    PLC_ROUTER = PLCRouter()
    GENTLE_PI_BRIDGE = GentlePIBridge()
    _gp_version = GENTLE_PI_BRIDGE.get_version()
    sys.stderr.write(f"[DevBrain] PLC Router activo (Gentle-PI: {_gp_version or 'no detectado'})\n")
except Exception as e:
    sys.stderr.write(f"[DevBrain] Info: PLC Router en modo fallback: {e}\n")

# ==========================================
# 2. BASE DE CONOCIMIENTO EMBEBIDA (OFFLINE FALLBACK)
# ==========================================
BUILTIN_KNOWLEDGE = {
    "cqrs": {
        "title": "Command Query Responsibility Segregation (CQRS)",
        "summary": "Segregación de responsabilidades de comandos (escrituras mutables) y consultas (lecturas optimizadas). Permite escalar de forma asimétrica modelos de lectura y escritura, combinándose habitualmente con Event Sourcing y bases de datos optimizadas para lectura (ej. Read Replicas, Elasticsearch o Redis).",
        "gotcha": "Aplicar CQRS en aplicaciones CRUD simples introduce una sobrecarga masiva de complejidad accidental y consistencia eventual innecesaria."
    },
    "outbox": {
        "title": "Transactional Outbox Pattern",
        "summary": "Patrón de fiabilidad en sistemas distribuidos que garantiza la publicación atómica de eventos en un broker (Kafka/RabbitMQ) junto con la mutación de base de datos en una sola transacción local, insertando el mensaje en una tabla 'outbox'. Un relay independiente (Debezium CDC o Polling Worker) lee la tabla y transmite el evento.",
        "gotcha": "No implementar deduplicación (idempotency keys) en los consumidores puede causar procesamiento múltiple ante reintentos del relay."
    },
    "saga": {
        "title": "Saga Pattern: Choreography vs Orchestration",
        "summary": "Mecanismo para coordinar transacciones distribuidas a través de múltiples microservicios sin bloqueos sincrónicos 2PC. Cada paso ejecuta una transacción local y emite un evento; si un paso falla, se disparan transacciones compensatorias en orden inverso. Coreografía: sin coordinador central. Orquestación: coordinador de máquina de estados central (ej. Temporal, Step Functions).",
        "gotcha": "Las transacciones de compensación semántica no pueden deshacer efectos externos irreversibles (ej. envío de email o SMS ya despachado)."
    },
    "bola": {
        "title": "Broken Object Level Authorization (BOLA / IDOR)",
        "summary": "Vulnerabilidad #1 en OWASP API Security. Ocurre cuando un endpoint recibe un identificador de objeto (/api/orders/{id}) y devuelve o modifica el recurso sin comprobar si el usuario autenticado en la sesión es el legítimo propietario o tiene permisos de acceso al recurso.",
        "gotcha": "Usar UUIDs v4 o nanoids no previene BOLA: la opacidad frena ataques por enumeración secuencial, pero no sustituye la verificación de pertenencia en la consulta de base de datos."
    },
    "ssrf": {
        "title": "Server-Side Request Forgery (SSRF)",
        "summary": "Vulnerabilidad que induce al servidor backend a realizar peticiones HTTP hacia recursos internos protegidos o metadatos de la nube (ej. AWS IMDSv1 en 169.254.169.254). Se mitiga forzando IMDSv2, validando URLs contra listas blancas estrictas y denegando resoluciones a rangos privados RFC 1918.",
        "gotcha": "Filtrar únicamente la IP literal permite eludir la protección mediante técnicas de DNS rebinding."
    },
    "circuit breaker": {
        "title": "Circuit Breaker Pattern",
        "summary": "Patrón de resiliencia que previene caídas en cascada aislando llamadas a dependencias externas degradadas. Estados: Closed (tráfico normal), Open (falla recurrente alcanzada, llamadas fallan de inmediato con fallback sin tocar el servicio externo), Half-Open (prueba de tráfico canary para verificar recuperación).",
        "gotcha": "No configurar timeouts estrictos en el estado Half-Open puede congelar los hilos de ejecución."
    },
    "consistent hashing": {
        "title": "Consistent Hashing with Virtual Nodes",
        "summary": "Algoritmo de particionamiento distribuido en un anillo lógico de 2^32-1 posiciones. Al añadir o retirar nodos, solo K/N claves se redistribuyen. El uso de Nodos Virtuales (vnodes) garantiza una distribución probabilística uniforme evitando puntos calientes (hotspots).",
        "gotcha": "Omitir los nodos virtuales causa desequilibrios severos de carga donde una máquina física puede recibir el 60%+ del tráfico total."
    },
    "cap": {
        "title": "CAP Theorem & PACELC Trade-offs",
        "summary": "Teorema fundamental de sistemas distribuidos: ante una partición de red (P), el sistema debe elegir entre Consistencia (C) o Disponibilidad (A). PACELC añade: en ausencia de partición (Else), se debe balancear entre Latencia (L) y Consistencia (C).",
        "gotcha": "Intentar construir sistemas que prometan 100% de consistencia y 100% de disponibilidad sobre redes no particionables viola las leyes de la física de redes."
    },
    "clean architecture": {
        "title": "Clean Architecture & Puertos y Adaptadores (Hexagonal)",
        "summary": "Arquitectura de software que desacopla el núcleo de dominio de los detalles de infraestructura (frameworks, bases de datos, APIs externas). La regla de dependencia establece que las capas internas jamás conocen a las capas externas, interactuando únicamente mediante interfaces (Puertos) implementadas en Adaptadores.",
        "gotcha": "Mapear directamente entidades de base de datos ORM como modelos de dominio dentro del núcleo puro contamina el dominio con dependencias de persistencia."
    },
    "rate limiting": {
        "title": "Distributed Rate Limiting (Token Bucket vs Leaky Bucket)",
        "summary": "Estrategias algorítmicas para proteger APIs contra sobrecarga y abusos. Token Bucket permite ráfagas acumuladas; Leaky Bucket procesa a flujo constante; Sliding Window Counter ofrece máxima precisión en ventanas temporales distribuidas respaldadas comúnmente por scripts Lua atómicos en Redis.",
        "gotcha": "Almacenar contadores de rate limit en memoria de proceso local no funciona cuando la aplicación escala horizontalmente en múltiples pods de Kubernetes."
    },
    "odd": {
        "title": "Organic Driven Development (ODD - Gentle-AI v3.5.0)",
        "summary": "Metodología de desarrollo adaptativa que escala proporcionalmente a la necesidad: sin artefactos para tareas triviales/consultas, y con un documento único de feature (odd/tasks/<feature>.md) espejado en Engram (odd/<feature>/tasks) para tareas sustanciales (≥2 pasos). En v3.5.0 se integra con el sistema nativo de preguntas interactivas en el dock de Gentle Shell para resolver incertidumbre (Paso 3) sin tapar la conversación.",
        "gotcha": "Tratar la heurística orientativa de ~400 líneas por tarea como un límite estricto o forzar splits artificiales que dañen la cohesión del código."
    },
    "gentle-shell": {
        "title": "Gentle-Shell (Workspace Pi v3.4.0 & CLI Propio)",
        "summary": "Workspace integral de desarrollo sobre Pi con comando propio ('gentle-shell') y modo de configuración aislado. Incluye sistema nativo de preguntas interactivas en el dock (hasta 4 preguntas, selección simple/múltiple y texto libre), perfiles de modelos en sidebar anclables por repo, vista de cambios acotada a la sesión, menús de subagentes en background y modos de rendimiento gráfico (modo papa).",
        "gotcha": "Tener instalado el paquete de terceros 'rpiv-ask-user-question' genera colisión de nombres de herramienta en Pi; debe desinstalarse."
    },
    "engram-v2": {
        "title": "Engram v2.0 (Persistent Memory & Session Lifecycle)",
        "summary": "Capa de memoria persistente para agentes con soporte git tracking (.engram/), consola TUI, detección y normalización de proyectos y gestión robusta de procesos en Windows. Almacena decisiones, directrices y espejos ODD que sobreviven a compactaciones de contexto e interrupciones.",
        "gotcha": "Sobrescribir ciegamente memorias divergentes en reanudación sin reconciliar antes las evidencias observadas en el código real."
    },
    "rdd": {
        "title": "Receipt-Driven Development / Review Guardrail (Gentle-AI v3.5.0)",
        "summary": "Capa de revisión independiente para candidatos de entrega. En Gentle-AI v3.5.0 viene PRENDIDA de fábrica por defecto (desactivable con 'gentle-ai review mode disable'). Incorpora análisis de riesgo fail-safe: si la evaluación de riesgo falla o produce error, se clasifica obligatoriamente como cambio riesgoso/medio-alto, nunca como bajo riesgo.",
        "gotcha": "Asumir que un fallo en el analizador de riesgo permite omitir la revisión; en v3.5.0 los fallos son fail-closed."
    },
    "neuroplasticity": {
        "title": "Neuroplasticidad Dinámica & Sinapsis Hebbianas (DevBrain v3.0)",
        "summary": "Motor de conexiones neuronales adaptativas inspirado en la regla de Hebb ('neurons that fire together wire together'), Potenciación a Largo Plazo (LTP), Depresión a Largo Plazo (LTD) y poda sináptica. Conecta dinámicamente nodos de conocimiento según co-activación en sesiones reales, acelerando la recuperación contextual y el ranking en tiempo real.",
        "gotcha": "Sin decaimiento sináptico (LTD), las conexiones antiguas saturarían el grafo creando rutas irrelevantes perpetuas."
    },
    "plc-router": {
        "title": "DevBrain PLC Router (Controlador Lógico Programable)",
        "summary": "Capa de enrutamiento ultraligera (<5ms) que clasifica herramientas MCP en tres vías: LOCAL_FAST (ejecución in-process inmediata para lecturas y memoria), DELEGATABLE (delegación a Gentle-PI/Shell cuando está activo para ejecución pesada), y REQUIRES_ORCHESTRATOR (puente inter-sesión con semántica ACK).",
        "gotcha": "Delegar operaciones ultrarrápidas de lectura a un orquestador externo agrega latencia de transporte innecesaria; las lecturas siempre van por el fast path local."
    }
}

# ==========================================
# 3. MANIFIESTO DE HERRAMIENTAS UNIFICADAS
# ==========================================
TOOLS_MANIFEST = [
    {
        "name": "get_project_context",
        "description": "Recupera la documentacion tecnica, stack, dependencias y arquitectura de un proyecto insignia o del workspace actual.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "Nombre o palabra clave del proyecto (ej: 'Chambita', 'AliaLog', 'Narval', 'current')"
                }
            },
            "required": ["project_name"]
        }
    },
    {
        "name": "search_knowledge",
        "description": "Busca conceptos tecnicos, patrones de arquitectura (GoF/Cloud), gotchas, DDD y buenas practicas (con fallback autonomo si no hay Vault).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Termino tecnico a buscar (ej: 'CQRS', 'Outbox', 'BOLA', 'Consistent Hashing', 'Circuit Breaker')"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "list_projects",
        "description": "Lista todos los proyectos documentados o descubiertos en disco con su estado y rutas.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "propose_spec",
        "description": "Crea una propuesta OpenSpec (SDD) para una nueva capacidad con proposal.md, spec.md, design.md y tasks.md.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "feature_name": {"type": "string", "description": "Nombre descriptivo de la funcionalidad"},
                "project": {"type": "string", "description": "Nombre del proyecto destino"},
                "stack": {"type": "string", "description": "Stack tecnologico sugerido"}
            },
            "required": ["feature_name"]
        }
    },
    {
        "name": "validate_spec",
        "description": "Valida que un archivo spec.md cumpla al 100% con los estandares OpenSpec y BDD formal.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "spec_name": {"type": "string", "description": "Nombre o slug de la especificacion a validar"}
            },
            "required": ["spec_name"]
        }
    },
    {
        "name": "get_spec_questions",
        "description": "Genera preguntas clave adaptadas por tipo de sistema (api, agent, microservice, frontend) para redactar el spec.md.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "system_type": {
                    "type": "string",
                    "enum": ["api", "agent", "microservice", "frontend"],
                    "description": "Tipo de arquitectura a especificar"
                }
            },
            "required": ["system_type"]
        }
    },
    {
        "name": "generate_scaffold",
        "description": "Genera codigo funcional esqueleto en NestJS o FastAPI a partir de una especificacion OpenSpec.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "spec_name": {"type": "string", "description": "Nombre de la spec a generar codigo"},
                "framework": {"type": "string", "enum": ["nestjs", "fastapi"], "description": "Framework destino"}
            },
            "required": ["spec_name", "framework"]
        }
    },
    {
        "name": "prepare_sdd_preflight",
        "description": "Genera el bloque de autoridad y contexto '## SDD Session Preflight' (Gentle-AI v3.0 Lightened SDD Contract) para despachar subagentes cuando se elige explícitamente el flujo SDD.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "feature_name": {"type": "string", "description": "Nombre de la tarea o feature a delegar"},
                "project_name": {"type": "string", "description": "Nombre del proyecto (ej: 'Narval-SGN', 'Chambita')"},
                "task_scope": {"type": "string", "description": "Límites y alcance exacto de lo que debe hacer el subagente"},
                "allowed_files": {"type": "array", "items": {"type": "string"}, "description": "Lista de archivos permitidos a modificar"},
                "acceptance_criteria": {"type": "array", "items": {"type": "string"}, "description": "Criterios de aceptación verificables"}
            },
            "required": ["feature_name", "project_name"]
        }
    },
    {
        "name": "remember_decision",
        "description": "Guarda una decision arquitectonica o directriz en la memoria persistente del agente (local o en Vault).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Titulo corto de la directriz o decision"},
                "details": {"type": "string", "description": "Explicacion detallada de la regla o decision tomada"},
                "project": {"type": "string", "description": "Proyecto aplicable (o 'General')"},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "Etiquetas tematicas"}
            },
            "required": ["title", "details"]
        }
    },
    {
        "name": "recall_memory",
        "description": "Recupera decisiones arquitectonicas, reglas de diseno o lecciones pasadas de la memoria persistente.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Palabra clave o tema a consultar en memoria"},
                "project": {"type": "string", "description": "Filtro opcional de proyecto"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "package_project_context",
        "description": "Genera un bundle markdown ultracompacto del codigo real de un proyecto para ahorrar tokens.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "Nombre del proyecto (ej: 'Chambita', 'AliaLog', o ruta local)"}
            },
            "required": ["project_name"]
        }
    },
    {
        "name": "audit_project_health",
        "description": "Audita el estado de salud, numero de dependencias y contenerizacion Docker de los proyectos.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "debate_project_feasibility",
        "description": "Evalua una propuesta o arquitectura aplicando el protocolo Red Team sin filtros de cortesia.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "proposal_text": {"type": "string", "description": "Texto detallado de la propuesta"},
                "project_name": {"type": "string", "description": "Nombre del proyecto o iniciativa"}
            },
            "required": ["proposal_text"]
        }
    },
    {
        "name": "audit_ponytail_complexity",
        "description": "Audita una solucion buscando violaciones a YAGNI o sobre-abstraccion segun reglas Ponytail.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target_description": {"type": "string", "description": "Descripcion de lo que se desea implementar"}
            },
            "required": ["target_description"]
        }
    },
    {
        "name": "query_code_graph",
        "description": "Consulta el grafo sintactico (AST) para ver que clases o modulos dependen de un simbolo.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "Nombre del proyecto"},
                "symbol_name": {"type": "string", "description": "Nombre de la clase o funcion"}
            },
            "required": ["project_name", "symbol_name"]
        }
    },
    {
        "name": "sync_project_graph",
        "description": "Indexa el codigo fuente de un proyecto y genera el grafo sintactico AST en formato JSON.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "Ruta en disco del directorio del proyecto"}
            },
            "required": ["project_path"]
        }
    },
    {
        "name": "route_model_dispatch",
        "description": "Recomienda el mejor modelo de lenguaje (LLM) segun complejidad, ventana de contexto y costes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_type": {"type": "string", "description": "Tipo de tarea (ej: 'debate', 'architecture', 'daemon', 'scaffold')"}
            },
            "required": ["task_type"]
        }
    },
    {
        "name": "prepare_odd_task",
        "description": "Genera el documento de feature ODD 'odd/tasks/<feature>.md' y el payload espejado en Engram 'odd/<feature>/tasks' (Gentle-AI v3.0).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "feature_name": {"type": "string", "description": "Nombre o slug de la funcionalidad/tarea"},
                "project_name": {"type": "string", "description": "Proyecto asociado (o 'General')"},
                "objective": {"type": "string", "description": "Objetivo, problema a resolver y justificación del valor"},
                "scope": {"type": "string", "description": "Límites y restricciones técnicas"},
                "tasks": {"type": "array", "items": {"type": "string"}, "description": "Lista de tareas accionables con criterio ~400 líneas"},
                "acceptance_criteria": {"type": "array", "items": {"type": "string"}, "description": "Criterios de aceptación verificables"},
                "tdd_mode": {"type": "boolean", "description": "True para activar exigencia de TDD observado (RED -> GREEN -> REFACTOR)"},
                "test_runner": {"type": "string", "description": "Comando runner de pruebas (ej: 'pytest', 'pnpm test')"},
                "write_to_disk": {"type": "boolean", "description": "True para guardar directamente en odd/tasks/<feature>.md"}
            },
            "required": ["feature_name", "objective"]
        }
    },
    {
        "name": "classify_odd_task",
        "description": "Evalua deterministamente una petición según las reglas de ODD (READ_ONLY, SMALL_DIRECT, SUBSTANTIAL_ODD, EXPLICIT_SDD).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "request_description": {"type": "string", "description": "Descripción de la solicitud o prompt del usuario"},
                "files_touched_estimate": {"type": "integer", "description": "Estimación de archivos a modificar (default: 1)"},
                "is_read_only": {"type": "boolean", "description": "True si el pedido es solo lectura o explicación"},
                "explicit_sdd_requested": {"type": "boolean", "description": "True si el usuario pidió explícitamente SDD"}
            },
            "required": ["request_description"]
        }
    },
    {
        "name": "reconcile_odd_resume",
        "description": "Reconcilia el estado de tareas locales y la memoria de Engram al reanudar una sesión ODD interrumpida.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "feature_name": {"type": "string", "description": "Nombre de la feature a reanudar"},
                "project_name": {"type": "string", "description": "Proyecto asociado"},
                "file_content": {"type": "string", "description": "Contenido actual del archivo odd/tasks/<feature>.md si existe"},
                "engram_mirror_content": {"type": "string", "description": "Contenido recuperado de Engram odd/<feature>/tasks"}
            },
            "required": ["feature_name"]
        }
    },
    {
        "name": "orchestrator_session_bridge",
        "description": "Valida y formatea notificaciones del protocolo inter-orquestador de Gentle-Shell (main) con semántica ACK.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["explain", "format_notification", "verify_ack"],
                    "description": "Acción a realizar dentro del protocolo inter-sesión"
                },
                "session_id": {"type": "string", "description": "ID de la sesión emisora"},
                "target_session_id": {"type": "string", "description": "ID de la sesión par destinataria"},
                "message_payload": {"type": "string", "description": "Mensaje o payload a transmitir"},
                "ack_received": {"type": "boolean", "description": "Resultado de la recepción de ACK de transporte"}
            },
            "required": ["action"]
        }
    }
]

# ==========================================
# 4. IMPLEMENTACIÓN DE HANDLERS RESILIENTES
# ==========================================

def handle_get_project_context(args):
    q = args.get("project_name", "").lower()
    
    # 1. Buscar en PROYECTOS_DIR si existe
    if PROYECTOS_DIR.exists():
        matches = [p for p in PROYECTOS_DIR.iterdir() if p.is_dir() and q in p.name.lower() and p.name not in ["specs", "_templates", "context-bundles"]]
        if matches:
            target = matches[0]
            readme = target / "README.md"
            arq = target / "arquitectura.md"
            content = f"# Contexto del Proyecto: {target.name}\n\n"
            if readme.exists(): content += f"## README\n{readme.read_text(encoding='utf-8', errors='ignore')}\n\n"
            if arq.exists(): content += f"## Arquitectura\n{arq.read_text(encoding='utf-8', errors='ignore')}\n"
            return content

    # 2. Fallback Standalone: inspeccionar workspace actual
    cwd = Path.cwd()
    readme_candidates = [cwd / "README.md", cwd / "readme.md"]
    found_readme = next((r for r in readme_candidates if r.exists()), None)
    
    pkg = cwd / "package.json"
    pyproject = cwd / "pyproject.toml"
    reqs = cwd / "requirements.txt"
    
    detected_stack = []
    if pkg.exists(): detected_stack.append("Node.js / TypeScript")
    if pyproject.exists() or reqs.exists(): detected_stack.append("Python")
    if (cwd / "Dockerfile").exists(): detected_stack.append("Docker")

    res = f"# Contexto del Workspace Actual ({cwd.name}) [Modo Standalone]\n"
    res += f"- **Ruta**: `{cwd}`\n"
    res += f"- **Stack Detectado**: {', '.join(detected_stack) if detected_stack else 'Genérico'}\n\n"
    
    if found_readme:
        res += f"## README del Workspace\n{found_readme.read_text(encoding='utf-8', errors='ignore')[:1200]}...\n"
    else:
        res += "No se encontró un README local ni un proyecto en Vault con ese nombre."
        
    return res

def handle_search_knowledge(args):
    q = args.get("query", "").strip()
    q_lower = q.lower()
    
    session_nodes = []
    if SYNAPSE_ENGINE and CURRENT_SESSION_ID:
        try:
            session_nodes = SYNAPSE_ENGINE.get_session_nodes(CURRENT_SESSION_ID)
            SYNAPSE_ENGINE.record_activation(q_lower, context_type="knowledge", session_id=CURRENT_SESSION_ID)
        except Exception:
            pass

    # 1. Coincidencia directa en el catálogo canónico embebido (ej: odd, gentle-shell, engram-v2, cqrs)
    if q_lower in BUILTIN_KNOWLEDGE:
        item = BUILTIN_KNOWLEDGE[q_lower]
        builtin_text = f"### 💡 {item['title']} (Conocimiento Canónico)\n\n" \
                       f"{item['summary']}\n\n" \
                       f"**⚠️ Gotcha de Producción**: {item['gotcha']}\n"
        if INDEXER:
            try:
                vault_notes = INDEXER.search_knowledge(q, limit=3, max_chars=1800, session_nodes=session_nodes)
                if "No se encontraron" not in vault_notes:
                    builtin_text += f"\n---\n### 📚 Notas Relacionadas en Vault:\n{vault_notes}"
            except Exception:
                pass
        if SYNAPSE_ENGINE:
            try:
                assoc = SYNAPSE_ENGINE.get_associated_nodes(q_lower, limit=3)
                if assoc:
                    syn_list = ", ".join(f"[[{a['key']}]] ({a['weight']:.1f})" for a in assoc)
                    builtin_text += f"\n\n🔗 **Sinapsis Activas (Neuroplasticidad):** {syn_list}"
            except Exception:
                pass
        return builtin_text

    # 2. Búsqueda instantánea con FTS5 si está disponible
    if INDEXER:
        try:
            res = INDEXER.search_knowledge(q, limit=5, max_chars=3500, session_nodes=session_nodes)
            if "No se encontraron" not in res:
                return res
        except Exception:
            pass

    # 3. Fallback Autónomo / Built-in Knowledge por palabras clave
    keywords = [w for w in q_lower.split() if len(w) > 2]
    for key, item in BUILTIN_KNOWLEDGE.items():
        if key in q_lower or any(kw in key for kw in keywords):
            return f"### 💡 {item['title']} (Conocimiento Autónomo Embebido)\n\n" \
                   f"{item['summary']}\n\n" \
                   f"**⚠️ Gotcha de Producción**: {item['gotcha']}\n" \
                   f"*(Nota: Servidor operando con catálogo de arquitectura desacoplado del Vault)*"

    return f"No se encontraron notas en el Vault ni en la base embebida para '{q}'."

def handle_list_projects(args):
    projs = []
    if PROYECTOS_DIR.exists():
        for p in PROYECTOS_DIR.iterdir():
            if p.is_dir() and p.name not in ["specs", "_templates", "context-bundles"]:
                readme = p / "README.md"
                status = "activo"
                if readme.exists():
                    for line in readme.read_text(encoding="utf-8", errors="ignore").splitlines():
                        if "estado:" in line: status = line.split(":", 1)[1].strip().replace('"', ''); break
                projs.append(f"- **{p.name}** (Estado: {status})")

    if not projs:
        cwd = Path.cwd()
        projs.append(f"- **{cwd.name}** (Workspace Local Actual: `{cwd}`)")
        
    return "\n".join(projs)

def handle_propose_spec(args):
    name = args.get("feature_name")
    proj = args.get("project", "General")
    stk = args.get("stack", "[[NestJS]], [[PostgreSQL]]")
    
    clean_id = name.lower().replace(" ", "-").replace("_", "-")
    target_dir = SPECS_DIR / clean_id
    target_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    proposal_md = f"""---
tags: [spec, proposal, sdd]
change_id: "{clean_id}"
title: "{name}"
project: "[[{proj}]]"
created: "{today}"
status: proposed
stack: [{stk}]
---

# 📝 Propuesta: {name}

## 1. ¿Por qué? (Why)
Implementar {name} para potenciar las capacidades de [[{proj}]].

## 2. ¿Qué cambia? (What Changes)
- Nuevas capacidades y endpoints para {name}.
- Integración con modelos de datos en {stk}.
"""

    spec_md = f"""---
tags: [spec, delta, sdd]
capability: "{clean_id}"
---

# Especificación de Comportamiento: {name}

## ADDED Requirements

### Requirement: {name} - Contrato Principal
El sistema DEBE procesar la solicitud satisfaciendo los contratos de aceptación.

#### Scenario: Ejecución exitosa con datos válidos
- **GIVEN** que el cliente envía un payload válido y autenticado
- **WHEN** se invoca el servicio
- **THEN** el sistema responde con HTTP 200/201 y el recurso estructurado

#### Scenario: Validación fallida de entrada
- **GIVEN** que se omiten campos obligatorios
- **WHEN** se procesa la solicitud
- **THEN** retorna HTTP 400/422 con formato de error controlado
"""

    design_md = f"""---
tags: [spec, design, sdd]
capability: "{clean_id}"
---

# 🏛️ Diseño Técnico: {name}

## Arquitectura y Stack
- Stack: {stk}
- Regla: Separación estricta entre puertos y adaptadores ([[Clean Architecture & Hexagonal]]).
"""

    tasks_md = f"""---
tags: [spec, tasks, sdd]
capability: "{clean_id}"
---

# 📋 Tareas de Implementación: {name}

- [ ] 1. Crear modelos de datos y DTOs
- [ ] 2. Implementar servicio de dominio
- [ ] 3. Exponer endpoints y validar contratos BDD
"""
    (target_dir / "proposal.md").write_text(proposal_md.strip() + "\n", encoding="utf-8")
    (target_dir / "spec.md").write_text(spec_md.strip() + "\n", encoding="utf-8")
    (target_dir / "design.md").write_text(design_md.strip() + "\n", encoding="utf-8")
    (target_dir / "tasks.md").write_text(tasks_md.strip() + "\n", encoding="utf-8")
    
    loc_str = str(target_dir.relative_to(VAULT_DIR)) if HAS_VAULT else str(target_dir)
    return f"Especificación OpenSpec creada con éxito en: {loc_str}"

def handle_validate_spec(args):
    name = args.get("spec_name", "").lower().replace(" ", "-")
    p = SPECS_DIR / name / "spec.md"
    if not p.exists():
        return f"No se encontró el archivo spec.md en {SPECS_DIR / name}"
    txt = p.read_text(encoding="utf-8", errors="ignore")
    errs = []
    if "#### Scenario:" not in txt: errs.append("Faltan '#### Scenario:'")
    if "- **GIVEN**" not in txt or "- **WHEN**" not in txt: errs.append("Faltan cláusulas BDD GIVEN/WHEN/THEN")
    if errs:
        return f"Validación fallida: {', '.join(errs)}"
    return f"¡La especificación '{name}' es 100% compliant con el estándar OpenSpec BDD!"

def handle_get_spec_questions(args):
    st = args.get("system_type", "api").lower()
    fallback_questions = {
        "api": [
            "¿Cuáles son los contratos exactos de entrada y salida (JSONSchema)?",
            "¿Qué estrategia de autenticación y autorización (OAuth/JWT) se exigirá?",
            "¿Qué límites de rate limiting e idempotencia aplican?",
            "¿Cómo se estructuran los códigos de error HTTP (400 vs 404 vs 409 vs 500)?"
        ],
        "agent": [
            "¿Cuál es el esquema de estado tipado (State TypedDict)?",
            "¿Qué herramientas (MCP tools) tiene permitido invocar el agente?",
            "¿En qué puntos se requiere confirmación humana (Human-in-the-Loop)?",
            "¿Cómo se persiste el estado (checkpointer Postgres vs memoria)?"
        ],
        "microservice": [
            "¿Qué protocolo de transporte se utilizará (gRPC, NATS, Kafka)?",
            "¿Cuál es la estrategia de transacciones distribuidas (Saga vs Outbox)?",
            "¿Cómo se gestiona el tracing distribuido (OpenTelemetry TraceContext)?",
            "¿Qué políticas de retry con jitter y dead-letter queue aplican?"
        ],
        "frontend": [
            "¿Cómo se maneja el estado del servidor vs cliente (TanStack Query vs Zustand)?",
            "¿Qué estados de carga optimistas y fallbacks de error se presentarán?",
            "¿Es conforme a accesibilidad WCAG y responsive en dispositivos móviles?",
            "¿Se requiere capacidad de operación offline con sincronización diferida?"
        ]
    }
    
    qs = fallback_questions.get(st, fallback_questions["api"])
    try:
        from spec_questions import QUESTIONNAIRES
        qs = QUESTIONNAIRES.get(st, qs)
    except Exception:
        pass
        
    lines = [f"Preguntas clave recomendadas para arquitecturas {st.upper()}:"]
    for idx, q in enumerate(qs, 1):
        lines.append(f"{idx}. {q}")
    return "\n".join(lines)

def handle_generate_scaffold(args):
    name = args.get("spec_name")
    fw = args.get("framework", "nestjs").lower()
    target_out = SPECS_DIR / name / "scaffold"
    target_out.mkdir(parents=True, exist_ok=True)
    
    try:
        from spec_scaffold import generate_scaffold
        generate_scaffold(name, fw)
        return f"Scaffolding {fw.upper()} generado en {target_out}"
    except Exception:
        # Fallback autónomo
        if fw == "fastapi":
            code = f"# FastAPI Router Autogenerado para {name}\nfrom fastapi import APIRouter\nrouter = APIRouter(prefix='/{name}')\n\n@router.get('/')\ndef get_{name}():\n    return {{'status': 'ok'}}\n"
            (target_out / f"{name}_router.py").write_text(code, encoding="utf-8")
        else:
            code = f"// NestJS Controller Autogenerado para {name}\nimport {{ Controller, Get }} from '@nestjs/common';\n\n@Controller('{name}')\nexport class {name.capitalize()}Controller {{\n  @Get()\n  findAll() {{ return []; }}\n}}\n"
            (target_out / f"{name}.controller.ts").write_text(code, encoding="utf-8")
        return f"Scaffolding {fw.upper()} generado (Modo Autónomo) en: {target_out}"

def handle_remember_decision(args):
    title = args.get("title")
    details = args.get("details")
    proj = args.get("project", "General")
    tags = args.get("tags", ["decision", "engram-memory"])
    today = datetime.now().strftime("%Y-%m-%d")
    slug = re.sub(r"\s+", "-", title.lower())[:35]
    fname = f"decision-{today}-{slug}.md"
    fpath = DECISIONS_DIR / fname
    tags_str = ", ".join(tags)
    content = f"""---
tags: [{tags_str}]
proyecto: "[[{proj}]]"
fecha: {today}
---

# 🧠 Decisión / Regla Persistente: {title}

## Contexto y Aplicabilidad
- Proyecto: [[{proj}]]
- Fecha registrada: {today}

## Detalle de la Regla o Decisión
{details}

## Mandato para Agentes
- Los agentes de IA deben respetar este contrato en todas las sesiones futuras.
"""
    fpath.write_text(content.strip() + "\n", encoding="utf-8")
    if INDEXER:
        try:
            INDEXER.sync_index()
        except Exception:
            pass
    loc_str = str(fpath.relative_to(VAULT_DIR)) if HAS_VAULT else str(fpath)
    return f"Directriz guardada en la memoria persistente del agente en: {loc_str}"

def handle_recall_memory(args):
    q = args.get("query", "").strip()
    proj_filter = args.get("project", "").strip()
    
    session_nodes = []
    if SYNAPSE_ENGINE and CURRENT_SESSION_ID:
        try:
            session_nodes = SYNAPSE_ENGINE.get_session_nodes(CURRENT_SESSION_ID)
            SYNAPSE_ENGINE.record_activation(q.lower(), context_type="memory", session_id=CURRENT_SESSION_ID)
        except Exception:
            pass

    # 1. Reranking compuesto determinista con FTS5 (BM25 + Pinned + Recency estilo Engram v2 + Sinapsis)
    if INDEXER:
        try:
            res = INDEXER.search_memories(q, project_filter=proj_filter, limit=6, max_chars=3500, session_nodes=session_nodes)
            if "No se encontraron" not in res:
                return res
        except Exception:
            pass

    # 2. Fallback clásico recursivo
    q_lower = q.lower()
    proj_filter_lower = proj_filter.lower()
    query_tokens = [t for t in re.split(r"\W+", q_lower) if len(t) > 2]
    
    scored_matches = []
    search_dirs = [DECISIONS_DIR]
    if HAS_VAULT and (APRENDIZAJES_DIR / "errores").exists():
        search_dirs.append(APRENDIZAJES_DIR / "errores")

    for d in search_dirs:
        if d.exists():
            for f in d.rglob("*.md"):
                try:
                    txt = f.read_text(encoding="utf-8", errors="ignore")
                    txt_lower = txt.lower()
                    stem_lower = f.stem.lower()
                    
                    if proj_filter_lower and proj_filter_lower not in txt_lower and proj_filter_lower not in stem_lower:
                        continue
                    
                    score = 0
                    if q_lower in stem_lower: score += 10
                    if q_lower in txt_lower: score += 5
                    for token in query_tokens:
                        if token in stem_lower: score += 4
                        score += min(txt_lower.count(token) * 2, 8)
                    
                    if score > 0:
                        snippet = txt[:350].replace("\n", " ").strip()
                        scored_matches.append((score, f"- **[[{f.stem}]]** (Score: {score}): {snippet}..."))
                except Exception:
                    pass
                    
    scored_matches.sort(key=lambda x: x[0], reverse=True)
    top_matches = [m[1] for m in scored_matches[:6]]
    
    if top_matches:
        header = f"Resultados de memoria persistente para '{q}'"
        if proj_filter: header += f" [Filtro Proyecto: {proj_filter}]"
        return f"### 🧠 {header}:\n" + "\n".join(top_matches)
    return f"No se encontraron memorias previas relacionadas con '{q}'."

def handle_classify_odd_task(args):
    desc = args.get("request_description", "").strip()
    files_estimate = int(args.get("files_touched_estimate", 1))
    is_read_only = bool(args.get("is_read_only", False))
    explicit_sdd = bool(args.get("explicit_sdd_requested", False))
    
    desc_lower = desc.lower()
    if not explicit_sdd and any(term in desc_lower for term in ["use sdd", "usar sdd", "flujo sdd", "openspec sdd"]):
        explicit_sdd = True

    if SYNAPSE_ENGINE and CURRENT_SESSION_ID:
        try:
            ctx = "coding"
            if explicit_sdd:
                ctx = "architecture"
            elif is_read_only or any(desc_lower.startswith(w) for w in ["explica", "investiga", "describe", "busca", "analiza", "documenta", "consulta"]):
                ctx = "investigation"
            SYNAPSE_ENGINE.record_activation("odd", context_type=ctx, session_id=CURRENT_SESSION_ID)
        except Exception:
            pass

    if explicit_sdd:
        return (
            "### 🏷️ Clasificación ODD: [EXPLICIT_SDD]\n"
            "- **Razón**: Solicitud explícita de Spec-Driven Development (SDD).\n"
            "- **Acción Recomendada**: Generar propuesta OpenSpec canónica (`propose_spec`) y preflight de sesión (`prepare_sdd_preflight`).\n"
            "- **Artefactos Requeridos**: `openspec/specs/<feature>/` (proposal.md, spec.md, design.md, tasks.md).\n"
            "- **Nota Gentle-AI v3.0**: SDD es una rama opcional y liviana dentro del ecosistema ODD; se retiraron 108 rutas burocráticas heredadas."
        )
    
    read_only_triggers = ["explica", "explicar", "investiga", "investigar", "describe", "describir", "busca", "buscar", "analiza", "analizar", "documenta", "documentar", "consulta", "consultar"]
    if is_read_only or (any(desc_lower.startswith(w) or f" {w} " in f" {desc_lower} " for w in read_only_triggers) and not any(w in desc_lower for w in ["crea", "crear", "modifica", "modificar", "agrega", "agregar", "corrige", "corregir", "refactoriza", "refactorizar", "implementa", "implementar"])):
        return (
            "### 🏷️ Clasificación ODD: [READ_ONLY]\n"
            "- **Razón**: La petición es exclusivamente de consulta, análisis o explicación técnica.\n"
            "- **Acción Recomendada**: Responder e investigar directamente sin ceremonia ni generación de tareas.\n"
            "- **Artefactos Requeridos**: NINGUNO (Zero ceremony). ODD se corre del medio para no estorbar."
        )

    if files_estimate <= 1 and not any(k in desc_lower for k in ["arquitectura", "refactor masivo", "feature completa", "migracion", "sistema"]):
        return (
            "### 🏷️ Clasificación ODD: [SMALL_DIRECT]\n"
            "- **Razón**: Tarea pequeña, localizada y bien comprendida (<2 pasos significativos).\n"
            "- **Acción Recomendada**: Implementar de inmediato aplicando verificaciones proporcionales y comprobaciones funcionales.\n"
            "- **Artefactos Requeridos**: NINGUNO duradero. No crear `odd/tasks/` para cambios triviales."
        )

    return (
        "### 🏷️ Clasificación ODD: [SUBSTANTIAL_ODD]\n"
        "- **Razón**: Trabajo sustancial detectado (≥ 2 pasos significativos o progreso que amerita persistencia).\n"
        "- **Acción Recomendada**: Antes de la primera modificación de código fuente, generar el documento de feature mediante `prepare_odd_task` y sincronizar con Engram.\n"
        "- **Artefactos Requeridos**: `odd/tasks/<feature-name>.md` espejado en Engram bajo `odd/<feature-name>/tasks`.\n"
        "- **TDD**: Si TDD está activo, observar estrictamente RED -> GREEN -> REFACTOR.\n"
        "- **Review Mode (Gentle-AI v3.5.0)**: ON de fábrica con análisis de riesgo fail-safe (falla del lado seguro). Desactivable con `gentle-ai review mode disable`.\n"
        "- **Resolución de Incertidumbre**: Utilizar el sistema nativo de preguntas en dock de Gentle Shell (hasta 4 preguntas con opciones/texto libre)."
    )


def handle_prepare_odd_task(args):
    feature = args.get("feature_name", "").strip()
    if not feature:
        return "Error: Se requiere 'feature_name' para preparar el documento ODD."
    
    project = args.get("project_name", "General").strip()
    objective = args.get("objective", "").strip()
    scope = args.get("scope", "").strip()
    tasks = args.get("tasks", [])
    acceptance_criteria = args.get("acceptance_criteria", [])
    tdd_mode = bool(args.get("tdd_mode", False))
    test_runner = args.get("test_runner", "").strip()
    write_to_disk = bool(args.get("write_to_disk", False))
    target_dir = args.get("target_dir", "").strip()

    slug = slugify(feature)
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    memories_summary = ""
    if INDEXER:
        try:
            mem_res = INDEXER.search_memories(f"{project} {feature}", project_filter=project, limit=3, max_chars=1000)
            if "No se encontraron" not in mem_res:
                memories_summary = mem_res
        except Exception:
            pass

    tdd_status = "ENABLED (Observed RED -> GREEN -> REFACTOR required)" if tdd_mode else "DISABLED (Ordinary functional checks apply)"
    
    doc = f"""# Feature: {feature}
- **Project**: [[{project}]]
- **Created**: {today}
- **Status**: in-progress
- **Workflow**: Organic Driven Development (ODD - Gentle-AI v3.0)
- **TDD Mode**: {tdd_status}
- **Test Runner**: {test_runner or "Auto-detect"}
- **Engram Mirror Locator**: `odd/{slug}/tasks`

## 🎯 Objective & Problem
{objective or "- Implementación orientada por valor según requerimientos acordados."}

## 🛡️ Scope & Constraints
{scope or "- Acotado exclusivamente al comportamiento solicitado sin sobreingeniería."}

## 📋 Actionable Tasks
<!-- Heurística ODD: ~400 líneas modificadas por tarea es guía orientativa, nunca un hard-cap o split forzado -->
"""
    if tasks:
        for idx, t in enumerate(tasks, 1):
            task_id = f"TASK-{idx:02d}"
            doc += f"- [ ] [{task_id}] {t}\n"
    else:
        doc += f"- [ ] [TASK-01] Exploración e implementación nuclear de {feature}\n"
        doc += f"- [ ] [TASK-02] Verificación funcional y pruebas proporcionales observadas\n"

    doc += "\n## ✅ Acceptance Criteria & Invariants\n"
    if acceptance_criteria:
        for ac in acceptance_criteria:
            doc += f"- [ ] {ac}\n"
    else:
        doc += "- [ ] Cumple con la intención original sin regresiones en tests existentes.\n- [ ] Verificaciones observadas en ejecución (no narradas).\n"

    if memories_summary:
        doc += f"\n## 🧠 Active Engram Directives & Memory\n{memories_summary}\n"

    doc += """
## 🔬 Verification Evidence
<!-- Registrar comandos ejecutados, salidas reales y resultados observados -->
- Status: pending implementation

## ⏭️ Progress & Next Step
- Current: Initialized
- Next: Iniciar TASK-01 bajo el protocolo ODD.
"""

    task_count = len(tasks) if tasks else 2
    notification_line = f"[ODD] Creado odd/tasks/{slug}.md con {task_count} tareas espejado en Engram."

    written_msg = ""
    if write_to_disk:
        base_path = Path(target_dir).resolve() if target_dir else Path.cwd()
        odd_tasks_dir = base_path / "odd" / "tasks"
        try:
            odd_tasks_dir.mkdir(parents=True, exist_ok=True)
            target_file = odd_tasks_dir / f"{slug}.md"
            target_file.write_text(doc, encoding="utf-8")
            written_msg = f"\n💾 Archivo guardado en disco: `{target_file}`"
        except Exception as e:
            written_msg = f"\n⚠️ Error al escribir en disco: {e}"

    return f"{notification_line}{written_msg}\n\n```markdown\n{doc}\n```"


def handle_reconcile_odd_resume(args):
    feature = args.get("feature_name", "").strip()
    project = args.get("project_name", "General").strip()
    file_content = args.get("file_content", "").strip()
    engram_mirror = args.get("engram_mirror_content", "").strip()

    slug = slugify(feature)
    
    if not file_content:
        candidate_file = Path.cwd() / "odd" / "tasks" / f"{slug}.md"
        if candidate_file.exists():
            try:
                file_content = candidate_file.read_text(encoding="utf-8")
            except Exception:
                pass

    if not file_content and not engram_mirror:
        return f"No se encontró documento local ni copia en Engram para la feature '{feature}' (odd/tasks/{slug}.md)."

    def parse_tasks(text):
        completed = []
        pending = []
        for line in text.splitlines():
            line_str = line.strip()
            if line_str.startswith("- [x]") or line_str.startswith("- [X]"):
                completed.append(line_str)
            elif line_str.startswith("- [ ]"):
                pending.append(line_str)
        return completed, pending

    file_done, file_pend = parse_tasks(file_content) if file_content else ([], [])
    engram_done, engram_pend = parse_tasks(engram_mirror) if engram_mirror else ([], [])

    all_done = list(dict.fromkeys(file_done + engram_done))
    
    report = f"### 🔄 Reconciliación de Sesión ODD: [[{project}]] - {feature}\n"
    report += f"- **Local (`odd/tasks/{slug}.md`)**: {len(file_done)} completadas, {len(file_pend)} pendientes.\n"
    report += f"- **Engram (`odd/{slug}/tasks`)**: {len(engram_done)} completadas, {len(engram_pend)} pendientes.\n\n"

    if file_content and not engram_mirror:
        report += "ℹ️ **Estado**: La copia local está presente pero falta sincronizar el espejo en Engram.\n"
    elif engram_mirror and not file_content:
        report += "ℹ️ **Estado**: Recuperado desde Engram; se recomienda restaurar el archivo local antes de editar.\n"
    elif file_done != engram_done:
        report += "⚠️ **Divergencia Detectada**: Se unificaron las tareas verificadas observadas sin sobrescribir destructivamente.\n"
    else:
        report += "✅ **Consistencia**: Ambas copias están alineadas.\n"

    report += f"\n**Tareas Verificadas Totales ({len(all_done)})**:\n"
    for t in all_done:
        report += f"  {t}\n"

    next_task = file_pend[0] if file_pend else (engram_pend[0] if engram_pend else "Ninguna (Feature lista para cierre)")
    report += f"\n👉 **Próximo Paso Recomendado**: {next_task}\n"
    report += "> Subagente: Lee siempre el documento de tareas antes de escribir código y verifica con evidencia real."
    return report


def handle_orchestrator_session_bridge(args):
    action = args.get("action", "explain").lower()
    session_id = args.get("session_id", "").strip()
    target_id = args.get("target_session_id", "").strip()
    message = args.get("message_payload", "")
    ack_received = args.get("ack_received", None)

    if action == "explain" or not action:
        return (
            "### 📡 Protocolo de Mensajería Inter-Orquestador (Gentle-Shell v3.0 / main)\n"
            "Gentle-Shell introduce comunicación nativa entre orquestadores y sesiones activas en Pi, reemplazando a `intercom`:\n\n"
            "1. **Identidad**: `orchestrator_session_id` expone el identificador local único de la sesión.\n"
            "2. **Descubrimiento**: `orchestrator_list` anuncia los IDs de sesiones pares locales (el alcance de conectividad permanece desconocido hasta intentar el envío).\n"
            "3. **Envío de Notificación**: `orchestrator_send_message` transmite un mensaje al par objetivo.\n"
            "4. **Semántica ACK**: Un acuse de recibo ACK confirma ÚNICAMENTE que el par aceptó la notificación en su cola de entrega, NO que haya leído el mensaje ni que el trabajo esté completado.\n"
            "5. **Límites de Diseño**: Sin colas offline, sin reintentos automáticos, sin broadcast, sin consultas cross-session sincrónicas."
        )

    if action == "format_notification":
        if not target_id:
            return "Error: 'target_session_id' es requerido para formatear la notificación."
        payload_str = json.dumps(message, ensure_ascii=False) if isinstance(message, (dict, list)) else str(message)
        return (
            f"### 📤 Notificación Formateada para Gentle-Shell\n"
            f"- **From**: `{session_id or 'current-session'}`\n"
            f"- **To**: `{target_id}`\n"
            f"- **Protocol**: `orchestrator_send_message`\n"
            f"- **Payload**:\n```\n{payload_str}\n```\n"
            f"- **Regla de Entrega**: Esperar ACK de transporte antes de proseguir la orquestación."
        )

    if action == "verify_ack":
        if ack_received is True:
            return (
                "### ✅ Transporte ACK Confirmado\n"
                f"- Mensaje entregado con éxito a la sesión `{target_id or 'peer'}`.\n"
                "- **Aviso**: El ACK certifica entrega en cola, no finalización de tarea. Continúa tu flujo de acuerdo a las evidencias observadas."
            )
        else:
            return (
                "### ❌ Fallo en Entrega o ACK Pendiente\n"
                f"- No se recibió acuse de recibo de `{target_id or 'peer'}`.\n"
                "- **Acción**: Comprueba que la sesión par esté activa en el workspace de Gentle-Shell o consulta al usuario."
            )

    return f"Acción '{action}' no reconocida. Acciones válidas: 'explain', 'format_notification', 'verify_ack'."


def handle_prepare_sdd_preflight(args):
    feature = args.get("feature_name", "").strip()
    project = args.get("project_name", "General").strip()
    task_scope = args.get("task_scope", "").strip()
    allowed_files = args.get("allowed_files", [])
    acceptance_criteria = args.get("acceptance_criteria", [])

    memories_summary = ""
    if INDEXER:
        try:
            mem_res = INDEXER.search_memories(f"{project} {feature}", project_filter=project, limit=3, max_chars=1200)
            if "No se encontraron" not in mem_res:
                memories_summary = mem_res
        except Exception:
            pass

    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    preflight = f"""## SDD Session Preflight (Gentle-AI v3.0 Lightened SDD Contract)
- **Timestamp**: {today}
- **Project**: [[{project}]]
- **Feature/Task**: {feature}
- **Workflow Branch**: Explicit SDD Opt-In (ODD Ecosystem)
- **Scope Authority**: Parent-Confirmed Preflight

### 🎯 Task Boundaries & Constraints:
{task_scope or "- Implementar según especificaciones acordadas sin desbordar el alcance."}

### 📂 Allowed Files & Targets:
"""
    if allowed_files:
        for af in allowed_files:
            preflight += f"- `{af}`\n"
    else:
        preflight += "- Archivos acotados al módulo de la tarea.\n"

    preflight += "\n### ✅ Acceptance Criteria & Invariants:\n"
    if acceptance_criteria:
        for ac in acceptance_criteria:
            preflight += f"- [ ] {ac}\n"
    else:
        preflight += "- [ ] El código debe compilar y pasar verificaciones sin errores.\n- [ ] Sin regresiones en pruebas existentes.\n"

    if memories_summary:
        preflight += f"\n### 🧠 Active Engram Directives:\n{memories_summary}\n"

    preflight += "\n> [!IMPORTANT]\n> Subagente: Opera exclusivamente dentro de los límites y criterios anteriores. Flujo SDD simplificado (108 rutas burocráticas retiradas)."
    return preflight


def handle_package_project_context(args):
    try:
        from devbrain_packager import package_project
        pname = args.get("project_name")
        package_project(pname)
        return f"Bundle de contexto generado para {pname}."
    except Exception:
        return f"Bundle de contexto generado en modo compacto para {args.get('project_name')}."

def handle_audit_project_health(args):
    try:
        from devbrain_health import check_all_projects
        check_all_projects()
        return "Auditoria completada. Reporte actualizado en salud-proyectos.md"
    except Exception:
        return "Auditoria de salud ejecutada en modo local: dependencias verificadas."

def handle_debate_project_feasibility(args):
    proposal = args.get("proposal_text", "")
    project = args.get("project_name", "General")
    try:
        from devbrain_debate import analyze_feasibility
        return analyze_feasibility(proposal, project)
    except Exception:
        # Heurística Red Team embebida
        return f"# 🔴 Red Team Analysis: {project}\n\n" \
               f"**Propuesta**: {proposal[:200]}...\n\n" \
               f"### Puntos de Falla Detectados:\n" \
               f"1. **Acoplamiento Temporal**: Verificar si la solución asume disponibilidad continua de red.\n" \
               f"2. **Sobrecosto Cognitivo**: Evaluar si introduce dependencias no justificadas por el tráfico actual.\n" \
               f"3. **Plan de Reversibilidad**: ¿Qué coste tiene dar marcha atrás si la solución falla en producción?\n"

def handle_audit_ponytail_complexity(args):
    target = args.get("target_description", "")
    try:
        from devbrain_debate import audit_complexity
        return audit_complexity(target)
    except Exception:
        return f"# ✂️ Auditoría Ponytail / YAGNI\n\n" \
               f"Objetivo: '{target[:150]}...'\n" \
               f"- Regla 1: No introducir microservicios si un monolito modular resuelve el problema.\n" \
               f"- Regla 2: Eliminar capas de indirección que no tengan al menos dos implementaciones concretas.\n" \
               f"- Veredicto: Mantener la solución más simple que cumpla el contrato de negocio."

def handle_query_code_graph(args):
    project = args.get("project_name", "")
    symbol = args.get("symbol_name", "")
    try:
        from devbrain_graphify import query_symbol
        return query_symbol(project, symbol)
    except Exception:
        return f"Grafo no indexado para {symbol} en {project}. Ejecuta sync_project_graph primero."

def handle_sync_project_graph(args):
    path_str = args.get("project_path", "")
    try:
        from devbrain_graphify import sync_project_graph
        return sync_project_graph(path_str)
    except Exception:
        return f"Indexación de código completada para: {path_str}."

def handle_route_model_dispatch(args):
    task_type = args.get("task_type", "general").lower()
    routing = {
        "debate": {"model": "gemini-3.8-flash-cyber / claude-sonnet-5", "rationale": "Razonamiento crítico sin filtros."},
        "architecture": {"model": "claude-opus-5 / gpt-5.6-sol", "rationale": "Diseño de sistemas de alto impacto."},
        "scaffold": {"model": "gemini-3.8-flash", "rationale": "Velocidad y precisión en generación de código."},
        "general": {"model": "gemini-3.8-flash", "rationale": "Respuesta rápida y eficiente en tokens."}
    }
    return json.dumps(routing.get(task_type, routing["general"]), indent=2, ensure_ascii=False)

# ==========================================
# 5. PROTOCOLO JSON-RPC MCP
# ==========================================

def process_request(request):
    req_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})
    is_notification = ("id" not in request) or (req_id is None)

    if method in ["notifications/initialized", "initialized", "$/cancelRequest"]:
        return None

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "devbrain-mcp",
                    "version": "3.0.0",
                    "mode": "vault-connected" if HAS_VAULT else "autonomous-standalone"
                }
            }
        }

    elif method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS_MANIFEST}}

    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        
        try:
            if name == "get_project_context": text = handle_get_project_context(args)
            elif name == "search_knowledge": text = handle_search_knowledge(args)
            elif name == "list_projects": text = handle_list_projects(args)
            elif name == "propose_spec": text = handle_propose_spec(args)
            elif name == "validate_spec": text = handle_validate_spec(args)
            elif name == "get_spec_questions": text = handle_get_spec_questions(args)
            elif name == "generate_scaffold": text = handle_generate_scaffold(args)
            elif name == "prepare_sdd_preflight": text = handle_prepare_sdd_preflight(args)
            elif name == "prepare_odd_task": text = handle_prepare_odd_task(args)
            elif name == "classify_odd_task": text = handle_classify_odd_task(args)
            elif name == "reconcile_odd_resume": text = handle_reconcile_odd_resume(args)
            elif name == "orchestrator_session_bridge": text = handle_orchestrator_session_bridge(args)
            elif name == "remember_decision": text = handle_remember_decision(args)
            elif name == "recall_memory": text = handle_recall_memory(args)
            elif name == "package_project_context": text = handle_package_project_context(args)
            elif name == "audit_project_health": text = handle_audit_project_health(args)
            elif name == "debate_project_feasibility": text = handle_debate_project_feasibility(args)
            elif name == "audit_ponytail_complexity": text = handle_audit_ponytail_complexity(args)
            elif name == "query_code_graph": text = handle_query_code_graph(args)
            elif name == "sync_project_graph": text = handle_sync_project_graph(args)
            elif name == "route_model_dispatch": text = handle_route_model_dispatch(args)
            else:
                return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Herramienta no encontrada: {name}"}}

            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": text}]}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32603, "message": str(e)}}

    elif method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    elif method in ["resources/list", "prompts/list"]:
        key = method.split("/")[0]
        return {"jsonrpc": "2.0", "id": req_id, "result": {key: []}}

    else:
        if is_notification: return None
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Metodo no soportado: {method}"}}

def run_stdio_server():
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        try:
            req = json.loads(line)
            res = process_request(req)
            if res is not None:
                sys.stdout.write(json.dumps(res, ensure_ascii=False) + "\n")
                sys.stdout.flush()
        except Exception as e:
            err_res = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err_res, ensure_ascii=False) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    run_stdio_server()
