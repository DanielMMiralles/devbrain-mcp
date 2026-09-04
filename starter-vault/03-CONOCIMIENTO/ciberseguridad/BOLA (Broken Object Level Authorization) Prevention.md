---
tags: [seguridad, appsec, authorization, best-practices]
categoria: ciberseguridad
---
# BOLA (Broken Object Level Authorization) Prevention

## ¿Cómo Prevenirlo en [[NestJS]] y [[FastAPI]]?
- **Nunca confiar solo en el ID de la URL**:
  - En [[FastAPI]]: Extraer el `current_user` desde la dependencia JWT y validar `WHERE user_id = current_user.id AND id = resource_id`.
  - En [[NestJS]]: Implementar un Guard personalizado a nivel de método o validar la pertenencia en el Service mediante políticas de dominio.
- **Uso de UUIDs v7 o Identificadores Opacos**:
  - Evitar enteros autoincrementales (`/users/123`) para impedir la enumeración secuencial de recursos por atacantes.
- **Row-Level Security (RLS)**:
  - Habilitar RLS en [[PostgreSQL]] o [[Supabase]] para que la propia base de datos impida lecturas no autorizadas a nivel de fila.
