---
tags: [skill, backend, api, rest]
nombre: API Design & Contratos OpenAPI
categoria: practicas-desarrollo
---

# 🌐 Buenas Prácticas de Diseño de APIs RESTful

## Directrices
1. **Sustantivos en Plural**: `/api/v1/users`, `/api/v1/orders`.
2. **Idempotencia**:
   - `GET`, `PUT`, `DELETE` deben ser idempotentes.
   - `POST` requiere clave de idempotencia (`Idempotency-Key`) en pagos o transacciones críticas.
3. **Códigos de Estado HTTP Correctos**:
   - `200 OK`, `201 Created`, `204 No Content`.
   - `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `422 Unprocessable Entity`.
   - `500 Internal Error`, `503 Service Unavailable`.
4. **Documentación Automática**: Generada out-of-the-box con [[FastAPI]] y Swagger en [[NestJS]].
