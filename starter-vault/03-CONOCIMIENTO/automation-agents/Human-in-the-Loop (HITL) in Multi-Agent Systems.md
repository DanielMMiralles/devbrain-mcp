---
tags: [ai, agents, safety, governance]
---
# Human-in-the-Loop (HITL) in [[Multi-Agent Systems]]
Patrón de diseño donde el grafo de ejecución de [[LangGraph]] se pausa antes de ejecutar herramientas de alto riesgo (escritura en DB, pagos, despliegues a [[Kubernetes]]), requiriendo aprobación explícita del desarrollador.
