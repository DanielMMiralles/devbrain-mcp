---
tags: [devops, kubernetes, networking, gateway-api]
categoria: devops-infra
---
# Kubernetes Gateway API Standard

## ¿Qué es?
La evolución oficial del recurso Ingress en [[Kubernetes]], diseñada como una colección de recursos declarativos desacoplados orientados a roles:
- `GatewayClass`: Administrado por el proveedor de infraestructura o equipo de plataforma.
- `Gateway`: Administrado por el operador del cluster para definir puntos de entrada (IPs, puertos, TLS).
- `HTTPRoute`, `GRPCRoute`, `TCPRoute`: Administrados por los desarrolladores de aplicaciones.

## Capacidades Avanzadas
- División de tráfico porcentual nativa para Canary deployments sin herramientas externas.
- Coincidencia de encabezados y redirección avanzada compatible con microservicios en [[NestJS]] y [[FastAPI]].
