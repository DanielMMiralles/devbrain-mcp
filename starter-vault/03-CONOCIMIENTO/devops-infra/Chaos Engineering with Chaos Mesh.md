---
tags: [devops, testing, reliability, chaos-mesh]
categoria: devops-infra
---
# Chaos Engineering with Chaos Mesh

## ¿Qué es Chaos Mesh?
Plataforma nativa de [[Kubernetes]] para orquestar experimentos de caos automatizados directamente en clusters de desarrollo y staging mediante Custom Resource Definitions (CRDs).

## Tipos de Fallos Inyectables
- **Pod Chaos**: Matar Pods aleatoriamente o simular fallos de inicialización.
- **Network Chaos**: Inyectar latencia artificial, pérdida de paquetes o particiones de red entre microservicios ([[NestJS]] y [[PostgreSQL]]).
- **Stress Chaos**: Saturar núcleos de CPU o agotar memoria RAM para evaluar el comportamiento del kernel ante OOM (Out Of Memory).
