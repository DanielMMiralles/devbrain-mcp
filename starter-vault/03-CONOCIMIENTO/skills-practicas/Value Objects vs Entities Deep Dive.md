---
tags: [skill, ddd, clean-code, arquitectura]
categoria: practicas-desarrollo
---
# 💎 Value Objects vs Entities: Modelado Riguroso

## Comparativa Técnica
| Característica | Entity | Value Object |
|---|---|---|
| **Identidad** | Sí (`id`, UUIDv7). Dos entidades son iguales solo si su ID coincide. | No. Se definen 100% por sus valores internos. |
| **Mutabilidad** | Mutable a través de métodos de negocio explícitos. | **Estrictamente Inmutable**. Cualquier cambio genera una nueva instancia. |
| **Ciclo de Vida** | Persiste a lo largo del tiempo y cambia de estado. | Efímero o embebido dentro de una Entidad o Agregado. |
| **Ejemplos Reales** | `Usuario`, `Buque`, `Factura`, `Envío`. | `Dinero(100, USD)`, `Email`, `CoordenadaGPS`, `RangoFechas`. |

## Implementación en [[mis-convenciones]]
- Prohibido pasar primitivos crudos (`string`, `number`) a los servicios de dominio (*Primitive Obsession*).
- Todo dato con reglas de validación (como un email o un precio) debe encapsularse en un **Value Object** que valide sus invariantes en el momento de instanciarse.
