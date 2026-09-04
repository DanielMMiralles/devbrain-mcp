---
tags: [database, postgresql, storage]
---
# [[PostgreSQL]] MVCC & VACUUM
Control de concurrencia multiversión (*Multi-Version Concurrency Control*) de [[PostgreSQL]]. Permite que los lectores no bloqueen a los escritores y viceversa. Requiere el proceso `VACUUM` para reclamar espacio de tuplas muertas (*dead tuples*).
