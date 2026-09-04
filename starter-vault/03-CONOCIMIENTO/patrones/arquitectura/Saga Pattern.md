---
tags: [patron, arquitectura, transacciones-distribuidas, microservicios]
nombre: Saga Pattern
categoria: arquitectura
---

# 🔄 Saga Pattern para Transacciones Distribuidas

## ¿Qué es?
Secuencia de transacciones locales coordinadas que actualizan el estado en múltiples servicios sin usar transacciones distribuidas bloqueantes (2PC / Two-Phase Commit).

## Tipos de Sagas
1. **Coreografía**: Cada servicio produce y escucha eventos de dominio; el siguiente servicio reacciona al evento del anterior sin un orquestador central.
2. **Orquestación**: Un servicio coordinador central (o flujo en [[LangGraph]] / [[n8n]]) le indica explícitamente a cada servicio qué transacción ejecutar.

## Transacciones Compensatorias
- Si una transacción falla a mitad de la saga, el sistema ejecuta transacciones de compensación hacia atrás para revertir los efectos colaterales ya aplicados.
