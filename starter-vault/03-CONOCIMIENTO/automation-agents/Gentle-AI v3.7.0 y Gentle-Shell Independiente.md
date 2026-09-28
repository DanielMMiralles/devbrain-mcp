---
title: Gentle-AI v3.7.0 y Gentle-Shell Independiente
category: automation-agents
tags: [ai, agents, gentle-ai, gentle-shell, gentle-pi, review, rdd, odd, token-optimization, v3.7.0]
status: canonical
created: 2026-09-28
updated: 2026-09-28
version: 3.7.0
---

# 🎩 Gentle-AI v3.7.0 y Gentle-Shell Independiente

> **"Ahora elegís qué modelo usa cada revisor. Decidís vos dónde gastar: un modelo potente para el revisor que busca riesgos, uno más barato para el que mira legibilidad. Y si el modelo guardado no está disponible, cae a uno soportado en vez de romperse."** — *Gentle AI Release Notes v3.7.0*

---

## 1. La Gran Novedad: Selección de Modelos por Revisor (*Per-Reviewer Model Selection*)

En las versiones anteriores, los agentes de revisión (RDD) ejecutaban bajo un único modelo monolítico global. En **Gentle-AI v3.7.0**, la asignación de modelos pasa a ser granular y desacoplada según el perfil del host:

| Entorno / Host | Capacidad de Asignación de Modelos | Beneficio Arquitectónico |
|---|---|---|
| **Claude Code** | Asignación independiente a cada uno de los **6 revisores** (*Risk, Resilience, Readability, Security, Performance, Architecture*). | Modelo de frontera (ej: Opus / Sonnet) para riesgos críticos; modelo ultrarrápido y económico (ej: Haiku) para legibilidad o sintaxis. |
| **OpenCode** | Edición de modelos diferenciados para los agentes **implementadores** (*implementer*) y **exploradores** (*explorer*). | Maximiza throughput de exploración de codebase con modelos rápidos y concentra el razonamiento profundo en la implementación. |
| **Codex** | Configuración de modelos para los agentes de **ODD** y de **revisores**, con presets incluidos para **GPT-6**. | Preparación futura para arquitecturas cognitivas avanzadas y control fino de cuota por agente. |

### Tolerancia a Fallos y Degradación Elegante (*Graceful Fallback*)
- Si un modelo especificado en la configuración no está disponible (por indisponibilidad de API, cuotas agotadas o falta de credenciales), el arnés **no interrumpe el ciclo ni genera un error fatal**.
- Realiza una **degradación automática a un modelo soportado** en el entorno local, emitiendo una notificación transparente al desarrollador.

---

## 2. Gentle-Shell como CLI Independiente y Aislado

A partir de `gentle-pi@3.7.0`, el comando **`gentle-shell`** se independiza como runtime de primera clase (`npm i -g gentle-pi`):

### 1. Directorio Aislado Dedicado (`~/.gentle-shell/agent`)
- Al ejecutarse sin modificadores, `gentle-shell` corre en su propia carpeta aislada.
- **No altera** la instalación vanilla de `pi` ni muta sus configuraciones (`~/.pi/agent/settings.json`).

### 2. Enlace con Pi Existente (`--link`)
Si el usuario desea compartir sus credenciales, modelos locales configurados y el historial previo de sesiones de `pi`:
```powershell
gentle-shell --link
```
Este modo lee las sesiones y credenciales de `~/.pi/agent` sin sobreescribir ni romper extensiones nativas de Pi.

### 3. Aprovisionamiento Automático (*Zero Config*)
- En su primer arranque, detecta dependencias faltantes (`engram`, `pi-mcp-adapter`, `pi-web-access`) y las aprovisiona de forma desatendida.
- Configura por defecto el tema visual **`Gentleman-Cute`**.
- Ante actualizaciones de versión, se reconfigura y compila automáticamente sin requerir intervención manual.

### 4. Restauración de In-Pi Review
- Se restaura el soporte para realizar revisiones utilizando modelos agregados mediante extensiones de Pi.

---

## 3. Correcciones de Estabilidad (v3.6.x a v3.7.0)

1. **Soporte Nativo de Windows & PowerShell**:
   - El hook de Claude Code ejecuta limpiamente en terminales PowerShell de Windows sin problemas de escape de rutas ni variables de entorno.
2. **Sincronización Inteligente (`gentle-ai sync`)**:
   - Remueve automáticamente extensiones de preguntas de terceros (ej: `rpiv-ask-user-question`) que colisionaban con el sistema de **Dock Questions nativo** de Gentle-Shell.
3. **Optimización con DevBrain PLC Router**:
   - DevBrain v3.0 detecta automáticamente tanto `gentle-shell` en PATH como los entornos aislados o enlazados, despachando peticiones de orquestación y ODD de forma transparente.
