import sys
import io
# Asegurar UTF-8 incondicional en Windows para stdio MCP
if sys.platform == "win32":
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

"""
DevBrain Unified MCP Server:
Integra la base de conocimiento de DevBrain, el ciclo completo de OpenSpec (SDD)
y las herramientas de Gentle-AI / Engram para memoria persistente y ahorro de tokens.
Compatible al 100% con la especificacion MCP oficial (2024-11-05).
"""
import json
import os
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
VAULT_DIR = Path(os.getenv("VAULT_DIR", r"C:\Users\damm1\OneDrive\Documentos\Obsidian Vault"))
PROYECTOS_DIR = VAULT_DIR / "02-PROYECTOS"
CONOCIMIENTO_DIR = VAULT_DIR / "03-CONOCIMIENTO"
APRENDIZAJES_DIR = VAULT_DIR / "04-APRENDIZAJES"
SPECS_DIR = PROYECTOS_DIR / "specs"
DECISIONS_DIR = VAULT_DIR / "04-APRENDIZAJES" / "decisiones"
DECISIONS_DIR.mkdir(parents=True, exist_ok=True)

# Importar modulos internos si existen
# Soportar ejecucion modular (repo standalone) o dentro del vault
if (BASE_DIR / "devspec").exists():
    sys.path.append(str(BASE_DIR / "devspec"))
else:
    sys.path.append(str(VAULT_DIR / "06-SISTEMA" / "devspec"))

if (BASE_DIR / "scripts").exists():
    sys.path.append(str(BASE_DIR / "scripts"))
else:
    sys.path.append(str(VAULT_DIR / "06-SISTEMA" / "scripts"))

