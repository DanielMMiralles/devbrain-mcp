---
tags: [concepto, ai, llm, optimization]
nombre: Prompt Caching & Context Windows
categoria: conceptos
---

# Prompt Caching & Context Windows

## Definición
Mecanismo que permite a los proveedores de modelos almacenar en memoria (caché) los prefijos de prompts largos y recurrentes (documentación de proyectos, bases de código, system prompts), reduciendo drásticamente la latencia y los costos por token hasta en un 90%.

## Buenas Prácticas
- Mantener los bloques estáticos (instrucciones del sistema, schemas de herramientas [[Model Context Protocol (MCP)]]) al inicio del prompt y el contexto dinámico al final.
