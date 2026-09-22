---
title: Gentle-Shell (Workspace & Multi-Orchestrator)
category: automation-agents
tags: [ai, agents, gentle-shell, gentle-pi, pi, orchestration, multi-agent, v3.4.0]
status: canonical
created: 2026-09-16
updated: 2026-09-22
version: 3.4.0
---

# Gentle-Shell (Workspace & Multi-Orchestrator)

> **"Gentle-Pi ahora se llama GENTLE SHELL. El agente del ecosistema crece de nombre porque creció de alcance: ya no es un paquete que ajusta Pi, es tu workspace completo de desarrollo con agentes."** — *Alan Buscaglia & Deco (Gentle-AI & Gentle-Shell releases)*

---

## 1. Evolución e Identidad de Gentle-Shell

**Gentle-Shell** (`Gentleman-Programming/gentle-shell`, publicado como `gentle-pi@3.4.0`) consolida el entorno integral para agentes y desarrollo orgánico:
- **Comando CLI Dedicado (`gentle-shell`)**: A partir de v3.4.0, Gentle-Shell cuenta con su propio ejecutable de terminal independiente. No depende de invocaciones genéricas sobre `pi` y ejecuta bajo un modo de configuración aislado y seguro.
- **Flujo ODD por Defecto**: Preparado de fábrica para ejecutar [[Organic Driven Development (ODD)]] de forma natural.
- **Optimización de Monorepos Grandes**: La vista *Changes* está acotada estrictamente a los archivos modificados por la sesión actual y sus subagentes delegados, eliminando escaneos masivos en repositorios pesados.
- **Perfiles de Modelos en Sidebar**: Selección ágil y anclaje (pinning) de modelos por repositorio para optimizar coste y latencia según la naturaleza del proyecto.

---

## 2. Sistema Nativo de Preguntas Interactivas (Dock UI)

Gentle-Shell v3.4.0 introduce un sistema interactivo de preguntas de primera clase integrado en el dock:

| Característica | Detalle Arquitectónico |
|---|---|
| **Capacidad** | Hasta 4 preguntas interactivas simultáneas para resolver incertidumbres sin fricción. |
| **Modalidades** | Selección simple (*single-select*) o selección múltiple (*multi-select*). |
| **Enriquecimiento** | Cada opción incluye título, previsualizaciones detalladas y descripciones contextuales. |
| **Navegación** | 100% operable por teclado con selector interactivo y fallback transparente a texto libre. |
| **No Intrusivo** | Mantiene el flujo de atención sin bloquear la visibilidad del código ni saturar el contexto. |

> [!WARNING]
> **Compatibilidad y Limpieza de Extensiones**:
> Si se utilizaba el paquete de terceros `rpiv-ask-user-question`, debe removerse de inmediato para evitar colisiones de eventos con el dock nativo de Gentle-Shell.

---

## 3. Subagentes en Background y Control de Rendimiento

Gentle-Shell incorpora paneles y menús dedicados para monitoreo y ajuste fino:
1. **"Modo Papa" (Optimización de Recursos)**:
   - Diseñado para laptops o máquinas con recursos limitados.
   - Permite pausar o simplificar animaciones pesadas y reducir la carga de renderizado en terminal/GUI sin degradar la capacidad cognitiva de los modelos.
2. **Medidores de Consumo de Suscripción**:
   - Monitoreo en tiempo real del uso de cuotas, tokens y balance por proveedor.
3. **Monitoreo de Subagentes Concurrentes**:
   - Vista clara del estado de subagentes en background (Idle, Running, Finished).

---

## 4. Comunicación Inter-Orquestador y Sesiones Nativas

Capacidades de mensajería entre múltiples sesiones y orquestadores concurrentes:
- `orchestrator_session_id`: Expone el identificador local único de la sesión activa.
- `orchestrator_list`: Anuncia los IDs de sesiones pares locales disponibles en el entorno.
- `orchestrator_send_message`: Notifica a un par específico con acuse de recibo.

### Semántica de Entrega y Acuse de Recibo (ACK):
- **Transporte Notification-and-ACK**: Un ACK exitoso certifica únicamente que el orquestador destino aceptó el mensaje en su cola de entrada.
- **Invariante Crítica**: Un ACK **NO** garantiza que el mensaje haya sido leído ni que la tarea encomendada haya concluido.
- **Límites Arquitectónicos**: No hay colas offline persistentes ni broadcast generalizado. La persistencia profunda se delega a [[Engram (Gentle-AI Persistent Memory)]].

---

## 5. Topología de Subagentes Especializados

1. **Explore / Map (`gentle-ai-explore`)**: Mapeo estático y lectura rápida sin permisos de escritura.
2. **Worker (`gentle-ai-worker`)**: Implementador acotado que lee `odd/tasks/<feature>.md` antes de editar código.
3. **Verify (`gentle-ai-verify`)**: Verificador independiente con ejecución de tests reales.

---

## 6. Conexiones Neuronales en el Grafo DevBrain
- [[Organic Driven Development (ODD)]] — Flujo central de trabajo orquestado por Gentle-Shell (Paso 3 resuelto vía Dock Questions).
- [[Engram (Gentle-AI Persistent Memory)]] — Memoria a largo plazo compartida entre sesiones y orquestadores.
- [[Spec-Driven Development (SDD)]] — Soporte opcional para especificaciones formales aligeradas.
- [[Token Saving & Sub-Agent Orchestration]] — Reducción de sobrecarga contextual y modo liviano.
