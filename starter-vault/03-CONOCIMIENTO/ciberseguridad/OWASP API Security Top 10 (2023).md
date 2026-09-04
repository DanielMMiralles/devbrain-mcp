---
tags: [seguridad, ciberseguridad, owasp, appsec, api]
categoria: ciberseguridad
---
# OWASP API Security Top 10 (2023)

## Los 10 Riesgos Críticos en APIs Modernas
1. **API1:2023 - Broken Object Level Authorization (BOLA)**: El fallo #1. Ocurre cuando un endpoint permite acceder a un recurso pasando un ID ajeno (`/api/orders/{id}`) sin verificar que el usuario autenticado sea el dueño.
2. **API2:2023 - Broken Authentication**: Fallos en la validación de tokens JWT, rotación de claves o endpoints de login sin rate limiting.
3. **API3:2023 - Broken Object Property Level Authorization (BOPLA)**: Exposición excesiva de datos (*Mass Assignment*) permitiendo modificar campos internos como `is_admin: true`.
4. **API4:2023 - Unrestricted Resource Consumption**: Falta de límites en tamaño de payload, concurrencia o complejidad de queries. Mitigado con [[Rate Limiting Algorithms]].
5. **API5:2023 - Broken Function Level Authorization (BFLA)**: Usuarios normales invocando endpoints administrativos (`/api/admin/users`).
6. **API6:2023 - Unrestricted Access to Sensitive Business Flows**: Abuso de flujos legítimos (compra masiva de entradas, scraping agresivo con bots).
7. **API7:2023 - Server-Side Request Forgery (SSRF)**: La API descarga URLs provistas por el usuario pudiendo acceder a metadatos internos de la nube (`169.254.169.254`).
8. **API8:2023 - Security Misconfiguration**: Errores en CORS (`Access-Control-Allow-Origin: *`), cabeceras de depuración activas en producción o servicios sin parchear.
9. **API9:2023 - Improper Inventory Management**: APIs en desuso (*Shadow APIs / Zombie APIs*) que exponen datos sin monitoreo.
10. **API10:2023 - Unsafe Consumption of Third-Party APIs**: Confiar ciegamente en datos recibidos de integraciones externas sin validación de schema.
