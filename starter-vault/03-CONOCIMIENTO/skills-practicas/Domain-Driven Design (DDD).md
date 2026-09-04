---
tags: [skill, ddd, arquitectura, domain-driven-design]
nombre: Domain-Driven Design (DDD)
categoria: arquitectura
---

# 🧩 Domain-Driven Design (DDD)

## ¿Qué es?
Enfoque de desarrollo de software centrado en modelar la lógica de negocio compleja a partir del dominio del problema y un lenguaje ubicuo (*Ubiquitous Language*) compartido entre expertos de negocio y desarrolladores.

## Conceptos Estratégicos
1. **Bounded Context (Contexto Delimitado)**: Frontera explícita donde un modelo de dominio y su vocabulario tienen un significado unívoco.
2. **Context Mapping**: Mapa de relaciones e integraciones entre distintos Bounded Contexts (Shared Kernel, Customer/Supplier, Anti-Corruption Layer).
3. **Core Domain vs Supporting vs Generic Subdomains**: Dónde reside la ventaja competitiva del software frente a funciones secundarias.

## Conceptos Tácticos
- **Entities**: Objetos con identidad persistente a lo largo del tiempo (ej. `User(id=1)`).
- **Value Objects**: Objetos inmutables definidos exclusivamente por sus atributos (ej. `Money(amount=100, currency="USD")`, `Address`, `Email`).
- **Aggregates & Aggregate Root**: Grupo de entidades y objetos de valor tratados como una unidad atómica para consistencia de datos. El Aggregate Root es la única puerta de acceso.
- **Domain Events**: Eventos inmutables que notifican algo que ya ocurrió en el dominio (ej. `OrderPlacedEvent`, `PaymentFailedEvent`).
- **Repositories**: Abstracción que simula una colección en memoria para recuperar y guardar agregados sin acoplarse a la base de datos.

## Cuándo usar DDD
- Dominios con reglas de negocio densas, múltiples entidades interconectadas y flujos transaccionales críticos.
- **Cuándo NO usarlo**: CRUDs simples, prototipos rápidos o microservicios anémicos que solo hacen passthrough de datos.
