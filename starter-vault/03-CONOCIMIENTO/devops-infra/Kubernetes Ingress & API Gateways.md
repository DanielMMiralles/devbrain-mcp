---
tags: [concepto, devops, kubernetes, networking, ingress]
nombre: Kubernetes Ingress & API Gateways
categoria: devops-infra
---

# 🌐 [[Kubernetes]] Ingress & API Gateways

## ¿Qué es?
Objeto de API que administra el acceso externo (HTTP/HTTPS) a los servicios dentro de un cluster de [[Kubernetes]], proporcionando enrutamiento basado en nombres de dominio o rutas, terminación SSL/TLS y balanceo de carga.

## Ingress Controllers Populares
- **Ingress NGINX**: Robusto, probado en batalla, basado en el servidor Nginx tradicional.
- **Traefik**: Nativo para microservicios y contenedores, configuración dinámica y métricas automáticas.
- **Envoy Gateway / Gateway API**: El estándar moderno de [[Kubernetes]] para orquestación de tráfico avanzada, división de tráfico porcentual (Canary deployments) y políticas de reintentos.

## Casos de Uso con tu Stack
- Enrutar el tráfico público de `api.tudominio.com` hacia microservicios en [[FastAPI]] o [[NestJS]], mientras que la UI en [[React]] se sirve estática o vía CDN.
