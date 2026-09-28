---
title: "Decisión: Actualización Suite Gentle — Gentle-AI v3.7.0 y Gentle-Shell Independiente"
date: 2026-09-28
status: accepted
tags: [decision, architecture, gentle-ai, gentle-shell, devbrain, odd, tokens, plc]
---

# Decisión: Actualización Suite Gentle — Gentle-AI v3.7.0 y Gentle-Shell Independiente

## Contexto
El ecosistema Gentle lanzó una actualización mayor compuesta por:
1. **`gentle-ai` v3.7.0**: Capacidad de asignación granular de modelos por revisor (Claude Code: modelos por revisor; OpenCode: implementer vs explorer; Codex: agentes ODD y revisores con presets GPT-6) con fallback tolerante a fallos si un modelo no está disponible.
2. **`gentle-shell` (independiente)**: CLI propio (`npm i -g gentle-pi`) con directorio aislado (`~/.gentle-shell/agent`), compatibilidad de enlace (`--link`), auto-reconfiguración y restauración del in-Pi review.
3. **Mejoras v3.6.x**: Compatibilidad fluida en Windows/PowerShell y eliminación automática de paquetes de preguntas obsoletos durante `gentle-ai sync`.

DevBrain v3.0 actúa como PLC y puente de orquestación, por lo que requería actualizar su compatibilidad de detección y telemetría hacia esta nueva release.

## Decisiones Tomadas

1. **Instalación y Verificación del Ecosistema en Windows**:
   - Binario `gentle-ai` compilado y actualizado a `v3.7.0` mediante Go 1.27 (`github.com/gentleman-programming/gentle-ai/v3/cmd/gentle-ai@latest`).
   - Binario `gentle-shell` instalado globalmente mediante npm (`gentle-pi@3.7.0`).
   - Aprovisionamiento exitoso del entorno aislado `~/.gentle-shell/agent` ejecutando `gentle-shell setup`.
   - Ejecución de `gentle-ai sync` para armonizar configuraciones de agentes y skills.

2. **Adaptación del PLC Router de DevBrain (`src/plc_router.py`)**:
   - `GentlePIBridge.is_available()` y `probe_gentle_pi()` actualizados para detectar `gentle-shell` en PATH, su carpeta dedicada `~/.gentle-shell/agent`, y el `package.json` global de npm en `%APPDATA%\npm\node_modules\gentle-pi`.
   - `GentlePIBridge.get_version()` resuelve de forma prioritaria la versión 3.7.0.

3. **Actualización de la Telemetría y CLI (`src/cli_hud.py`, `src/cli_help.py`)**:
   - HUD Cognitive Workspace actualizado a `Gentle-AI v3.7.0` y `gentle-shell v3.7.0 (independiente)`.
   - Comando `devbrain help gentle` añadido para explicar per-reviewer model selection, uso de `gentle-shell --link`, y la arquitectura de tolerancia a fallos.
   - Skills `devbrain-core` y `devbrain-odd` actualizados con los nuevos lineamientos.
