---
tags: [seguridad, devops, secrets, vault, hashicorp]
categoria: ciberseguridad
---
# HashiCorp Vault & Dynamic Secrets

## ¿Qué son los Dynamic Secrets?
Credenciales de bases de datos o servicios en la nube que se generan bajo demanda sobre la marcha y se destruyen automáticamente tras expirar su tiempo de vida (TTL).

## Flujo con [[PostgreSQL]] y [[FastAPI]]
1. El backend solicita acceso temporal a la base de datos a HashiCorp Vault.
2. Vault crea un usuario efímero en PostgreSQL (`v-token-app-xyz`) con permisos estrictos de lectura y TTL de 1 hora.
3. La aplicación usa la credencial; al expirar el tiempo, Vault revoca el usuario en la base de datos automáticamente.
- **Beneficio**: Las fugas de credenciales en logs o memoria quedan neutralizadas tras pocos minutos.
