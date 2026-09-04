---
tags: [devops, kubernetes, reliability, high-availability]
categoria: devops-infra
---
# Kubernetes Pod Disruption Budgets (PDB)

## ¿Qué es?
Regla de gobernanza en [[Kubernetes]] que limita la cantidad de Pods de una aplicación que pueden estar caídos simultáneamente durante interrupciones voluntarias (ej. actualizaciones de nodos del cluster, drenado con `kubectl drain`).

## Configuración Recomendada
- `minAvailable: 2` o `maxUnavailable: 1` para servicios transaccionales como APIs de [[Chambita-Ecosystem]] y [[AliaLog-System]], garantizando cero tiempo de inactividad durante mantenimientos de infraestructura.
