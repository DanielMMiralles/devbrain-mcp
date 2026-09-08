---
tags: [inbox, release, gentle-ai]
herramienta: "[[gentle-ai]]"
version: "v2.7.0"
fecha: 2026-09-08
---

# 🚀 Nueva Versión: gentle-ai v2.7.0

## Enlace Oficial
- [Ver Release en GitHub](https://github.com/Gentleman-Programming/gentle-ai/releases/tag/v2.7.0)

## Resumen de Cambios Clave
- **Evaluación Dinámica de Riesgo (`gentle-ai review assess --json`)**: Clasificación previa (`passive`, `medium`, `high`) para ahorrar verificadores innecesarios en cambios triviales.
- **Composición Nativa SDD (`gentle-ai sdd-archive-compose`)**: Automatiza el archivado de especificaciones en `openspec/specs/`.
- **Ciclo de Revisión Resiliente**: Eliminación de bloqueos ante roles faltantes, manejo de renames y tipado de estados de indeterminación.
- **Telemetría Transparente & Anónima**: Proceso en background de 3s sin PII, deshabilitable con `gentle-ai telemetry disable`.
- **Contratos & Compatibilidad**: Cero breaking changes; contratos congelados bajo bundle 1.2.0.

## Tareas Relacionadas
- [x] Evaluar si introduce breaking changes para mis proyectos activos (Evaluado: 100% compatible hacia atrás).
- [x] Actualizar nota de conocimiento en [[Gentle-AI & Sub-Agent Orchestration (Token Saving)]].
