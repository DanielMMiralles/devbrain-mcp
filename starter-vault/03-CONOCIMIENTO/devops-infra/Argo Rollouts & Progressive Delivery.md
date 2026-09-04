---
tags: [devops, gitops, continuous-delivery, canary]
categoria: devops-infra
---
# Argo Rollouts & Progressive Delivery

## ¿Qué es?
Controlador de despliegue avanzado para [[Kubernetes]] que sustituye al objeto `Deployment` tradicional, permitiendo estrategias de despliegue progresivo automatizado:

## Modos de Despliegue
1. **Canary Deployment con Métricas Automáticas**: Envía un 5% del tráfico a la nueva versión, consulta métricas de latencia y tasa de errores en Prometheus; si los umbrales se cumplen, incrementa gradualmente el tráfico a 20%, 50% y 100%.
2. **Blue-Green Deployment**: Despliegue paralelo con validación previa y conmutación instantánea de tráfico en el balanceador.
