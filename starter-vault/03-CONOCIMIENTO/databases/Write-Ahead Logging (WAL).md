---
tags: [database, postgresql, durability]
---
# Write-Ahead Logging (WAL)
Técnica de [[PostgreSQL]] para asegurar durabilidad y recuperación ante fallos registrando todas las modificaciones en disco secuencial antes de escribirlas en las páginas de datos. Habilita replicación y Point-In-Time Recovery (PITR).
