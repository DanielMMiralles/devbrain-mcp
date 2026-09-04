---
tags: [concepto, backend, realtime, streaming]
nombre: WebSockets vs Server-Sent Events (SSE)
categoria: backend
---

# 📡 WebSockets vs Server-Sent Events (SSE)

## Comparativa Técnica
| Característica | WebSockets | Server-Sent Events (SSE) |
|---|---|---|
| **Dirección** | Bidireccional full-duplex (cliente <-> servidor) | Unidireccional (servidor -> cliente) |
| **Protocolo** | Protocolo propio `ws://` o `wss://` (upgrade HTTP) | HTTP estándar (`text/event-stream`) |
| **Reconexión** | Manual en el cliente | Automática nativa en el navegador |
| **Complejidad con Proxies/Load Balancers** | Mayor (requiere soporte de websocket sticky sessions) | Mínima (tráfico HTTP estándar compatible con [[Docker]] / K8s) |
| **Caso Ideal** | Chat bidireccional, juegos, edición colaborativa | **Streaming de tokens de LLMs**, notificaciones, logs en vivo |
