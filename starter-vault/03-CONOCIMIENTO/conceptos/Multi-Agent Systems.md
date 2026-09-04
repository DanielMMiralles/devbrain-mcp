---
tags: [concepto, ai, agents, architecture]
nombre: Multi-Agent Systems
categoria: conceptos
---

# Multi-Agent Systems (Sistemas Multi-Agente)

## Definición
Paradigma arquitectónico donde múltiples agentes especializados colaboran para resolver problemas complejos que sobrepasan la capacidad o ventana de contexto de un único agente monolítico.

## Patrones Comunes
1. **Router / Supervisor**: Un agente central clasifica y delega tareas a sub-agentes especializados.
2. **Network / Swarm**: Agentes autónomos que se comunican entre sí mediante mensajes peer-to-peer.
3. **Sequential Pipeline**: La salida de un agente se convierte en la entrada del siguiente.
4. **Hierarchical Teams**: Estructuras jerárquicas implementables con [[LangGraph]].
