---
tags: [devops, kubernetes, service-mesh, istio, security]
categoria: devops-infra
---
# Istio Service Mesh Architecture

## ¿Qué es?
Plataforma de malla de servicios que proporciona gestión de tráfico, seguridad y observabilidad uniforme sobre microservicios sin requerir cambios en el código fuente de las aplicaciones.

## Plano de Control & Plano de Datos
- **Istiod (Control Plane)**: Centraliza la configuración, certificados mTLS y políticas de enrutamiento.
- **Envoy Proxy (Data Plane)**: Proxy de alto rendimiento en C++ inyectado como sidecar junto a cada Pod de [[NestJS]] o [[Django]].

## Características Críticas
- Autenticación mTLS obligatoria entre todos los microservicios (Zero Trust).
- Inyección de fallos y circuit breaking a nivel de aplicación L7.
