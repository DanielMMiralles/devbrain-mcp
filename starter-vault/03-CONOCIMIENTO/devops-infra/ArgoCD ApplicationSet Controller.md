---
tags: [devops, gitops, argocd, automation]
categoria: devops-infra
---
# ArgoCD ApplicationSet Controller

## ¿Qué es?
Controlador de [[GitOps & ArgoCD]] que automatiza la generación y gestión de múltiples aplicaciones de ArgoCD a través de múltiples clusters, repositorios Git o carpetas de monorepos.

## Generadores Clave
- **Git Generator**: Detecta automáticamente nuevos microservicios agregados al repositorio y crea su despliegue en K8s.
- **Cluster Generator**: Despliega automáticamente aplicaciones de infraestructura en todos los clusters registrados.
