---
tags: [herramienta, devops, gitops, argocd, continuous-delivery]
nombre: GitOps & ArgoCD
categoria: devops-infra
---

# 🐙 GitOps & ArgoCD

## ¿Qué es GitOps?
Paradigma operativo donde el estado deseado de toda la infraestructura y aplicaciones en [[Kubernetes]] se declara y versiona en repositorios de [[Git & GitHub]], convirtiendo a Git en la **única fuente de verdad**.

## Principios Fundamentales
1. **Declarativo**: El sistema se describe completamente en manifiestos o [[Helm Charts & K8s Packaging]].
2. **Versionado & Inmutable**: Cada cambio se audita vía Pull Requests y commits en Git.
3. **Pillado Automático (Pull-based)**: Un agente interno ([[ArgoCD]]) monitorea el repo y sincroniza el cluster activamente, eliminando la necesidad de dar acceso al cluster a pipelines externos de CI/CD.
4. **Auto-healing**: Si alguien modifica manualmente un recurso en el cluster (drift), ArgoCD detecta la desviación y restaura el estado declarado en Git.
