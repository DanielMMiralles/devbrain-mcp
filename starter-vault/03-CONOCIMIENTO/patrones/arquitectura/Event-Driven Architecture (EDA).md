---
tags: [patron, arquitectura, eda, microservicios]
nombre: Event-Driven Architecture (EDA)
categoria: arquitectura
---

# ⚡ Event-Driven Architecture (EDA)

## ¿Qué es?
Patrón de arquitectura distribuida donde los componentes del sistema se comunican emitiendo y reaccionando a eventos de dominio de forma asíncrona y desacoplada.

## Componentes
- **Productores de Eventos**: Servicios que detectan un cambio de estado y publican un evento (ej. servicio en [[NestJS]] publica `OrderCreated`).
- **Canal de Eventos / Broker**: Middleware de mensajería ([[Redis]] Pub/Sub, RabbitMQ, Apache Kafka).
- **Consumidores de Eventos**: Servicios o agentes ([[LangGraph]]) que reaccionan ejecutando lógica secundaria sin bloquear al productor.

## Ventajas & Desafíos
- **Ventajas**: Escalabilidad horizontal independiente, tolerancia a fallos, acoplamiento mínimo.
- **Desafíos**: Consistencia eventual, trazabilidad distribuida y orden de eventos.
