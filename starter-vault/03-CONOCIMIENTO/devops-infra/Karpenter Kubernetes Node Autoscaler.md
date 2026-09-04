---
tags: [cloud, devops, kubernetes, karpenter, finops, aws]
categoria: devops-infra
---
# Karpenter Kubernetes Node Autoscaler

## ¿Qué es?
Aprovisionador y autoscaler de nodos de próxima generación para [[Kubernetes]] de código abierto (originalmente creado por AWS).

## Ventajas sobre Cluster Autoscaler Clásico
- **Aprovisionamiento Just-in-Time sin Node Groups**: Observa directamente los Pods pendientes y aprovisiona instancias EC2 óptimas en menos de 30 segundos.
- **Consolidación Activa de Nodos**: Desaloja y empaqueta Pods automáticamente en instancias más pequeñas o apaga nodos vacíos para reducir costos de infraestructura de inmediato.
- **Gestión Inteligente de Spot Instances**: Selecciona automáticamente los pools de instancias Spot con menor riesgo de interrupción.
