---
title: Neuroplasticidad en DevBrain (Grafo Sináptico Adaptativo)
category: automation-agents
tags: [ai, agents, neuroplasticity, hebb, ltp, ltd, devbrain, plc, gentle-pi, gentle-shell, architecture]
status: canonical
created: 2026-09-23
version: 3.0.0
---

# Neuroplasticidad en DevBrain (Grafo Sináptico Adaptativo)

> **"El cerebro humano no almacena información de forma estática en casilleros rígidos: reconecta dinámicamente sus sinapsis según los patrones de co-activación y la relevancia del contexto. DevBrain v3.0 adopta este principio biológico como un PLC neuroplástico."**

---

## 1. El Doble Paradigma: DevBrain PLC + Neuroplasticidad

En arquitecturas tradicionales de asistentes con memoria, el servidor procesa todas las tareas de manera uniforme y mantiene relaciones fijas entre documentos. DevBrain v3.0 desacopla estas responsabilidades:

```
[ Petición MCP ]
       │
       ▼
┌───────────────────────────────────────────────┐
│              DevBrain PLC Router              │
│       (Clasificación y Enrutamiento < 5ms)    │
└──────┬────────────────────────────────┬───────┘
       │                                │
       ▼ Fast Path (<5ms)               ▼ Heavy / Orchestration
┌──────────────────────────────┐ ┌──────────────────────────────┐
│  Corteza Cerebral (Local)    │ │   Gentle-PI / Gentle-Shell   │
│  - Búsqueda FTS5 Instantánea │ │   - Orquestación Subagentes  │
│  - Memoria Persistente       │ │   - Ciclo ODD Implementación │
│  - Grafo Sináptico Dinámico  │ │   - TDD Observado & Verify   │
│  - Clasificación ODD         │ │   - Review Mode Fail-Safe    │
└──────────────────────────────┘ └──────────────────────────────┘
               ▲                                │
               │     Feedback de Co-Activación  │
               └────────────────────────────────┘
```

1. **DevBrain como PLC (Controlador Lógico Programable)**:
   - Actúa como un switch de ultra-baja latencia.
   - Resuelve operaciones de lectura (`search_knowledge`, `recall_memory`, `classify_odd_task`) localmente in-process.
   - Redirige tareas de orquestación, verificación y trabajo sustancial a **Gentle-PI / Gentle-Shell**.

2. **Corteza Neuroplástica**:
   - Las conexiones entre notas técnicas, decisiones y requerimientos no son estáticas.
   - Se crean y fortalecen sinapsis bidireccionales cada vez que dos conceptos se co-activan en una misma sesión.

---

## 2. Fundamentos Neurocientíficos Implementados

| Principio Biológico | Mecanismo en DevBrain | Fórmula / Implementación |
|---|---|---|
| **Regla de Hebb** | *"Neurons that fire together wire together"*: nodos consultados en la misma sesión forman sinapsis. | `record_activation(node, context, session_id)` crea enlaces automáticos entre todos los nodos de la sesión. |
| **LTP (Long-Term Potentiation)** | Cada co-activación incrementa el peso sináptico con saturación asintótica. | $w_{new} = w_{old} + \delta \cdot \left(1 - \frac{w_{old}}{W_{max}}\right)$ con $W_{max} = 100.0$. |
| **LTD (Long-Term Depression)** | Las conexiones en desuso pierden fuerza gradualmente en el tiempo. | $w_{decayed} = w \cdot 2^{-\Delta t / t_{1/2}}$ con $t_{1/2} = 30\text{ días}$. |
| **Poda Sináptica** | Eliminación de conexiones residuales para evitar saturación de memoria. | Se podan sinapsis con $w < 0.05$ durante cada ciclo de resincronización. |
| **Mielinización** | Creación de "hot paths" (axones rápidos) para las rutas cognitivas más transitadas. | Nodos con mayor peso sináptico se priorizan y pre-cargan en el reranker. |

---

## 3. Reranking Compuesto Determinista con Synaptic Bonus

El motor FTS5 de DevBrain evalúa la relevancia de cada nota combinando señales léxicas, temporales y sinápticas:

$$\text{Score}_{compuesto} = \underbrace{\text{BM25}(q)}_{\text{relevancia texto}} + \underbrace{\text{Pinned Bonus}}_{\text{+15.0 reglas}} + \underbrace{\text{Recency Bonus}}_{\text{0.0 a 5.0 decaimiento}} + \underbrace{\text{Exact Title}}_{\text{+10.0 título exacto}} + \underbrace{\text{Synaptic Bonus}}_{\text{NUEVO v3.0}}$$

### Cálculo del Synaptic Bonus:
$$\text{Synaptic Bonus} = \sum_{n \in \text{session\_nodes}} w(n, \text{candidato}) \cdot \alpha$$

Donde:
- $\text{session\_nodes}$ son los conceptos activados durante la sesión activa.
- $w(n, \text{candidato})$ es el peso de la sinapsis entre el nodo previo y el resultado candidato.
- $\alpha = 0.5$ es el factor de escala.

**Efecto Práctico**: Si un agente está trabajando en [[Organic Driven Development (ODD)]], la búsqueda de "arquitectura" priorizará automáticamente [[Clean Architecture & Puertos y Adaptadores]] sobre notas arquitectónicas genéricas, porque la sinapsis `odd ↔ clean-architecture` ha sido reforzada en sesiones previas.

---

## 4. Clasificación de Herramientas en el PLC Router

El controlador `PLCRouter` clasifica las 21 herramientas MCP en tres vías:

1. **`LOCAL_FAST` (Vía Rápida Local, < 5ms)**:
   - `search_knowledge`, `recall_memory`, `remember_decision`
   - `classify_odd_task`, `list_projects`, `get_project_context`
   - `route_model_dispatch`, `get_spec_questions`

2. **`DELEGATABLE` (Delegación a Gentle-PI cuando está disponible)**:
   - `prepare_odd_task`, `reconcile_odd_resume`
   - `sync_project_graph`, `query_code_graph`
   - `package_project_context`, `audit_project_health`
   - `generate_scaffold`, `propose_spec`, `validate_spec`
   - `debate_project_feasibility`, `audit_ponytail_complexity`

3. **`REQUIRES_ORCHESTRATOR` (Orquestación Exclusiva de Gentle-Shell)**:
   - `orchestrator_session_bridge`
   - `prepare_sdd_preflight`

Si Gentle-PI o Gentle-Shell no están activos en el entorno, el PLC Router conmuta automáticamente a **modo fallback in-process**, garantizando 100% de disponibilidad sin interrupciones.

---

## 5. Conexiones Neuronales en el Grafo DevBrain
- [[Organic Driven Development (ODD)]] — Protocolo adaptativo que alimenta los contextos de sesión.
- [[Gentle-Shell (Workspace & Multi-Orchestrator)]] — Entorno de ejecución que asume la orquestación delegada por el PLC.
- [[Engram (Gentle-AI Persistent Memory)]] — Memoria a largo plazo complementaria al grafo sináptico.
- [[Clean Architecture & Puertos y Adaptadores]] — Invariantes de diseño protegidas por el fast-path local.
