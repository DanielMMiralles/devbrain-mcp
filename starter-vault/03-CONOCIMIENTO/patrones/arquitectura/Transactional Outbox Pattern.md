---
tags: [patron, arquitectura, consistencia, microservicios]
nombre: Transactional Outbox Pattern
categoria: arquitectura
---

# 📦 Transactional Outbox Pattern

## El Problema
En arquitecturas de microservicios, modificar la base de datos y publicar un evento en el broker ([[Redis]]/Kafka) en dos operaciones separadas puede causar inconsistencias si una de las dos falla (Dual-Write Problem).

## La Solución
1. El servicio guarda la entidad y el evento correspondiente en una tabla `outbox` dentro de la **misma transacción atómica** de [[PostgreSQL]].
2. Un proceso relay asíncrono (Message Relay / Debezium / Poller) lee la tabla `outbox` y publica los eventos al broker garantizando entrega *at-least-once*.
