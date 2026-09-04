---
tags: [arquitectura, matriz-decision, skills, devbrain]
nombre: Matriz de Selección de Arquitectura de Software
categoria: arquitectura
---

# 🧭 Matriz de Decisión de Arquitectura de Software

Usa esta matriz para determinar el estilo arquitectónico más idóneo según los requerimientos de tu proyecto:

| Criterio / Tipo de Sistema | Arquitectura Recomendada | Stack Ideal | Justificación |
|---|---|---|---|
| **CRUD / MVP Rápido / Prototipo** | Monolito Modular Liviano | [[FastAPI]] / [[Django]] + [[PostgreSQL]] / [[Supabase]] | Máxima velocidad de iteración sin overhead de red ni complejidad distribuida. |
| **Dominio de Negocio Complejo / Reglas Densas** | Clean Architecture / Hexagonal + [[Domain-Driven Design (DDD)]] | [[NestJS]] / [[FastAPI]] + [[PostgreSQL]] | Aísla los agregados y lógica pura del negocio de frameworks y bases de datos. |
| **Sistemas Multi-Agente / Flujos Cognitivos** | Arquitectura de Grafos de Estado & Event-Driven | [[LangGraph]] + [[FastAPI]] + [[Redis]] / Postgres | Flujos cíclicos, checkpoints inmutables, memoria persistente e intervención humana (human-in-the-loop). |
| **Alta Concurrencia / Tiempo Real / Eventos** | Event-Driven Architecture (EDA) + CQRS | [[FastAPI]] (Async) + [[Redis]] / Kafka + [[PostgreSQL]] | Desacoplamiento de productores y consumidores, escalado independiente de lecturas y escrituras. |
| **Escala Empresarial / Múltiples Equipos** | Microservicios Orientados a Bounded Contexts | [[NestJS]] / [[FastAPI]] + [[Docker]] + [[Kubernetes]] | Fronteras delimitadas de dominio con despliegues y pipelines de CI/CD independientes. |

## Árbol de Decisión Rápido
```
¿El negocio tiene reglas intrincadas y múltiples estados?
 ├── SÍ ──► Aplica DDD + Clean Architecture
 └── NO
      ¿El sistema requiere agentes autónomos con memoria y ciclos?
       ├── SÍ ──► Aplica [[LangGraph]] State Graph
       └── NO
            ¿El volumen de lectura supera por 10x al de escritura?
             ├── SÍ ──► Aplica CQRS + Caching
             └── NO ──► Monolito Modular pragmático
```
