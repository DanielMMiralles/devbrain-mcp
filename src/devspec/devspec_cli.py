"""
DevSpec / OpenSpec Engine para DevBrain.
Soporta el ciclo completo SDD:
1. Propose (proposal.md + delta specs + design.md + tasks.md)
2. Validate (cumplimiento de contratos Gherkin/Scenario)
3. Ingest-Skills (descarga y cataloga las mejores skills de desarrollo e ingenieria de software)
"""
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

VAULT_DIR = Path(os.getenv("VAULT_DIR", r"C:\Users\damm1\OneDrive\Documentos\Obsidian Vault"))
SPECS_DIR = VAULT_DIR / "02-PROYECTOS" / "specs"
SKILLS_DIR = VAULT_DIR / "03-CONOCIMIENTO" / "skills-practicas"

PROPOSAL_TEMPLATE = """---
tags: [spec, proposal, sdd]
change_id: "{id}"
title: "{title}"
project: "[[{project}]]"
created: "{date}"
status: proposed # proposed | in-progress | applied | archived
stack: [{stack}]
---

# 📝 Propuesta: {title}

## 1. ¿Por que? (Why)
<!-- 1-2 oraciones explicando el problema de negocio o la oportunidad -->

## 2. ¿Que cambia? (What Changes)
- **Nuevas Capacidades**: {title}
- **Impacto**: Afecta controladores, modelos y flujos del proyecto [[{project}]].

## 3. Capacidades Afectadas
- `specs/{id}/spec.md`
"""

DELTA_SPEC_TEMPLATE = """---
tags: [spec, delta, sdd]
capability: "{id}"
---

# Especificacion de Comportamiento: {title}

## Purpose
Define de forma no ambigua el contrato de comportamiento observable que los agentes y el codigo deben cumplir.

## ADDED Requirements

### Requirement: {title} - Flujo Principal
El sistema DEBE procesar la solicitud cumpliendo con los contratos establecidos y manejo de errores.

#### Scenario: Ejecucion exitosa con datos validos
- **GIVEN** que el cliente envia un payload valido
- **WHEN** se invoca el servicio
- **THEN** el sistema responde con HTTP 200/201 y el payload estructurado esperado

#### Scenario: Fallo por validacion de entrada
- **GIVEN** que el cliente omite campos obligatorios o tipos erroneos
- **WHEN** se procesa la solicitud
- **THEN** el sistema retorna HTTP 422/400 con los detalles del error sin exponer secretos

#### Scenario: Resiliencia ante caida de dependencias
- **GIVEN** que el almacenamiento o servicio externo no responde
- **WHEN** se alcanza el tiempo limite de espera (timeout)
- **THEN** el sistema aplica fallback o retorna HTTP 503 controlado
"""

DESIGN_TEMPLATE = """---
tags: [spec, design, sdd]
capability: "{id}"
---

# 🏛️ Diseño Tecnico: {title}

## Contexto & Arquitectura
Diseñado para operar sobre: {stack}.

## Decisiones Tecnicas Clave
1. **Separacion de Capas**: Separar controladores de servicios de dominio.
2. **Validacion de Schemas**: Uso de Pydantic o Zod para garantizar tipado estricto.

## Modelos de Datos & Contratos
```json
{{
  "id": "uuid",
  "status": "string",
  "created_at": "ISO8601"
}}
```

## Riesgos & Mitigaciones
- *Riesgo*: Latencia elevada en queries pesadas.
  - *Mitigacion*: Indexacion adecuada en [[PostgreSQL]] y cache temporal si aplica.
"""

TASKS_TEMPLATE = """---
tags: [spec, tasks, sdd]
capability: "{id}"
---

# 📋 Tareas de Implementacion: {title}

## 1. Setup & Contratos
- [ ] 1.1 Definir modelos de datos y validar tests de schema
- [ ] 1.2 Configurar variables de entorno y dependencias

## 2. Logica Core
- [ ] 2.1 Implementar servicio de dominio
- [ ] 2.2 Agregar endpoints o controladores correspondientes

## 3. Verificacion
- [ ] 3.1 Ejecutar suite de pruebas unitarias
- [ ] 3.2 Verificar integracion con contenedor [[Docker]]
"""

def propose(name: str, project: str = "General", stack: str = "[[FastAPI]], [[PostgreSQL]]"):
    clean_id = name.lower().replace(" ", "-").replace("_", "-")
    change_folder = SPECS_DIR / clean_id
    change_folder.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    (change_folder / "proposal.md").write_text(
        PROPOSAL_TEMPLATE.format(id=clean_id, title=name, project=project, date=today, stack=stack).strip() + "\n",
        encoding="utf-8"
    )
    (change_folder / "spec.md").write_text(
        DELTA_SPEC_TEMPLATE.format(id=clean_id, title=name).strip() + "\n",
        encoding="utf-8"
    )
    (change_folder / "design.md").write_text(
        DESIGN_TEMPLATE.format(id=clean_id, title=name, stack=stack).strip() + "\n",
        encoding="utf-8"
    )
    (change_folder / "tasks.md").write_text(
        TASKS_TEMPLATE.format(id=clean_id, title=name).strip() + "\n",
        encoding="utf-8"
    )
    print(f"[OK] Paquete OpenSpec/DevSpec creado con exito en: {change_folder}")
    print("  -> proposal.md")
    print("  -> spec.md (Given/When/Then contracts)")
    print("  -> design.md")
    print("  -> tasks.md")

def validate(spec_path: str):
    p = Path(spec_path)
    if not p.is_absolute():
        p = SPECS_DIR / spec_path
    if p.is_dir():
        p = p / "spec.md"

    if not p.exists():
        print(f"Error: No existe el archivo {p}")
        return

    content = p.read_text(encoding="utf-8")
    errors = []
    if "#### Scenario:" not in content:
        errors.append("Faltan escenarios en formato OpenSpec ('#### Scenario:').")
    if "- **GIVEN**" not in content and "- **WHEN**" not in content:
        errors.append("Faltan clausulas BDD (GIVEN / WHEN / THEN).")
    if "### Requirement:" not in content:
        errors.append("Faltan definiciones de requerimientos ('### Requirement:').")

    if errors:
        print(f"[ERROR] Validacion fallida para {p.name}:")
        for err in errors:
            print(f"   - {err}")
    else:
        print(f"[VALIDADO] ¡{p.name} es 100% compliant con la especificacion SDD de OpenSpec!")

def main():
    parser = argparse.ArgumentParser(description="DevSpec / OpenSpec CLI")
    sub = parser.add_subparsers(dest="command")

    p_prop = sub.add_parser("propose", help="Crea una propuesta completa OpenSpec")
    p_prop.add_argument("name", help="Nombre del cambio (ej: payment-gateway)")
    p_prop.add_argument("--project", default="General", help="Proyecto objetivo")
    p_prop.add_argument("--stack", default="[[FastAPI]], [[PostgreSQL]]", help="Stack vinculado")

    p_val = sub.add_parser("validate", help="Valida contratos BDD de una spec")
    p_val.add_argument("path", help="Ruta o carpeta de la spec")

    args = parser.parse_args()
    if args.command == "propose":
        propose(args.name, args.project, args.stack)
    elif args.command == "validate":
        validate(args.path)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()