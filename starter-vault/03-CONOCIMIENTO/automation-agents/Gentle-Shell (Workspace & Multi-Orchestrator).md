---
title: Gentle-Shell (Workspace & Multi-Orchestrator)
category: automation-agents
tags: [ai, agents, gentle-shell, gentle-pi, pi, orchestration, multi-agent]
status: canonical
created: 2026-09-16
version: 3.0.0
---

# Gentle-Shell (Workspace & Multi-Orchestrator)

> **"Gentle-Pi ahora se llama GENTLE SHELL. El agente del ecosistema crece de nombre porque creció de alcance: ya no es un paquete que ajusta Pi, es tu workspace completo de desarrollo con agentes."** — *Alan Buscaglia & Deco (Gentle-AI v3.0)*

## 1. Evolución de Gentle-Pi a Gentle-Shell
**Gentle-Shell** (`Gentleman-Programming/gentle-shell`) consolida la maduración del arnés para **Pi**:
- **Identidad de Workspace Completo**: Integra layout de terminal, panel lateral (sidebar) interactivo, visor de cambios y trazabilidad de tareas en una sola superficie de control.
- **Flujo ODD por Defecto**: Preparado de fábrica para ejecutar [[Organic Driven Development (ODD)]] sin configuración manual.
- **Optimización de Monorepos Grandes**: La vista *Changes* ahora está estrictamente acotada a los archivos modificados por la sesión actual y sus subagentes delegados, eliminando los escaneos masivos de disco que congelaban el arranque en repositorios voluminosos.
- **Perfiles de Modelos en Sidebar**: Selección rápida y anclaje (pinning) de modelos por repositorio para optimizar costes y latencia según la naturaleza de cada proyecto.

---

## 2. Comunicación Inter-Orquestador y Sesiones Nativas (Main)

En la rama `main`, Gentle-Shell introduce capacidades de mensajería entre múltiples sesiones y orquestadores concurrentes.

> [!WARNING]
> **Desinstalación de Intercom**:
> Se recomienda retirar por completo la extensión antigua `intercom` para evitar colisiones de puertos y desincronización de eventos con la nueva implementación nativa.

### Contrato de Herramientas Inter-Sesión:
- `orchestrator_session_id`: Expone el identificador local único de la sesión activa.
- `orchestrator_list`: Anuncia los IDs de sesiones pares locales disponibles en el entorno. *(Nota: el alcance de conectividad permanece desconocido hasta intentar el despacho).*
- `orchestrator_send_message`: Notifica a un par específico (si hay uno solo, lo selecciona automáticamente; si hay varios, solicita selección al usuario).

### Semántica de Entrega y Acuse de Recibo (ACK):
- **Transporte Notification-and-ACK**: Un ACK exitoso certifica únicamente que el orquestador destino aceptó el mensaje en su cola de entrada.
- **Invariante Crítica**: Un ACK **NO** garantiza que el mensaje haya sido leído ni que la tarea encomendada haya concluido.
- **Límites Arquitectónicos**:
  - No existen colas offline de reintento persistente.
  - No hay mecanismo de broadcast generalizado.
  - La sincronización profunda debe apoyarse en la memoria persistente de [[Engram (Gentle-AI Persistent Memory)]].

---

## 3. Topología de Subagentes Especializados

Gentle-Shell preserva y optimiza el despacho de subagentes delegados con contexto acotado:
1. **Explore / Map (`gentle-ai-explore`)**: Mapeo estático y lectura rápida sin permisos de escritura.
2. **Worker (`gentle-ai-worker`)**: Implementador acotado que lee `odd/tasks/<feature>.md` antes de editar código.
3. **Verify (`gentle-ai-verify`)**: Verificador independiente con ejecución de tests reales.

---

## 4. Conexiones Neuronales en el Grafo DevBrain
- [[Organic Driven Development (ODD)]] — Flujo central de trabajo orquestado por Gentle-Shell.
- [[Engram (Gentle-AI Persistent Memory)]] — Memoria a largo plazo compartida entre sesiones.
- [[Spec-Driven Development (SDD)]] — Soporte opcional para especificaciones formales.
- [[Token Saving & Sub-Agent Orchestration]] — Reducción de sobrecarga contextual.
