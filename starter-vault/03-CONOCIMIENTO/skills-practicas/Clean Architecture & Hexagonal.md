---
tags: [skill, backend, arquitectura, clean-code]
nombre: Clean Architecture & Puertos y Adaptadores
categoria: arquitectura
---

# 🏛️ Clean Architecture & Patrón Hexagonal

## Objetivo
Aislar las reglas de negocio centrales de frameworks externos, bases de datos o interfaces de usuario.

## Capas
1. **Dominio (Entities / Use Cases)**: Lógica pura e independiente de frameworks (ej. clases TypeScript o modelos Python).
2. **Puertos (Interfaces)**: Contratos abstractos de entrada y salida (ej. `UserRepositoryInterface`).
3. **Adaptadores (Adapters)**: Implementaciones concretas (ej. controlador [[NestJS]], endpoint [[FastAPI]], repositorio [[PostgreSQL]] con Prisma o SQLAlchemy).

## Beneficio en Sistemas con Agentes
- Facilita a los LLMs generar tests unitarios con mocks sin necesidad de levantar bases de datos reales.
