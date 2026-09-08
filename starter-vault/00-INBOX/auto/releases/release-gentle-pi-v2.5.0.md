---
tags: [inbox, release, gentle-pi]
herramienta: "[[gentle-pi]]"
version: "v2.5.0"
fecha: 2026-09-08
---

# 🚀 Nueva Versión: gentle-pi v2.5.0

## Enlace Oficial
- [Ver Release en GitHub](https://github.com/Gentleman-Programming/gentle-pi/releases/tag/v2.5.0)

## Resumen de Cambios Clave
- **Transporte**: Incluye el binario gentle-ai **v2.7.0** y el bundle de contratos **1.2.0**.
- **Gentle Shell**: Statusline compacta unificada, context gauge (alerta 80%/95%), prompt animado con petal spinner y diff overlay (`/gentle:changes` / `alt+g`).
- **Gentle Agents (Nativo)**: Sub-agentes nativos en Pi sin depender de plugins de terceros. Monitoreo en streaming cards y panel `/gentle:agents` (`alt+a`).
- **Gentle Todo**: Sustituye `rpiv-todo` con tarjetas integradas y plegables.
- **Delegación RDD-Aware**: Optimización de costos: verificación delegada solo cuando el riesgo lo amerita.
- **Consentimiento por Sesión**: Aprobación única con `/gentle:review`.
- **Mejoras Windows**: Arreglos en CodeGraph shim sin subshell y manejo de rutas PATH.

## Tareas Relacionadas
- [x] Evaluar si introduce breaking changes para mis proyectos activos (Requiere desinstalar `pi-subagents-j0k3r` y `rpiv-todo` al migrar a componentes nativos).
- [x] Actualizar nota de conocimiento en [[Gentle-Pi (Senior Architect Harness para Pi)]].
