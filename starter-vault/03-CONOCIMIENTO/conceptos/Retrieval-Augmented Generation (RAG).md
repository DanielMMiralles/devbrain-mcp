---
tags: [concepto, ai, rag, embeddings]
nombre: Retrieval-Augmented Generation (RAG)
categoria: conceptos
---

# Retrieval-Augmented Generation (RAG)

## Definición
Técnica para mejorar las respuestas de los LLMs recuperando fragmentos de información relevante desde una base de conocimiento externa antes de generar la respuesta.

## Componentes Clave
- **Chunking**: División semántica de documentos.
- **Embeddings**: Representación vectorial del texto.
- **Vector Database**: Almacenamiento y búsqueda por similitud de cosenos (ej. extensión `[[pgvector]]` en [[PostgreSQL]] o [[Supabase]]).
- **Reranking**: Reordenamiento de fragmentos más relevantes antes de alimentar el prompt.
