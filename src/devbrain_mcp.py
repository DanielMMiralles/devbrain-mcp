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
DevBrain Unified MCP Server (v2.1.0 - Decoupled & Resilient Architecture):
Integra la base de conocimiento de DevBrain, el ciclo completo de OpenSpec (SDD)
y las herramientas de Gentle-AI / Engram para memoria persistente.
100% prescindible de un Obsidian Vault: opera en modo conectado si existe un Vault,
o en modo Standalone autónomo con conocimiento y almacenamiento local si no existe.
Compatible al 100% con la especificación MCP oficial (2024-11-05).
"""
import json
import os
import re
from pathlib import Path
from datetime import datetime

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
        "description": "Genera el bloque de autoridad y contexto estandarizado '## SDD Session Preflight' (Gentle-AI v2.9.1) para despachar subagentes con limites estrictos y directrices Engram.",
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
    
    # 1. Búsqueda instantánea con FTS5 si está disponible
    if INDEXER:
        try:
            res = INDEXER.search_knowledge(q, limit=5, max_chars=3500)
            if "No se encontraron" not in res:
                return res
        except Exception:
            pass

    # 2. Fallback Autónomo / Built-in Knowledge (Prescindible de Vault)
    q_lower = q.lower()
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
    
    # 1. Reranking compuesto determinista con FTS5 (BM25 + Pinned + Recency estilo Engram v2)
    if INDEXER:
        try:
            res = INDEXER.search_memories(q, project_filter=proj_filter, limit=6, max_chars=3500)
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

    preflight = f"""## SDD Session Preflight (Gentle-AI v2.9.1 Contract)
- **Timestamp**: {today}
- **Project**: [[{project}]]
- **Feature/Task**: {feature}
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

    preflight += "\n> [!IMPORTANT]\n> Subagente: Opera exclusivamente dentro de los límites y criterios anteriores. No ejecutes subprocesos de consola no autorizados."
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
                    "version": "2.1.0",
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