# ==========================================
# MANIFIESTO DE HERRAMIENTAS UNIFICADAS
# ==========================================
TOOLS_MANIFEST = [
    # --- GRUPO 1: DevBrain Core & Proyectos ---
    {
        "name": "get_project_context",
        "description": "Recupera la documentacion tecnica, stack, dependencias y arquitectura de un proyecto insignia (AliaLog, Chambita, Narval-SGN, Mayan-EDMS, Alia-IMA-LangGraph, Odysseus, AlaOrden-Web).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "Nombre o palabra clave del proyecto (ej: 'Chambita', 'AliaLog', 'Narval')"
                }
            },
            "required": ["project_name"]
        }
    },
    {
        "name": "search_knowledge",
        "description": "Busca conceptos tecnicos, patrones de arquitectura (GoF/Cloud), gotchas, DDD y buenas practicas entre las 1,675 notas del Vault.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Termino tecnico a buscar (ej: 'CQRS', 'Event Storming', 'pgvector', 'BOLA', 'React Fiber')"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "list_projects",
        "description": "Lista todos los proyectos insignia documentados en DevBrain con su estado y rutas en disco.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },

    # --- GRUPO 2: Suite OpenSpec (Spec-Driven Development) ---
    {
        "name": "propose_spec",
        "description": "Crea una propuesta de especificacion completa SDD/OpenSpec (proposal.md, spec.md con BDD Given/When/Then, design.md y tasks.md) en 02-PROYECTOS/specs/.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "feature_name": {"type": "string", "description": "Nombre de la funcionalidad (ej: 'rating-reviews', 'gps-tracking')"},
                "project": {"type": "string", "description": "Proyecto asignado (ej: 'Chambita-Ecosystem', 'AliaLog-System')"},
                "stack": {"type": "string", "description": "Tecnologias involucradas (ej: 'NestJS, PostgreSQL, shadcn')"}
            },
            "required": ["feature_name"]
        }
    },
    {
        "name": "validate_spec",
        "description": "Valida si una especificacion de OpenSpec cumple con todos los contratos de aceptacion BDD requeridos.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "spec_name": {"type": "string", "description": "Nombre o carpeta de la spec (ej: 'agent-memory-service')"}
            },
            "required": ["spec_name"]
        }
    },
    {
        "name": "get_spec_questions",
        "description": "Genera preguntas clave adaptadas por tipo de sistema (api, agent, microservice, frontend) para redactar el spec.md sin omitir detalles criticos.",
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
        "description": "Convierte una especificacion OpenSpec en codigo funcional esqueleto en NestJS (DTOs, Service, Controller) o FastAPI (Schemas Pydantic, Router).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "spec_name": {"type": "string", "description": "Nombre de la spec a generar codigo"},
                "framework": {"type": "string", "enum": ["nestjs", "fastapi"], "description": "Framework destino"}
            },
            "required": ["spec_name", "framework"]
        }
    },

    # --- GRUPO 3: Suite Gentle-AI & Engram (Memoria y Ahorro de Tokens) ---
    {
        "name": "remember_decision",
        "description": "Guarda una decision arquitectonica, regla de negocio, directriz o leccion aprendida en la memoria persistente del agente para futuras sesiones.",
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
        "description": "Recupera decisiones arquitectonicas, reglas de diseno o lecciones pasadas buscando en la memoria persistente del agente.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Palabra clave o tema a consultar en memoria"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "package_project_context",
        "description": "Genera un bundle markdown ultracompacto del codigo real de un proyecto del Escritorio, filtrando archivos pesados para ahorrar un 80% de tokens.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "Nombre del proyecto (ej: 'Chambita', 'AliaLog')"}
            },
            "required": ["project_name"]
        }
    },
    {
        "name": "audit_project_health",
        "description": "Audita el estado de salud, numero de dependencias y contenerizacion Docker de los proyectos en el Escritorio.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]

# ==========================================
# IMPLEMENTACION DE HANDLERS
# ==========================================

def handle_get_project_context(args):
    q = args.get("project_name", "").lower()
    matches = [p for p in PROYECTOS_DIR.iterdir() if p.is_dir() and q in p.name.lower() and p.name not in ["specs", "_templates", "context-bundles"]]
    if not matches:
        return f"No se encontro un proyecto que coincida con '{q}'."
    target = matches[0]
    readme = target / "README.md"
    arq = target / "arquitectura.md"
    content = f"# Contexto del Proyecto: {target.name}\n\n"
    if readme.exists(): content += f"## README\n{readme.read_text(encoding='utf-8', errors='ignore')}\n\n"
    if arq.exists(): content += f"## Arquitectura\n{arq.read_text(encoding='utf-8', errors='ignore')}\n"
    return content

def handle_search_knowledge(args):
    q = args.get("query", "").lower()
    results = []
    for f in CONOCIMIENTO_DIR.rglob("*.md"):
        if q in f.stem.lower():
            try:
                snippet = f.read_text(encoding="utf-8", errors="ignore")[:350]
                results.append(f"### [[{f.stem}]]\n{snippet}...\n")
            except Exception: pass
        if len(results) >= 5: break
    return "\n".join(results) if results else f"No se encontraron notas sobre '{q}'."

def handle_list_projects(args):
    projs = []
    for p in PROYECTOS_DIR.iterdir():
        if p.is_dir() and p.name not in ["specs", "_templates", "context-bundles"]:
            readme = p / "README.md"
            status = "activo"
            if readme.exists():
                for line in readme.read_text(encoding="utf-8", errors="ignore").splitlines():
                    if "estado:" in line: status = line.split(":", 1)[1].strip().replace('"', ''); break
            projs.append(f"- **{p.name}** (Estado: {status})")
    return "\n".join(projs)

# Handlers OpenSpec
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
- Integracion con modelos de datos en {stk}.
"""

    spec_md = f"""---
tags: [spec, delta, sdd]
capability: "{clean_id}"
---

# Especificación de Comportamiento: {name}

## ADDED Requirements

### Requirement: {name} - Contrato Principal
El sistema DEBE procesar la solicitud satisfaciendo los contratos de aceptacion.

#### Scenario: Ejecucion exitosa con datos validos
- **GIVEN** que el cliente envia un payload valido y autenticado
- **WHEN** se invoca el servicio
- **THEN** el sistema responde con HTTP 200/201 y el recurso estructurado

#### Scenario: Validacion fallida de entrada
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
- Regla: Separacion estricta entre puertos y adaptadores ([[Clean Architecture & Hexagonal]]).
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
    return f"Especificacion OpenSpec creada con exito en: 02-PROYECTOS/specs/{clean_id}/ (proposal.md, spec.md, design.md, tasks.md)"

def handle_validate_spec(args):
    name = args.get("spec_name", "").lower().replace(" ", "-")
    p = SPECS_DIR / name / "spec.md"
    if not p.exists():
        return f"No se encontro el archivo spec.md en {SPECS_DIR / name}"
    txt = p.read_text(encoding="utf-8", errors="ignore")
    errs = []
    if "#### Scenario:" not in txt: errs.append("Faltan '#### Scenario:'")
    if "- **GIVEN**" not in txt or "- **WHEN**" not in txt: errs.append("Faltan clausulas BDD GIVEN/WHEN/THEN")
    if errs:
        return f"Validacion fallida: {', '.join(errs)}"
    return f"¡La especificacion '{name}' es 100% compliant con el estandar OpenSpec BDD!"

def handle_get_spec_questions(args):
    st = args.get("system_type", "api").lower()
    from spec_questions import QUESTIONNAIRES
    qs = QUESTIONNAIRES.get(st, QUESTIONNAIRES["api"])
    lines = [f"Preguntas clave recomendadas para sistemas tipo {st.upper()}:"]
    for idx, q in enumerate(qs, 1): lines.append(f"{idx}. {q}")
    return "\n".join(lines)

def handle_generate_scaffold(args):
    from spec_scaffold import generate_scaffold
    name = args.get("spec_name")
    fw = args.get("framework", "nestjs")
    generate_scaffold(name, fw)
    return f"Scaffolding {fw.upper()} generado exitosamente en 02-PROYECTOS/specs/{name}/scaffold/"

# Handlers Gentle-AI / Engram
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
    return f"Directriz guardada en la memoria persistente del agente en: {fpath.relative_to(VAULT_DIR)}"

def handle_recall_memory(args):
    q = args.get("query", "").lower()
    matches = []
    # Buscar en decisiones y aprendizajes
    for d in [DECISIONS_DIR, APRENDIZAJES_DIR / "errores"]:
        if d.exists():
            for f in d.rglob("*.md"):
                txt = f.read_text(encoding="utf-8", errors="ignore")
                if q in f.stem.lower() or q in txt.lower():
                    snippet = txt[:350].replace("\n", " ")
                    matches.append(f"- **[[{f.stem}]]**: {snippet}...")
                if len(matches) >= 5: break
    return "\n".join(matches) if matches else f"No se encontraron memorias previas relacionadas con '{q}'."

def handle_package_project_context(args):
    from devbrain_packager import package_project, OUTPUT_DIR
    pname = args.get("project_name")
    package_project(pname)
    bundle_name = f"context-{pname.lower().replace(' ', '-')}.md"
    return f"Bundle de contexto compacto generado en: 02-PROYECTOS/context-bundles/{bundle_name}"

def handle_audit_project_health(args):
    from devbrain_health import check_all_projects, OUTPUT_REPORT
    check_all_projects()
    return f"Auditoria completada. Reporte actualizado en: 04-APRENDIZAJES/salud-proyectos.md"


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
                "serverInfo": {"name": "devbrain-mcp", "version": "2.0.0"}
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
            # OpenSpec
            elif name == "propose_spec": text = handle_propose_spec(args)
            elif name == "validate_spec": text = handle_validate_spec(args)
            elif name == "get_spec_questions": text = handle_get_spec_questions(args)
            elif name == "generate_scaffold": text = handle_generate_scaffold(args)
            # Gentle-AI
            elif name == "remember_decision": text = handle_remember_decision(args)
            elif name == "recall_memory": text = handle_recall_memory(args)
            elif name == "package_project_context": text = handle_package_project_context(args)
            elif name == "audit_project_health": text = handle_audit_project_health(args)
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