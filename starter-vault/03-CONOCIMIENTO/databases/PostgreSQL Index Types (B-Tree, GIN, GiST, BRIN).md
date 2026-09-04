---
tags: [database, postgresql, indexing]
---
# [[PostgreSQL]] Index Types (B-Tree, GIN, GiST, BRIN)
Estructuras de datos de indexación en [[PostgreSQL]]:
- **B-Tree**: Índice predeterminado para comparaciones de igualdad y rango (`<`, `<=`, `=`, `>=`).
- **GIN (Generalized Inverted Index)**: Diseñado para tipos compuestos, JSONB y arrays.
- **GiST (Generalized Search Tree)**: Ideal para datos geométricos, geoespaciales y búsqueda de texto.
- **BRIN (Block Range Index)**: Índices ultra-compactos para tablas masivas ordenadas cronológicamente.
