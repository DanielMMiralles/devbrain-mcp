---
tags: [skill, ddd, arquitectura, herramientas, frameworks]
categoria: practicas-desarrollo
---
# 🛠️ Herramientas y Frameworks para Domain-Driven Design (DDD)

## 1. Event Storming & Modelado Visual
- **Miro / FigJam ([[Figma]])**: Plataforma colaborativa para talleres de *Event Storming* (Orange: Domain Events, Blue: Commands, Yellow: Aggregates, Pink: Policies).
- **Context Mapper**: Herramienta DSL (Domain-Specific Language) open source para generar mapas de contexto de DDD, diagramas UML y contratos arquitectónicos directamente desde código.

## 2. Bibliotecas de Dominio Táctico por Lenguaje
### En TypeScript / [[NestJS]]:
- **`@nestjs/cqrs`**: Módulo oficial de NestJS para CommandBus, QueryBus y EventBus con agregados de DDD.
- **`oxide.ts` o `neverthrow`**: Tipos `Result<T, E>` y `Option<T>` para modelar fallos de dominio sin lanzar excepciones descontroladas.
- **`ts-domain` / Clases Base de DDD**:
  - `Entity<T>` con `equals(other)` basado exclusivamente en `id`.
  - `ValueObject<T>` inmutable con validación en constructor.
  - `AggregateRoot<T>` con método `addDomainEvent(event)` para publicación atómica.

### En Python / [[FastAPI]]:
- **Pydantic v2**: Validación de esquemas inmutables (`frozen=True`) para **Value Objects**.
- **Eventsourcing in Python**: Framework maduro para persistencia de eventos y agregados con soporte para [[PostgreSQL]].
- **FastAPI + Clean Architecture**: Inyección de dependencias (`Depends`) vinculada a Interfaces abstractas (`typing.Protocol` o `abc.ABC`).

## 3. Persistencia y Mapeo Desacoplado
- **Patrón Data Mapper vs Active Record**:
  - En DDD estricto, el modelo de dominio no conoce la base de datos.
  - Se utiliza **Prisma** o **SQLAlchemy 2.0 (Imperative Mapping)** para convertir entidades de dominio puras a tablas relacionales de [[PostgreSQL]] sin contaminar la lógica de negocio.
