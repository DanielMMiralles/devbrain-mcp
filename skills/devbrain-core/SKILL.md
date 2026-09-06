---
name: devbrain-core
description: >-
  Acceso y navegacion por el ecosistema DevBrain: consulta de la base de conocimiento
  (+1,600 notas tecnicas), recuperacion de contexto de proyectos insignia,
  empaquetado ultracompacto para ahorro de tokens y ciclo SDD/OpenSpec.
---

# DevBrain Core Skill

Esta habilidad conecta a los agentes con el segundo cerebro de desarrollo (DevBrain).

## Cuándo usar esta habilidad
- Al iniciar el trabajo en cualquiera de los proyectos insignia: Chambita-Ecosystem, AliaLog-System, Narval-SGN, Alia-IMA-LangGraph, Mayan-EDMS, Odysseus, AlaOrden-Web.
- Para buscar patrones GoF, principios de diseño cloud, DDD táctico o lecciones aprendidas en `03-CONOCIMIENTO`.
- Para iniciar una nueva especificación de funcionalidad mediante OpenSpec (`propose_spec`).

## Flujo Operativo Estándar
1. **Recuperar Contexto**: Invocar `get_project_context(project_name)` para cargar el README y arquitectura del proyecto.
2. **Consultar Decisiones Previas**: Usar `recall_memory(query)` para no contradecir decisiones arquitectónicas ya acordadas.
3. **Generar Propuesta SDD**: Para nuevas funcionalidades mayores, usar `propose_spec(feature_name, project, stack)` antes de escribir código.
4. **Empaquetar Contexto**: Al depurar código complejo, usar `package_project_context(project_name)` para obtener una vista condensada sin sobrecargar tokens.
