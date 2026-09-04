---
tags: [devops, kubernetes, multi-tenancy, platform-engineering]
categoria: devops-infra
---
# vCluster & Multi-Tenancy Virtualization

## ¿Qué es?
Tecnología que permite crear clusters virtuales de [[Kubernetes]] totalmente funcionales y aislados que se ejecutan dentro de un namespace de un cluster físico subyacente.

## Casos de Uso
- Entornos efímeros de prueba para Pull Requests en pipelines de [[CI-CD Pipelines]] sin el costo de aprovisionar clusters dedicados.
- Aislamiento completo de controladores y CRDs entre diferentes equipos de desarrollo.
