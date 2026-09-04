---
tags: [concepto, devops, observabilidad, monitoring]
nombre: Cloud-Native Observability
categoria: devops-infra
---

# 📊 Cloud-Native Observability: Los Tres Pilares

## 1. Logs Estructurados
- Formato JSON con campos estandarizados (`timestamp`, `level`, `trace_id`, `service`, `message`).
- Centralización con herramientas como Grafana Loki, Fluentd o ElasticSearch.

## 2. Métricas
- Valores numéricos agregados a lo largo del tiempo (CPU, memoria, tasa de peticiones por segundo, latencia p95/p99).
- Instrumentación con Prometheus y visualización en dashboards de Grafana.

## 3. Distributed Tracing (Trazabilidad Distribuida)
- Seguimiento del ciclo de vida completo de una petición que atraviesa múltiples microservicios ([[FastAPI]], [[NestJS]], [[PostgreSQL]], [[Redis]]).
- Estándar abierto: **OpenTelemetry (OTel)** con visualización en Grafana Tempo o Jaeger.
