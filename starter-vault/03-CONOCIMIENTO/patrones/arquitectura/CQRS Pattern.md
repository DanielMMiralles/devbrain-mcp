---
tags: [patron, arquitectura, cqrs, data]
nombre: Command Query Responsibility Segregation (CQRS)
categoria: arquitectura
---

# 🔀 Command Query Responsibility Segregation (CQRS)

## ¿Qué es?
Patrón que segrega estrictamente las operaciones de modificación del estado (**Commands**) de las operaciones de lectura (**Queries**), utilizando modelos de datos y esquemas independientes para cada una.

## Arquitectura
- **Command Model**: Valida reglas de negocio complejas usando [[Domain-Driven Design (DDD)]] y escribe en la base de datos transaccional principal ([[PostgreSQL]]).
- **Query Model**: Proyecciones desnormalizadas optimizadas para lectura rápida (ej. vistas materializadas, caché en [[Redis]], o búsqueda elástica).

## Cuándo usar CQRS
- Sistemas donde la carga de lectura supera por órdenes de magnitud a las escrituras.
- Interfaces de usuario con vistas complejas que combinan datos de múltiples entidades agregadas.
