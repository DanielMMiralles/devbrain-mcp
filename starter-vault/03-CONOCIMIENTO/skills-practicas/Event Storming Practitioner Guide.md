---
tags: [skill, ddd, modelado, event-storming, arquitectura]
categoria: practicas-desarrollo
---
# 🌪️ Event Storming: Guía Práctica de Modelado

## ¿Qué es?
Taller rápido de descubrimiento inventado por Alberto Brandolini para explorar dominios de negocio complejos reuniendo a desarrolladores y expertos de dominio.

## La Sintaxis Cromática
| Color Post-it | Concepto DDD | Significado / Ejemplo |
|---|---|---|
| 🟧 **Naranja** | **Domain Event** | Algo que ya ocurrió en el pasado (`PedidoCreado`, `PagoProcesado`). |
| 🟦 **Azul** | **Command** | La intención del usuario o sistema (`CrearPedido`, `ProcesarPago`). |
| 🟨 **Amarillo** | **Aggregate** | El cluster de entidades que garantiza invariantes de negocio (`Pedido`). |
| 🟪 **Lila / Rosa** | **Policy / Reactive Logic** | *"Cada vez que ocurra X, entonces ejecutar Y"* (reglas de negocio). |
| 🟩 **Verde** | **Read Model / Projection** | Información que el usuario necesita ver antes de tomar una decisión. |

## Cuándo usarlo en Proyectos
- Antes de redactar cualquier especificación en [[Spec-Driven Development (SDD)]].
- Para identificar las fronteras exactas de un **Bounded Context** en [[Chambita-Ecosystem]] o [[AliaLog-System]].
