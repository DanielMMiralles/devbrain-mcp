---
tags: [patron, arquitectura, resiliencia, devops]
nombre: Circuit Breaker & Retry Patterns
categoria: arquitectura
---

# 🔌 Circuit Breaker & Retry Patterns

## Circuit Breaker (Disyuntor)
Previene que una aplicación intente ejecutar repetidamente una operación condenada a fallar, protegiendo tanto al cliente como al servicio destino de una saturación en cascada.
- **Closed (Cerrado)**: Las peticiones fluyen con normalidad.
- **Open (Abierto)**: Se detectan fallos continuos por encima del umbral; las llamadas fallan inmediatamente devolviendo fallback sin consumir recursos.
- **Half-Open (Semi-abierto)**: Permite una cantidad limitada de peticiones de prueba para verificar si el servicio externo se recuperó.

## Estrategia de Reintentos (Exponential Backoff + Jitter)
- Los reintentos deben espaciarse exponencialmente (`t = base * 2^intento`) con ruido aleatorio (*jitter*) para evitar el problema de manada atronadora (*thundering herd*).
