---
tags: [devops, kubernetes, autoscaling, serverless, keda]
categoria: devops-infra
---
# KEDA (Kubernetes Event-Driven Autoscaling)

## ¿Qué es?
Operador de [[Kubernetes]] que permite escalar cargas de trabajo (Pods) de 0 a N instancias en función del volumen de eventos en sistemas externos (colas de RabbitMQ, Kafka, topics de Redis, AWS SQS o Postgres).

## Integración con tu Stack
- Escala automáticamente workers de procesamiento OCR en [[Mayan-EDMS]] cuando la cola de RabbitMQ acumula documentos pendientes.
- Escala a cero instancias cuando no hay actividad, optimizando costos de infraestructura en la nube.
